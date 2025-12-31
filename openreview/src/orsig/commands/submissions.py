"""
Submissions command for downloading submission information.
"""

import json
from argparse import ArgumentParser, Namespace

from ..command import Command
from ..utils import get_client
from ..rdf import format_rdf_prefixes, Rdf


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

    def execute(self, args: Namespace) -> None:
        """
        Download all information about current submissions.
        """
        import sys

        # Fetch submissions
        submission_invitation = f"{args.venue_id}/-/Submission"
        print(
            f"Fetching all submissions from {args.venue_id} "
            f"using invitation {submission_invitation}...",
            file=sys.stderr,
        )
        client = get_client(args.api_url, args.username, args.password)
        submissions = client.get_all_notes(invitation=submission_invitation)

        print(f"Submissions found: {len(submissions)}", file=sys.stderr)

        # Generate output based on format
        if args.as_rdf:
            # Generate RDF output
            rdf = Rdf()

            # Build RDF content
            rdf_lines = []

            # Add prefixes
            rdf_lines.append(format_rdf_prefixes(rdf.get_prefixes()))
            rdf_lines.append('')  # Empty line after prefixes

            # Add triples for each submission
            for note in submissions:
                submission_iri = rdf.submissionIri(note.id)
                # Add rdf:type triple
                rdf_lines.append(f"{submission_iri} a :Submission .")
                # Add title triple
                title_object = rdf.literalFromJson(note.content, 'title.value')
                rdf_lines.append(f"{submission_iri} :title {title_object} .")
                # Add author triples
                author_ids = rdf.valuesFromJson(note.content, 'authorids.value')
                for author_id in author_ids:
                    if author_id:  # Skip empty author IDs
                        person_iri = rdf.personIri(author_id)
                        rdf_lines.append(f"{submission_iri} :author {person_iri} .")
                # Add author-reviewer triple
                author_reviewer = rdf.iriFromJson(note.content, 'serve_as_reviewer.value', 'person')
                rdf_lines.append(f"{submission_iri} :author_reviewer {author_reviewer} .")

            output_content = '\n'.join(rdf_lines)
        else:
            # Generate JSON output
            submissions_data = [note.to_json() for note in submissions]
            output_content = json.dumps(submissions_data, indent=2)

        # Output to file or stdout
        if args.output:
            with open(args.output, "w") as f:
                f.write(output_content)
            format_type = "RDF" if args.as_rdf else "JSON"
            print(f"Submissions saved to {args.output} in {format_type} format", file=sys.stderr)
        else:
            print(output_content)

        # Print summary
        if args.verbose:
            for i, note in enumerate(submissions, 1):
                print(f"\n{i}. {note.content.get('title', 'No title')}", file=sys.stderr)
                print(f"   ID: {note.id}", file=sys.stderr)
                print(f"   Authors: {note.content.get('authors', 'N/A')}", file=sys.stderr)
