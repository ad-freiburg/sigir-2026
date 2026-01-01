"""
Submissions command for downloading submission information.
"""

import json

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
            "--as-rdf",
            action="store_true",
            help="Output submissions as RDF triples instead of JSON",
        )
        parser.add_argument(
            "--with-profiles",
            action="store_true",
            help="Include full profile information for all authors",
        )

    def execute(self, args: Namespace) -> None:
        """
        Download all information about current submissions.
        """
        # Get submissions.
        submission_invitation = f"{args.venue_id}/-/Submission"
        log.info(
            f"Fetching all submissions from {args.venue_id} "
            f"using invitation {submission_invitation}..."
        )
        submissions = get_client().get_all_notes(invitation=submission_invitation)

        log.info(f"Submissions found: {len(submissions)}")

        # Get the set of distinct author IDs.
        all_author_ids = set()
        for note in submissions:
            author_ids = note.content.get("authorids", {}).get("value", [])
            for author_id in author_ids:
                all_author_ids.add(author_id)

        # Get profile for each distinct author.
        author_profiles = {}
        profile_with_papers = ProfileWithPapers()
        if args.with_profiles:
            log.info(
                f"Fetching profiles for {len(all_author_ids)} distinct authors ..."
            )
            for author_id in all_author_ids:
                try:
                    profile_with_papers.get_profile(author_id)
                    author_profiles[author_id] = profile_with_papers.asJson()
                except Exception as e:
                    log.error(f"Failed to get profile for {author_id}: {e}")
                    author_profiles[author_id] = {"id": author_id, "error": str(e)}

        if args.as_rdf:
            # Add RDF triples for each submission.
            rdf = Rdf()
            for note in submissions:
                submission_iri = rdf.submissionIri(note.id)
                rdf.add_triple(submission_iri, "a", ":Submission")
                rdf.add_triple(
                    submission_iri,
                    ":title",
                    rdf.literalFromJson(note.content, "title.value"),
                )
                author_ids = rdf.valuesFromJson(note.content, "authorids.value")
                for author_id in author_ids:
                    rdf.add_triple(submission_iri, ":author", rdf.personIri(author_id))
                rdf.add_triple(
                    submission_iri,
                    ":author_reviewer",
                    rdf.iriFromJson(note.content, "serve_as_reviewer.value", "person"),
                )

            # Add RDF triple for each author profile.
            if args.with_profiles:
                for author_id, profile_data in author_profiles.items():
                    profile_with_papers.addToRdf(rdf, profile_data, author_id)
            else:
                # No profiles requested, just add :dblp_id :novalue for each author
                for author_id in all_author_ids:
                    rdf.add_triple(rdf.personIri(author_id), ":dblp_id", ":novalue")

            output_content = rdf.as_turtle()
        else:
            # Generate JSON output
            submissions_data = []
            for note in submissions:
                submission_json = note.to_json()

                # Add author profiles if --with-profiles is specified
                if args.with_profiles:
                    author_ids = note.content.get("authorids", {}).get("value", [])
                    authors_with_profiles = []
                    for author_id in author_ids:
                        if author_id and author_id in author_profiles:
                            authors_with_profiles.append(author_profiles[author_id])
                        else:
                            authors_with_profiles.append({"id": author_id})
                    submission_json["authors_profiles"] = authors_with_profiles

                submissions_data.append(submission_json)

            output_content = json.dumps(submissions_data, indent=2)

        # Output to file or stdout
        if args.output:
            with open(args.output, "w") as f:
                f.write(output_content)
            format_type = "RDF" if args.as_rdf else "JSON"
            log.info(f"Submissions saved to {args.output} in {format_type} format")
        else:
            print(output_content)

        # Print summary
        if args.verbose:
            for i, note in enumerate(submissions, 1):
                log.info(f"\n{i}. {note.content.get('title', 'No title')}")
                log.info(f"   ID: {note.id}")
                log.info(f"   Authors: {note.content.get('authors', 'N/A')}")
