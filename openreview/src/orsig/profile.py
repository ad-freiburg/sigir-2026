"""
ProfileWithPapers class for handling OpenReview profile data with imported papers.
"""

import json
from pathlib import Path
from typing import Dict, Any

from .log import log
from .rdf import Rdf
from .client import get_client


class ProfileWithPapers:
    """
    Class for managing OpenReview profile data with imported DBLP papers.
    """

    def __init__(
        self,
        cache_profiles: bool = True,
        cache_dir: str = "orsig-cache",
        recache: bool = False,
    ):
        """
        Initialize ProfileWithPapers with caching options.
        The cache_dir is the top-level cache directory; profiles are stored in cache_dir/profiles.
        If recache is True, skip reading from cache but still write fresh data to cache.
        """
        self.profile = None
        self.papers = []
        self.cache_profiles = cache_profiles
        self.cache_dir = str(Path(cache_dir) / "profiles")
        self.recache = recache

    def get_profile(self, profile_id: str) -> None:
        """
        Get the profile as well as all imported DBLP papers for a given ID.
        """
        # Clear any cached result from previous calls
        if hasattr(self, "_cached_final_result"):
            del self._cached_final_result

        # Get the client (singleton if no args)
        client = get_client()

        # Get the profile using the OpenReview client to get canonical ID
        self.profile = client.get_profile(profile_id)

        # Get the canonical profile ID for caching
        canonical_profile_id = self.profile.id

        # Check cache using canonical ID (skip if recache is True)
        if self.cache_profiles and not self.recache:
            cached_data = self._load_from_cache(canonical_profile_id)
            if cached_data:
                log.debug(
                    f"Profile information retrieved from cache for {canonical_profile_id}"
                )
                self._restore_from_cache(cached_data)
                return

        # Fetch DBLP papers for this profile
        raw_papers = client.get_notes(
            invitation="DBLP.org/-/Record", content={"authorids": canonical_profile_id}
        )

        # Process papers
        self.papers = []
        for paper in raw_papers:
            self.papers.append(paper.to_json())

        # Save to cache if caching is enabled (use canonical profile ID to avoid duplicates)
        if self.cache_profiles:
            self._save_to_cache(canonical_profile_id)

    def _get_cache_filename(self, profile_id: str) -> str:
        """
        Get cache filename for a profile ID, removing tildes.
        """
        clean_id = profile_id.replace("~", "")
        return f"{clean_id}.json"

    def _get_cache_path(self, profile_id: str) -> Path:
        """
        Get full cache file path for a profile ID.
        """
        cache_dir = Path(self.cache_dir)
        filename = self._get_cache_filename(profile_id)
        return cache_dir / filename

    def _load_from_cache(self, profile_id: str) -> Dict[str, Any] | None:
        """
        Load profile and papers data from cache if it exists.
        """
        cache_path = self._get_cache_path(profile_id)

        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If cache file is corrupted, ignore it
                return None

        return None

    def _save_to_cache(self, profile_id: str) -> None:
        """
        Save current profile and papers data to cache.
        """
        cache_path = self._get_cache_path(profile_id)
        cache_dir = cache_path.parent

        # Create cache directory if it doesn't exist
        cache_dir.mkdir(exist_ok=True)

        # Pre-compute the final output format to avoid processing on load
        profile_json = self.profile.to_json()
        final_result = profile_json.copy()
        final_result["imported_dblp_papers"] = self.papers

        # Save to cache file using JSON
        try:
            with open(cache_path, "w") as f:
                json.dump(final_result, f, indent=2)
        except IOError:
            # If we can't write to cache, just continue without caching
            pass

    def _restore_from_cache(self, cached_data: Dict[str, Any]) -> None:
        """
        Restore profile and papers from cached data.
        """
        # Store the pre-computed final result
        self._cached_final_result = cached_data

    def asJson(self) -> Dict[str, Any]:
        """
        Return profile and papers information as a dictionary.
        """
        # Check if we have cached final result
        if hasattr(self, "_cached_final_result"):
            return self._cached_final_result

        # Build result from live data
        if not self.profile:
            raise ValueError("Profile not loaded. Call get_profile() first.")

        result = self.profile.to_json()
        result["imported_dblp_papers"] = self.papers
        return result

    def addToRdf(
        self, rdf: Rdf, profile_data: Dict[str, Any], person_id: str = ""
    ) -> str:
        """
        Add profile triples to an existing Rdf instance.
        If profile_data has an error, just adds :dblp_id :novalue.
        If person_id is provided, use that for the IRI; otherwise use profile_data's id.
        Returns the person IRI for additional triples.
        """
        effective_id = person_id if person_id else profile_data.get("id", "")
        if not effective_id:
            return ""

        person_iri = rdf.personIri(effective_id)

        # If there was an error fetching the profile, just add :dblp_id :novalue
        if profile_data.get("error"):
            rdf.add_triple(person_iri, ":dblp_id", ":novalue")
            return person_iri

        # Add type declaration
        rdf.add_triple(person_iri, "a", ":Person")

        # Add properties
        rdf.add_triple(
            person_iri, ":gender", rdf.literalFromJson(profile_data, "content.gender")
        )
        dblp_id = rdf.urlFromJson(profile_data, "content.dblp")
        if dblp_id.endswith(".html>"):
            dblp_id = dblp_id[:-6] + ">"  # Remove .html but keep >
        rdf.add_triple(person_iri, ":dblp_id", dblp_id)
        rdf.add_triple(
            person_iri, ":orcid", rdf.urlFromJson(profile_data, "content.orcid")
        )
        rdf.add_triple(
            person_iri,
            ":email",
            rdf.literalFromJson(profile_data, "content.preferredEmail"),
        )

        # Get fullname from the first (preferred) name
        names = profile_data.get("content", {}).get("names", [])
        if names and len(names) > 0:
            fullname = names[0].get("fullname", "")
            if fullname:
                fullname_literal = rdf.literal(fullname)
            else:
                fullname_literal = ":novalue"
        else:
            fullname_literal = ":novalue"
        rdf.add_triple(person_iri, "rdfs:label", fullname_literal)

        # Add current position and institution from history (first entry)
        history = profile_data.get("content", {}).get("history", [])
        current = history[0] if history else {}
        rdf.add_triple(
            person_iri, ":position", rdf.literalFromJson(current, "position")
        )
        rdf.add_triple(
            person_iri, ":institution", rdf.literalFromJson(current, "institution.name")
        )

        # Add imported DBLP papers
        papers = profile_data.get("imported_dblp_papers", [])
        for paper in papers:
            dblp_iri = rdf.dblpUrlFromBibtex(paper)
            if dblp_iri:
                rdf.add_triple(person_iri, ":dblp_pub", dblp_iri)

        return person_iri

    def asRdf(self) -> str:
        """
        Return profile information as RDF triples.
        """
        # Get profile data (either cached or live)
        if hasattr(self, "_cached_final_result"):
            profile_data = self._cached_final_result
        else:
            if not self.profile:
                raise ValueError("Profile not loaded. Call get_profile() first.")
            profile_data = self.profile.to_json()
            profile_data["imported_dblp_papers"] = self.papers

        # Generate RDF output
        rdf = Rdf()
        self.addToRdf(rdf, profile_data)
        return rdf.as_turtle()
