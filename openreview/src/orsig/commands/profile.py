"""
Profile command for retrieving complete profile information for a user.
"""

import json
import sys
from argparse import ArgumentParser, Namespace

from ..command import Command
from ..utils import get_client
from ..profile import ProfileWithPapers


class ProfileCommand(Command):
    """
    Get complete profile information for a given user name.
    """

    @property
    def name(self) -> str:
        return "profile"

    @property
    def help(self) -> str:
        return "Get complete profile information for a given user name"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """
        Add profile command arguments.
        """
        parser.add_argument(
            "profile_id",
            help="Username (e.g., ~John_Doe1) or email address to get profile for",
        )
        parser.add_argument(
            "--output",
            help="Output file path (default: stdout)",
        )
        parser.add_argument(
            "--as-rdf",
            action="store_true",
            help="Output profile as RDF triples instead of JSON",
        )

    def execute(self, args: Namespace) -> None:
        """
        Get complete profile information for the specified user.
        """
        # Create client factory - client only created if cache miss
        client_factory = lambda: get_client(args.api_url, args.username, args.password, args.impersonate)

        try:
            profile_with_papers = ProfileWithPapers(client_factory=client_factory)
            profile_with_papers.get_profile(args.profile_id)

            if args.as_rdf:
                result_content = profile_with_papers.asRdf()
            else:
                result_content = json.dumps(profile_with_papers.asJson(), indent=2)

            # Output to file or stdout
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(result_content)
                print(f"Profile information saved to {args.output}")
            else:
                print(result_content)

        except Exception as e:
            print(f"Error retrieving profile for '{args.profile_id}': {e}", file=sys.stderr)
            sys.exit(1)
