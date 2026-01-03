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
            help="Fetch fresh profiles from OpenReview and update the cache",
        )

    def execute(self, args: Namespace) -> None:
        """
        Download all information about current submissions.
        """
        # Get submissions.
        submission_invitation = f"{args.venue_id}/-/Submission"
        submissions = get_client().get_all_notes(invitation=submission_invitation)

        # Get the set of distinct author IDs.
        all_author_ids = set()
        for note in submissions:
            author_ids = note.content.get("authorids", {}).get("value", [])
            for author_id in author_ids:
                all_author_ids.add(author_id)

        log.info(
            f"Fetching information for {len(submissions)} submissions "
            f"with {len(all_author_ids)} distinct authors ..."
        )

        # Get profile for each distinct author.
        author_profiles = {}
        profile_with_papers = ProfileWithPapers(
            cache_dir=args.cache_dir, recache=args.recache
        )
        for author_id in all_author_ids:
            profile_with_papers.get_profile(author_id)
            author_profiles[author_id] = profile_with_papers.asJson()

        if args.dump == "rdf":
            # Add RDF triples for each submission.
            rdf = Rdf()
            for note in submissions:
                submission_iri = rdf.paperIri(note.id)
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

            # Add RDF triples for each author profile.
            for author_id in all_author_ids:
                person_iri = rdf.personIri(author_id)
                rdf.add_triple(person_iri, "a", ":Person")
                rdf.add_triple(person_iri, "a", ":Author")
                profile_with_papers.addToRdf(rdf, author_profiles[author_id], author_id)

            output_content = rdf.as_turtle()
        else:
            # Generate JSON output
            submissions_data = []
            for note in submissions:
                submission_json = note.to_json()
                author_ids = note.content.get("authorids", {}).get("value", [])
                submission_json["authors_profiles"] = [
                    author_profiles.get(aid, {"id": aid}) for aid in author_ids
                ]
                submissions_data.append(submission_json)

            output_content = json.dumps(submissions_data, indent=2)

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
            for i, note in enumerate(submissions, 1):
                log.info(f"\n{i}. {note.content.get('title', 'No title')}")
                log.info(f"   ID: {note.id}")
                log.info(f"   Authors: {note.content.get('authors', 'N/A')}")
