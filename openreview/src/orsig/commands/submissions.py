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
            "-o",
            "--output",
            help="Output file path (default: submissions.json)",
            default="submissions.json",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Print detailed information about each submission",
        )

    def execute(self, args: Namespace) -> None:
        """
        Download all information about current submissions.
        """
        # Fetch submissions
        submission_invitation = f"{args.venue_id}/-/Submission"
        print(
            f"Fetching all submissions from {args.venue_id} "
            f"using invitation  {submission_invitation} ..."
        )
        client = get_client(args.api_url, args.username, args.password)
        submissions = client.get_all_notes(invitation=submission_invitation)

        # Save to JSON file
        output_file = args.output or "submissions.json"
        print(f"Submissions found: {len(submissions)}, saving to {output_file}")
        submissions_data = [note.to_json() for note in submissions]
        with open(output_file, "w") as f:
            json.dump(submissions_data, f, indent=2)

        # Print summary
        if args.verbose:
            for i, note in enumerate(submissions, 1):
                print(f"\n{i}. {note.content.get('title', 'No title')}")
                print(f"   ID: {note.id}")
                print(f"   Authors: {note.content.get('authors', 'N/A')}")
