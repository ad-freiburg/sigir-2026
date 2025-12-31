"""
ProfileWithPapers class for handling OpenReview profile data with imported papers.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

from .log import log
from .rdf import format_rdf_prefixes, Rdf


class ProfileWithPapers:
    """
    Class for managing OpenReview profile data with imported DBLP papers.
    """

    def __init__(self, client_factory=None, cache_profiles: bool = True, cache_dir: str = "./profiles"):
        """
        Initialize ProfileWithPapers with client factory and caching options.
        """
        self.client_factory = client_factory
        self.client = None
        self.profile = None
        self.papers = []
        self.cache_profiles = cache_profiles
        self.cache_dir = cache_dir

    def get_profile(self, profile_id: str) -> None:
        """
        Get the profile as well as all imported DBLP papers for a given ID.
        """
        # Create client only when needed
        if self.client is None:
            if self.client_factory is None:
                raise ValueError("No client factory provided")
            self.client = self.client_factory()

        # Get the profile using the OpenReview client to get canonical ID
        self.profile = self.client.get_profile(profile_id)

        # Get the canonical profile ID for caching
        canonical_profile_id = self.profile.id

        # Check cache using canonical ID
        if self.cache_profiles:
            cached_data = self._load_from_cache(canonical_profile_id)
            if cached_data:
                log.debug(f"Profile information retrieved from cache for {canonical_profile_id}")
                self._restore_from_cache(cached_data)
                return

        # Fetch DBLP papers for this profile
        raw_papers = self.client.get_notes(
            invitation='DBLP.org/-/Record',
            content={'authorids': canonical_profile_id}
        )

        # Process papers and extract DBLP keys
        self.papers = []
        for paper in raw_papers:
            paper_json = paper.to_json()
            # Add external_ids if they exist as an attribute
            if hasattr(paper, 'external_ids') and paper.external_ids:
                paper_json['external_ids'] = paper.external_ids
                # Extract DBLP key from external_ids if available
                dblp_keys = [eid for eid in paper.external_ids if eid.startswith('dblp:')]
                if dblp_keys:
                    dblp_key = dblp_keys[0].replace('dblp:', '')
                    paper_json['dblp_key'] = f"https://dblp.org/rec/{dblp_key}"
            self.papers.append(paper_json)

        # Save to cache if caching is enabled (use canonical profile ID to avoid duplicates)
        if self.cache_profiles:
            self._save_to_cache(canonical_profile_id)

    def _get_cache_filename(self, profile_id: str) -> str:
        """
        Get cache filename for a profile ID, removing tildes.
        """
        clean_id = profile_id.replace('~', '')
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
                with open(cache_path, 'r') as f:
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
        final_result['imported_dblp_papers'] = self.papers

        # Save to cache file using JSON
        try:
            with open(cache_path, 'w') as f:
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
        if hasattr(self, '_cached_final_result'):
            return self._cached_final_result

        # Build result from live data
        if not self.profile:
            raise ValueError("Profile not loaded. Call get_profile() first.")

        result = self.profile.to_json()
        result['imported_dblp_papers'] = self.papers
        return result

    def asRdf(self) -> str:
        """
        Return profile information as RDF triples.
        """
        # Get profile data (either cached or live)
        if hasattr(self, '_cached_final_result'):
            profile_data = self._cached_final_result
        else:
            if not self.profile:
                raise ValueError("Profile not loaded. Call get_profile() first.")
            profile_data = self.profile.to_json()
            profile_data['imported_dblp_papers'] = self.papers

        # Generate RDF output
        rdf = Rdf()

        # Build RDF content
        rdf_lines = []

        # Add prefixes
        rdf_lines.append(format_rdf_prefixes(rdf.get_prefixes()))
        rdf_lines.append('')  # Empty line after prefixes

        # Get the profile ID
        profile_id = profile_data.get('id', '')
        if profile_id:
            person_iri = rdf.personIri(profile_id)

            # Start with the type declaration
            triple_parts = [f"{person_iri} a :Person ;"]

            # Add additional properties using semicolon notation
            gender = rdf.literalFromJson(profile_data, 'content.gender')
            triple_parts.append(f"  :gender {gender} ;")

            dblp = rdf.urlFromJson(profile_data, 'content.dblp', ':novalue')
            triple_parts.append(f"  :dblp_id {dblp} ;")

            orcid = rdf.urlFromJson(profile_data, 'content.orcid', ':novalue')
            triple_parts.append(f"  :orcid {orcid} ;")

            email = rdf.literalFromJson(profile_data, 'content.preferredEmail')
            triple_parts.append(f"  :email {email} ;")

            # Get fullname from the first (preferred) name
            names = profile_data.get('content', {}).get('names', [])
            if names and len(names) > 0:
                fullname = names[0].get('fullname', '')
                if fullname:
                    fullname_literal = rdf.literal(fullname)
                else:
                    fullname_literal = ':novalue'
            else:
                fullname_literal = ':novalue'
            triple_parts.append(f"  rdfs:label {fullname_literal} .")

            rdf_lines.append('\n'.join(triple_parts))

            # Add imported DBLP papers
            papers = profile_data.get('imported_dblp_papers', [])
            if papers:
                dblp_iris = []
                for paper in papers:
                    dblp_iri = rdf.urlFromJson(paper, 'dblp_key', '[]')
                    dblp_iris.append(dblp_iri)
                if dblp_iris:
                    publications = ', '.join(dblp_iris)
                    rdf_lines.append(f"{person_iri} :publication {publications} .")

        return '\n'.join(rdf_lines)
