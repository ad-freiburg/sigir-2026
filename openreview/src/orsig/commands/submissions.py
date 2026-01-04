"""
Submissions command for downloading submission information.
"""

import json
from pathlib import Path

from argparse import ArgumentParser, Namespace

from ..command import Command
from ..client import get_client
from ..rdf import Rdf
from ..profile import ProfileWithPapers
from ..log import log


class SubmissionsCommand(Command):
    """
    Download all information about current submissions.
    """

    @property
    def name(self) -> str:
        return "submissions"

    @property
    def help(self) -> str:
        return "Download all information about current submissions"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """
        Add submissions command arguments.
        """
        parser.add_argument(
            "--dump",
            choices=["json", "rdf"],
            required=True,
            help="Dump submissions in the specified format",
        )
        parser.add_argument(
            "--output",
            help="Output file path (default: stdout)",
            default=None,
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Print detailed information about each submission",
        )
        parser.add_argument(
            "--recache",
            action="store_true",
            help="Fetch fresh data from OpenReview and update the cache",
        )

    def _get_cache_dir(self, cache_dir: str) -> Path:
        """Get the submissions cache directory."""
        return Path(cache_dir) / "submissions"

    def _get_cache_path(self, cache_dir: str, submission_id: str) -> Path:
        """Get cache file path for a submission."""
        return self._get_cache_dir(cache_dir) / f"{submission_id}.json"

    def _load_from_cache(self, cache_dir: str, submission_id: str) -> dict | None:
        """Load submission from cache if available."""
        cache_path = self._get_cache_path(cache_dir, submission_id)
        if cache_path.exists():
            with open(cache_path) as f:
                return json.load(f)
        return None

    def _save_to_cache(self, cache_dir: str, submission_id: str, data: dict) -> None:
        """Save submission data to cache."""
        cache_path = self._get_cache_path(cache_dir, submission_id)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2)

    def _get_pdf_cache_path(self, cache_dir: str, submission_id: str) -> Path:
        """Get cache file path for a submission PDF."""
        return Path(cache_dir) / "pdfs" / f"{submission_id}.pdf"

    def _get_review_cache_path(self, cache_dir: str, submission_id: str) -> Path:
        """Get cache file path for an AI review."""
        return Path(cache_dir) / "reviews" / f"{submission_id}.json"

    def _load_review(self, cache_dir: str, submission_id: str) -> dict | None:
        """Load AI review from cache if available."""
        review_path = self._get_review_cache_path(cache_dir, submission_id)
        if review_path.exists():
            with open(review_path) as f:
                return json.load(f)
        return None

    def _download_pdf(
        self,
        client,
        cache_dir: str,
        submission_id: str,
        mdate: int | None,
        recache: bool,
    ) -> tuple[bool, str]:
        """
        Download PDF for a submission if needed.
        Returns (success, status) where status is 'downloaded', 'cached', or 'failed'.
        Re-downloads if submission mdate is newer than cached file.
        """
        pdf_path = self._get_pdf_cache_path(cache_dir, submission_id)

        if pdf_path.exists() and not recache:
            # Check if cached file is older than submission mdate
            if mdate:
                cached_mtime_ms = pdf_path.stat().st_mtime * 1000
                if cached_mtime_ms >= mdate:
                    return True, "cached"
            else:
                return True, "cached"

        try:
            pdf_bytes = client.get_attachment(id=submission_id, field_name="pdf")
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            return True, "downloaded"
        except Exception:
            return False, "failed"

    def execute(self, args: Namespace) -> None:
        """
        Download all information about current submissions.
        """
        # Get submissions from API (always fetch to get current list)
        submission_invitation = f"{args.venue_id}/-/Submission"
        api_submissions = get_client().get_all_notes(invitation=submission_invitation)

        # Process submissions with caching
        submissions_data = []
        cached_count = 0
        for note in api_submissions:
            submission_id = note.id
            cached = (
                None
                if args.recache
                else self._load_from_cache(args.cache_dir, submission_id)
            )
            if cached:
                submissions_data.append(cached)
                cached_count += 1
            else:
                submission_json = note.to_json()
                submissions_data.append(submission_json)
                self._save_to_cache(args.cache_dir, submission_id, submission_json)

        # Get the set of distinct author IDs
        all_author_ids = set()
        for submission in submissions_data:
            author_ids = (
                submission.get("content", {}).get("authorids", {}).get("value", [])
            )
            for author_id in author_ids:
                all_author_ids.add(author_id)

        if cached_count == len(submissions_data):
            cache_info = "all from cache"
        elif cached_count == 0:
            cache_info = "none from cache"
        else:
            cache_info = f"{cached_count} from cache"
        log.info(
            f"Processing {len(submissions_data)} submissions "
            f"({cache_info}) "
            f"with {len(all_author_ids)} distinct authors ..."
        )

        # Download PDFs (smart caching: only download new or updated PDFs)
        client = get_client()
        pdf_downloaded = 0
        pdf_cached = 0
        pdf_failed = 0
        for submission in submissions_data:
            submission_id = submission["id"]
            has_pdf = "pdf" in submission.get("content", {})
            if has_pdf:
                mdate = submission.get("mdate")
                success, status = self._download_pdf(
                    client, args.cache_dir, submission_id, mdate, args.recache
                )
                if status == "downloaded":
                    pdf_downloaded += 1
                elif status == "cached":
                    pdf_cached += 1
                else:
                    pdf_failed += 1
        log.info(
            f"PDFs: {pdf_downloaded} downloaded, {pdf_cached} cached, {pdf_failed} failed"
        )

        # Get profile for each distinct author.
        author_profiles = {}
        profile_with_papers = ProfileWithPapers(
            cache_dir=args.cache_dir, recache=args.recache
        )

        # Batch check which profiles have changed
        if not args.recache:
            profile_with_papers.check_profiles_for_updates(list(all_author_ids))

        for author_id in all_author_ids:
            profile_with_papers.get_profile(author_id)
            author_profiles[author_id] = profile_with_papers.asJson()

        if args.dump == "rdf":
            # Add RDF triples for each submission.
            rdf = Rdf()
            for submission in submissions_data:
                submission_iri = rdf.paperIri(submission["id"])
                content = submission.get("content", {})
                rdf.add_triple(submission_iri, "a", ":Submission")
                title_literal = rdf.literalFromJson(content, "title.value")
                rdf.add_triple(submission_iri, ":title", title_literal)
                rdf.add_triple(submission_iri, "rdfs:label", title_literal)
                rdf.add_triple(
                    submission_iri,
                    ":abstract",
                    rdf.literalFromJson(content, "abstract.value"),
                )
                author_ids = rdf.valuesFromJson(content, "authorids.value")
                for author_id in author_ids:
                    rdf.add_triple(submission_iri, ":author", rdf.personIri(author_id))
                # Add comma-separated author IDs and count
                author_ids_clean = [aid.lstrip("~") for aid in author_ids]
                rdf.add_triple(
                    submission_iri,
                    ":authors",
                    rdf.literal(", ".join(author_ids_clean))
                    if author_ids_clean
                    else ":novalue",
                )
                rdf.add_triple(
                    submission_iri,
                    ":num_authors",
                    str(len(author_ids)),
                )
                rdf.add_triple(
                    submission_iri,
                    ":author_reviewer",
                    rdf.iriFromJson(content, "serve_as_reviewer.value", "person"),
                )
                rdf.add_triple(
                    submission_iri,
                    ":created_on",
                    rdf.dateTimeFromTimestamp(submission.get("cdate")),
                )
                rdf.add_triple(
                    submission_iri,
                    ":last_modified_on",
                    rdf.dateTimeFromTimestamp(submission.get("mdate")),
                )
                has_pdf = "pdf" in content
                rdf.add_triple(
                    submission_iri,
                    ":has_pdf",
                    "true" if has_pdf else "false",
                )

                # Add AI review triples (or :novalue if no review)
                review = self._load_review(args.cache_dir, submission["id"]) or {}
                rdf.add_triple(
                    submission_iri,
                    ":ai_summary",
                    rdf.literalFromJson(review, "summary"),
                )
                rdf.add_triple(
                    submission_iri,
                    ":ai_methods",
                    rdf.literalFromJson(review, "methods"),
                )
                rdf.add_triple(
                    submission_iri,
                    ":ai_results",
                    rdf.literalFromJson(review, "results"),
                )
                strengths = review.get("strengths", [])
                rdf.add_triple(
                    submission_iri,
                    ":ai_strengths",
                    rdf.literal("\n".join(strengths)) if strengths else ":novalue",
                )
                weaknesses = review.get("weaknesses", [])
                rdf.add_triple(
                    submission_iri,
                    ":ai_weaknesses",
                    rdf.literal("\n".join(weaknesses)) if weaknesses else ":novalue",
                )

            # Add RDF triples for each author profile.
            for author_id in all_author_ids:
                person_iri = rdf.personIri(author_id)
                rdf.add_triple(person_iri, "a", ":Person")
                rdf.add_triple(person_iri, "a", ":Author")
                profile_with_papers.addToRdf(rdf, author_profiles[author_id], author_id)

            output_content = rdf.as_turtle()
        else:
            # Generate JSON output with author profiles
            output_data = []
            for submission in submissions_data:
                submission_with_profiles = submission.copy()
                author_ids = (
                    submission.get("content", {}).get("authorids", {}).get("value", [])
                )
                submission_with_profiles["authors_profiles"] = [
                    author_profiles.get(aid, {"id": aid}) for aid in author_ids
                ]
                output_data.append(submission_with_profiles)

            output_content = json.dumps(output_data, indent=2)

        # Output to file or stdout
        if args.output:
            with open(args.output, "w") as f:
                f.write(output_content)
            log.info(
                f"Submissions saved to {args.output} in {args.dump.upper()} format"
            )
        else:
            print(output_content)

        # Print summary
        if args.verbose:
            for i, submission in enumerate(submissions_data, 1):
                content = submission.get("content", {})
                title = content.get("title", {}).get("value", "No title")
                authors = content.get("authors", {}).get("value", "N/A")
                log.info(f"\n{i}. {title}")
                log.info(f"   ID: {submission.get('id')}")
                log.info(f"   Authors: {authors}")
