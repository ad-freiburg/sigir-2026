"""
Submissions command for downloading submission information.
"""

import json
from argparse import ArgumentParser, Namespace

from ..command import Command
from ..utils import get_client


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

        # Convert to JSON
        submissions_data = [note.to_json() for note in submissions]

        # Output to file or stdout
        if args.output:
            with open(args.output, "w") as f:
                json.dump(submissions_data, f, indent=2)
            print(f"Submissions saved to {args.output}", file=sys.stderr)
        else:
            print(json.dumps(submissions_data, indent=2))

        # Print summary
        if args.verbose:
            for i, note in enumerate(submissions, 1):
                print(f"\n{i}. {note.content.get('title', 'No title')}", file=sys.stderr)
                print(f"   ID: {note.id}", file=sys.stderr)
                print(f"   Authors: {note.content.get('authors', 'N/A')}", file=sys.stderr)
