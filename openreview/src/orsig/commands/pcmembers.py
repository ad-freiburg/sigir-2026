"""
Program committee members command for managing reviewers, area chairs, and senior area chairs.
"""

import json
from argparse import ArgumentParser, Namespace

from ..command import Command
from ..utils import get_client, get_random_profiles


class PcmembersCommand(Command):
    """
    Manage program committee members (reviewers, area chairs, senior area chairs) for the venue.
    """

    @property
    def name(self) -> str:
        return "pcmembers"

    @property
    def help(self) -> str:
        return "Manage program committee members for the venue"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """
        Add pcmembers command arguments.
        """
        parser.add_argument(
            "--role",
            required=True,
            choices=["reviewers", "area-chairs", "senior-area-chairs"],
            help="Role type to manage",
        )
        parser.add_argument(
            "--add",
            nargs="+",
            metavar="USER_ID",
            help="Add one or more users by ID (e.g., ~Hannah_Bast1 or email@example.com)",
        )
        parser.add_argument(
            "--remove",
            nargs="+",
            metavar="USER_ID",
            help="Remove one or more users by ID (e.g., ~Hannah_Bast1 or email@example.com)",
        )
        parser.add_argument(
            "--add-random",
            type=int,
            metavar="K",
            help="Add K random members to the specified role",
        )
        parser.add_argument(
            "--only-show",
            action="store_true",
            help="Only show what would be added without actually adding",
        )
        parser.add_argument(
            "--output",
            help="Output file path (default: stdout)",
            default=None,
        )

    def execute(self, args: Namespace) -> None:
        """
        Manage program committee members for the venue.
        """
        client = get_client(args.api_url, args.username, args.password)

        if args.add:
            self._add_specific_members(args, client)
        elif args.remove:
            self._remove_specific_members(args, client)
        elif args.add_random:
            self._add_random_members(args, client)
        else:
            self._list_members(args, client)

    def _get_group_suffix(self, role: str) -> str:
        """
        Map CLI role name to OpenReview group suffix.
        """
        role_mapping = {
            "reviewers": "Reviewers",
            "area-chairs": "Area_Chairs",
            "senior-area-chairs": "Senior_Area_Chairs",
        }
        return role_mapping[role]

    def _get_role_display_name(self, role: str) -> str:
        """
        Get human-readable display name for role.
        """
        display_names = {
            "reviewers": "reviewers",
            "area-chairs": "area chairs",
            "senior-area-chairs": "senior area chairs",
        }
        return display_names[role]

    def _get_placeholder_prefix(self, role: str) -> str:
        """
        Get placeholder prefix for random profile generation.
        """
        prefixes = {
            "reviewers": "Random Reviewer",
            "area-chairs": "Random Area Chair",
            "senior-area-chairs": "Random Senior Area Chair",
        }
        return prefixes[role]

    def _add_specific_members(self, args: Namespace, client) -> None:
        """
        Add specific members by ID to the specified role group.
        """
        user_ids = args.add
        role_display = self._get_role_display_name(args.role)
        print(f"Adding {len(user_ids)} {role_display} to {args.venue_id}...")

        # Get the group
        group_suffix = self._get_group_suffix(args.role)
        group_id = f"{args.venue_id}/{group_suffix}"

        try:
            group = client.get_group(group_id)
            print(f"Found existing group: {group_id}")
            existing_members = set(group.members or [])
        except Exception:
            print(f"Group {group_id} does not exist yet.")
            print("Creating it would require appropriate permissions.")
            existing_members = set()

        # Fetch profile information and check for duplicates
        print(f"\n{role_display.capitalize()} to add:")
        new_count = 0
        duplicate_count = 0
        names = []

        for user_id in user_ids:
            # Try to get profile information
            try:
                if user_id.startswith("~") or "@" in user_id:
                    profile = client.get_profile(user_id)
                    name = profile.get_preferred_name() if hasattr(profile, "get_preferred_name") else user_id
                else:
                    name = user_id
            except Exception:
                name = user_id

            names.append(name)

            if user_id in existing_members:
                print(f"  - {name} ({user_id}) [ALREADY A MEMBER]")
                duplicate_count += 1
            else:
                print(f"  - {name} ({user_id})")
                new_count += 1

        print(f"\nSummary:")
        print(f"  New {role_display}: {new_count}")
        print(f"  Already members: {duplicate_count}")
        print(f"  Total: {len(user_ids)}")

        if new_count > 0:
            # Prepare the updated members list
            new_members = list(existing_members.union(set(user_ids)))

            if args.only_show:
                print(f"\nTo add these {role_display}, the group would need to be updated with:")
                print(f"  Group ID: {group_id}")
                print(f"  Total members after addition: {len(new_members)}")
                print(f"\nNote: This is a preview only. Run without --only-show to actually add {role_display}.")
            else:
                # Actually add the members
                print(f"\nUpdating group...")
                try:
                    # Add only the new members (not duplicates)
                    new_member_ids = [uid for uid in user_ids if uid not in existing_members]
                    client.add_members_to_group(group_id, new_member_ids)
                    print(f"✓ Successfully added {new_count} new {role_display} to {group_id}")
                    print(f"  Total members now: {len(new_members)}")
                except Exception as e:
                    print(f"Error: Failed to update group: {e}")
        else:
            print(f"\nNo new {role_display} to add (all are already members).")

    def _remove_specific_members(self, args: Namespace, client) -> None:
        """
        Remove specific members by ID from the specified role group.
        """
        user_ids = args.remove
        role_display = self._get_role_display_name(args.role)
        print(f"Removing {len(user_ids)} {role_display} from {args.venue_id}...")

        # Get the group
        group_suffix = self._get_group_suffix(args.role)
        group_id = f"{args.venue_id}/{group_suffix}"

        try:
            group = client.get_group(group_id)
            print(f"Found existing group: {group_id}")
            existing_members = set(group.members or [])
        except Exception as e:
            print(f"Error: Could not fetch group {group_id}: {e}")
            return

        # Fetch profile information and check membership
        print(f"\n{role_display.capitalize()} to remove:")
        remove_count = 0
        not_member_count = 0
        names = []

        for user_id in user_ids:
            # Try to get profile information
            try:
                if user_id.startswith("~") or "@" in user_id:
                    profile = client.get_profile(user_id)
                    name = profile.get_preferred_name() if hasattr(profile, "get_preferred_name") else user_id
                else:
                    name = user_id
            except Exception:
                name = user_id

            names.append(name)

            if user_id in existing_members:
                print(f"  - {name} ({user_id})")
                remove_count += 1
            else:
                print(f"  - {name} ({user_id}) [NOT A MEMBER]")
                not_member_count += 1

        print(f"\nSummary:")
        print(f"  To remove: {remove_count}")
        print(f"  Not members: {not_member_count}")
        print(f"  Total: {len(user_ids)}")

        if remove_count > 0:
            # Prepare the updated members list
            remaining_members = [m for m in existing_members if m not in user_ids]

            if args.only_show:
                print(f"\nTo remove these {role_display}, the group would need to be updated with:")
                print(f"  Group ID: {group_id}")
                print(f"  Total members after removal: {len(remaining_members)}")
                print(f"\nNote: This is a preview only. Run without --only-show to actually remove {role_display}.")
            else:
                # Actually remove the members
                print(f"\nUpdating group...")
                try:
                    # Remove only the members that exist
                    members_to_remove = [uid for uid in user_ids if uid in existing_members]
                    client.remove_members_from_group(group_id, members_to_remove)
                    print(f"✓ Successfully removed {remove_count} {role_display} from {group_id}")
                    print(f"  Total members now: {len(remaining_members)}")
                except Exception as e:
                    print(f"Error: Failed to update group: {e}")
        else:
            print(f"\nNo {role_display} to remove (none are members).")

    def _add_random_members(self, args: Namespace, client) -> None:
        """
        Add random members to the specified role group.
        """
        num_members = args.add_random
        role_display = self._get_role_display_name(args.role)
        print(f"Adding {num_members} random {role_display} to {args.venue_id}...")

        # Get random profiles
        print(f"Finding {num_members} random profiles...")
        names, profile_ids = get_random_profiles(
            client, num_members, placeholder_prefix=self._get_placeholder_prefix(args.role)
        )

        # Get the group
        group_suffix = self._get_group_suffix(args.role)
        group_id = f"{args.venue_id}/{group_suffix}"

        try:
            group = client.get_group(group_id)
            print(f"Found existing group: {group_id}")
            existing_members = set(group.members or [])
        except Exception:
            print(f"Group {group_id} does not exist yet.")
            print("Creating it would require appropriate permissions.")
            existing_members = set()

        # Display the members that would be added
        print(f"\n{role_display.capitalize()} to add:")
        new_count = 0
        duplicate_count = 0

        for name, profile_id in zip(names, profile_ids):
            if profile_id in existing_members:
                print(f"  - {name} ({profile_id}) [ALREADY A MEMBER]")
                duplicate_count += 1
            else:
                print(f"  - {name} ({profile_id})")
                new_count += 1

        print(f"\nSummary:")
        print(f"  New {role_display}: {new_count}")
        print(f"  Already members: {duplicate_count}")
        print(f"  Total: {len(profile_ids)}")

        if new_count > 0:
            # Prepare the updated members list
            new_members = list(existing_members.union(set(profile_ids)))

            if args.only_show:
                print(f"\nTo add these {role_display}, the group would need to be updated with:")
                print(f"  Group ID: {group_id}")
                print(f"  Total members after addition: {len(new_members)}")
                print(f"\nNote: This is a preview only. Run without --only-show to actually add {role_display}.")
            else:
                # Actually add the members
                print(f"\nUpdating group...")
                try:
                    # Add only the new members (not duplicates)
                    new_member_ids = [pid for pid in profile_ids if pid not in existing_members]
                    client.add_members_to_group(group_id, new_member_ids)
                    print(f"✓ Successfully added {new_count} new {role_display} to {group_id}")
                    print(f"  Total members now: {len(new_members)}")
                except Exception as e:
                    print(f"Error: Failed to update group: {e}")
        else:
            print(f"\nNo new {role_display} to add (all are already members).")

    def _list_members(self, args: Namespace, client) -> None:
        """
        List all members of the specified role and output their information as JSON.
        """
        import sys

        group_suffix = self._get_group_suffix(args.role)
        group_id = f"{args.venue_id}/{group_suffix}"
        role_display = self._get_role_display_name(args.role)

        try:
            group = client.get_group(group_id)
            members = group.members or []
        except Exception as e:
            print(f"Error: Could not fetch group {group_id}: {e}", file=sys.stderr)
            return

        print(f"Fetching information for {len(members)} {role_display}...", file=sys.stderr)

        members_data = []
        for member_id in members:
            try:
                # Try to get profile information
                if member_id.startswith("~") or "@" in member_id:
                    profile = client.get_profile(member_id)
                    member_info = {
                        "id": profile.id,
                        "name": profile.get_preferred_name() if hasattr(profile, "get_preferred_name") else None,
                        "email": profile.get_preferred_email() if hasattr(profile, "get_preferred_email") else None,
                        "emails": profile.content.get("emails", []) if hasattr(profile, "content") else [],
                        "homepage": profile.content.get("homepage") if hasattr(profile, "content") else None,
                    }
                else:
                    # It's a group or other ID
                    member_info = {
                        "id": member_id,
                        "name": None,
                        "email": None,
                        "emails": [],
                        "homepage": None,
                    }
                members_data.append(member_info)
            except Exception as e:
                # If we can't get profile info, just include the ID
                members_data.append({
                    "id": member_id,
                    "name": None,
                    "email": None,
                    "emails": [],
                    "homepage": None,
                    "error": str(e),
                })

        # Output the JSON
        output_data = {
            "venue_id": args.venue_id,
            "role": args.role,
            "group_id": group_id,
            "count": len(members_data),
            "members": members_data,
        }

        if args.output:
            # Write to file
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=2)
            print(f"Members information saved to {args.output}", file=sys.stderr)
        else:
            # Write to stdout
            print(json.dumps(output_data, indent=2))
