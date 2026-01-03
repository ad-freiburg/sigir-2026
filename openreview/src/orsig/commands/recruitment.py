"""
Recruitment command for managing reviewers, area chairs, and senior area chairs.
"""

import json
from argparse import ArgumentParser, Namespace

import openreview

from ..command import Command
from ..client import get_client
from ..utils import get_random_profiles
from ..rdf import Rdf
from ..profile import ProfileWithPapers
from ..log import log


class RecruitmentCommand(Command):
    """
    Manage recruitment of reviewers, area chairs, and senior area chairs for the venue.
    """

    @property
    def name(self) -> str:
        return "recruitment"

    @property
    def help(self) -> str:
        return "Manage recruitment for the venue"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """
        Add recruitment command arguments.
        """
        parser.add_argument(
            "--role",
            required=True,
            choices=["pc", "spc", "ac"],
            help="Role type: pc (reviewers), spc (area chairs), ac (senior area chairs)",
        )
        parser.add_argument(
            "--dump",
            choices=["json", "rdf"],
            help="Dump recruitment data in the specified format",
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
            "--set-reduced-load",
            nargs=2,
            metavar=("PROFILE_ID", "LOAD"),
            help="Set reduced load for a member (e.g., --set-reduced-load ~John_Doe1 2)",
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
        parser.add_argument(
            "--recache",
            action="store_true",
            help="Fetch fresh profiles from OpenReview and update the cache",
        )

    def execute(self, args: Namespace) -> None:
        """
        Execute recruitment command.
        """
        # Get the singleton client (initialized in main.py)
        client = get_client()

        if args.dump:
            self._dump_members(args, client)
        elif args.add:
            self._add_specific_members(args, client)
        elif args.remove:
            self._remove_specific_members(args, client)
        elif args.add_random:
            self._add_random_members(args, client)
        elif args.set_reduced_load:
            self._set_reduced_load(args, client)
        else:
            log.info(
                "No action specified. Use --dump, --add, --remove, or --set-reduced-load."
            )

    def _get_group_suffix(self, role: str) -> str:
        """
        Map CLI role name to OpenReview group suffix.
        """
        role_mapping = {
            "pc": "Reviewers",
            "spc": "Area_Chairs",
            "ac": "Senior_Area_Chairs",
        }
        return role_mapping[role]

    def _get_role_display_name(self, role: str) -> str:
        """
        Get human-readable display name for role.
        """
        display_names = {
            "pc": "PC aka Reviewers",
            "spc": "SPC aka Area Chairs",
            "ac": "AC aka Senior Area Chairs",
        }
        return display_names[role]

    def _get_placeholder_prefix(self, role: str) -> str:
        """
        Get placeholder prefix for random profile generation.
        """
        prefixes = {
            "pc": "Random PC",
            "spc": "Random SPC",
            "ac": "Random AC",
        }
        return prefixes[role]

    def _get_rdf_class(self, role: str) -> str:
        """
        Get RDF class name for the role.
        """
        rdf_classes = {
            "pc": ":PC",
            "spc": ":SPC",
            "ac": ":AC",
        }
        return rdf_classes[role]

    def _get_reduced_loads(self, args: Namespace, client) -> dict[str, int]:
        """
        Fetch reduced_load values from recruitment notes.
        Returns a dict mapping user email/profile ID to their reduced load as integer.
        """
        group_suffix = self._get_group_suffix(args.role)
        recruitment_invitation = f"{args.venue_id}/{group_suffix}/-/Recruitment"

        reduced_loads = {}
        try:
            notes = client.get_all_notes(invitation=recruitment_invitation)
            for note in notes:
                content = note.content
                if "reduced_load" in content and content["reduced_load"].get("value"):
                    user = content.get("user", {}).get("value", "")
                    load_str = content["reduced_load"]["value"]
                    if user and load_str:
                        try:
                            reduced_loads[user] = int(load_str)
                        except ValueError:
                            pass
        except Exception as e:
            log.warning(f"Could not fetch recruitment notes: {e}")

        return reduced_loads

    def _set_reduced_load(self, args: Namespace, client) -> None:
        """
        Set the reduced load for a member by updating their recruitment note.
        """
        profile_id, load_str = args.set_reduced_load

        try:
            load = int(load_str)
        except ValueError:
            log.error(f"Invalid load value: {load_str}. Must be an integer.")
            return

        group_suffix = self._get_group_suffix(args.role)
        recruitment_invitation = f"{args.venue_id}/{group_suffix}/-/Recruitment"

        # Resolve profile ID to canonical form and get emails
        try:
            profile = client.get_profile(profile_id)
            canonical_id = profile.id
            profile_emails = set(profile.content.get("emails", []))
            log.info(f"Setting reduced load for {canonical_id} to {load}")
        except Exception as e:
            log.error(f"Could not find profile {profile_id}: {e}")
            return

        # Find the recruitment note for this user (by email)
        try:
            notes = client.get_all_notes(invitation=recruitment_invitation)
            recruitment_note = None
            for note in notes:
                user_email = note.content.get("user", {}).get("value", "")
                if user_email in profile_emails:
                    recruitment_note = note
                    break

            if not recruitment_note:
                log.error(
                    f"No recruitment note found for {canonical_id}. "
                    "The user may not have responded to recruitment yet."
                )
                return

        except Exception as e:
            log.error(f"Could not fetch recruitment notes: {e}")
            return

        # Update the recruitment note with the new reduced_load using the meta Edit invitation
        try:
            client.post_note_edit(
                invitation=f"{args.venue_id}/-/Edit",
                signatures=[args.venue_id],
                note=openreview.api.Note(
                    id=recruitment_note.id,
                    content={
                        "reduced_load": {"value": str(load)},
                    },
                ),
            )
            log.info(f"Successfully set reduced load for {canonical_id} to {load}")
        except Exception as e:
            log.error(f"Could not update recruitment note: {e}")

    def _add_specific_members(self, args: Namespace, client) -> None:
        """
        Add specific members by ID to the specified role group.
        """
        user_ids = args.add
        role_display = self._get_role_display_name(args.role)
        log.info(f"Adding {len(user_ids)} {role_display} to {args.venue_id}...")

        # Get the group
        group_suffix = self._get_group_suffix(args.role)
        group_id = f"{args.venue_id}/{group_suffix}"

        try:
            group = client.get_group(group_id)
            log.info(f"Found existing group: {group_id}")
            existing_members = set(group.members or [])
        except Exception:
            log.info(f"Group {group_id} does not exist yet.")
            log.info("Creating it would require appropriate permissions.")
            existing_members = set()

        # Fetch profile information and check for duplicates
        log.info(f"\n{role_display.capitalize()} to add:")
        new_count = 0
        duplicate_count = 0
        names = []

        for user_id in user_ids:
            # Try to get profile information
            try:
                if user_id.startswith("~") or "@" in user_id:
                    profile = client.get_profile(user_id)
                    name = (
                        profile.get_preferred_name()
                        if hasattr(profile, "get_preferred_name")
                        else user_id
                    )
                else:
                    name = user_id
            except Exception:
                name = user_id

            names.append(name)

            if user_id in existing_members:
                log.info(f"  - {name} ({user_id}) [ALREADY A MEMBER]")
                duplicate_count += 1
            else:
                log.info(f"  - {name} ({user_id})")
                new_count += 1

        log.info("\nSummary:")
        log.info(f"  New {role_display}: {new_count}")
        log.info(f"  Already members: {duplicate_count}")
        log.info(f"  Total: {len(user_ids)}")

        if new_count > 0:
            # Prepare the updated members list
            new_members = list(existing_members.union(set(user_ids)))

            if args.only_show:
                log.info(
                    f"\nTo add these {role_display}, the group would need to be updated with:"
                )
                log.info(f"  Group ID: {group_id}")
                log.info(f"  Total members after addition: {len(new_members)}")
                log.info(
                    f"\nNote: This is a preview only. Run without --only-show to actually add {role_display}."
                )
            else:
                # Actually add the members
                log.info("\nUpdating group...")
                try:
                    # Add only the new members (not duplicates)
                    new_member_ids = [
                        uid for uid in user_ids if uid not in existing_members
                    ]
                    client.add_members_to_group(group_id, new_member_ids)
                    log.info(
                        f"Successfully added {new_count} new {role_display} to {group_id}"
                    )
                    log.info(f"  Total members now: {len(new_members)}")
                except Exception as e:
                    log.error(f" Failed to update group: {e}")
        else:
            log.info(f"\nNo new {role_display} to add (all are already members).")

    def _remove_specific_members(self, args: Namespace, client) -> None:
        """
        Remove specific members by ID from the specified role group.
        """
        user_ids = args.remove
        role_display = self._get_role_display_name(args.role)
        log.info(f"Removing {len(user_ids)} {role_display} from {args.venue_id}...")

        # Get the group
        group_suffix = self._get_group_suffix(args.role)
        group_id = f"{args.venue_id}/{group_suffix}"

        try:
            group = client.get_group(group_id)
            log.info(f"Found existing group: {group_id}")
            existing_members = set(group.members or [])
        except Exception as e:
            log.error(f" Could not fetch group {group_id}: {e}")
            return

        # Fetch profile information and check membership
        log.info(f"\n{role_display.capitalize()} to remove:")
        remove_count = 0
        not_member_count = 0
        names = []

        for user_id in user_ids:
            # Try to get profile information
            try:
                if user_id.startswith("~") or "@" in user_id:
                    profile = client.get_profile(user_id)
                    name = (
                        profile.get_preferred_name()
                        if hasattr(profile, "get_preferred_name")
                        else user_id
                    )
                else:
                    name = user_id
            except Exception:
                name = user_id

            names.append(name)

            if user_id in existing_members:
                log.info(f"  - {name} ({user_id})")
                remove_count += 1
            else:
                log.info(f"  - {name} ({user_id}) [NOT A MEMBER]")
                not_member_count += 1

        log.info("\nSummary:")
        log.info(f"  To remove: {remove_count}")
        log.info(f"  Not members: {not_member_count}")
        log.info(f"  Total: {len(user_ids)}")

        if remove_count > 0:
            # Prepare the updated members list
            remaining_members = [m for m in existing_members if m not in user_ids]

            if args.only_show:
                log.info(
                    f"\nTo remove these {role_display}, the group would need to be updated with:"
                )
                log.info(f"  Group ID: {group_id}")
                log.info(f"  Total members after removal: {len(remaining_members)}")
                log.info(
                    f"\nNote: This is a preview only. Run without --only-show to actually remove {role_display}."
                )
            else:
                # Actually remove the members
                log.info("\nUpdating group...")
                try:
                    # Remove only the members that exist
                    members_to_remove = [
                        uid for uid in user_ids if uid in existing_members
                    ]
                    client.remove_members_from_group(group_id, members_to_remove)
                    log.info(
                        f"Successfully removed {remove_count} {role_display} from {group_id}"
                    )
                    log.info(f"  Total members now: {len(remaining_members)}")
                except Exception as e:
                    log.error(f" Failed to update group: {e}")
        else:
            log.info(f"\nNo {role_display} to remove (none are members).")

    def _add_random_members(self, args: Namespace, client) -> None:
        """
        Add random members to the specified role group.
        """
        num_members = args.add_random
        role_display = self._get_role_display_name(args.role)
        log.info(f"Adding {num_members} random {role_display} to {args.venue_id}...")

        # Get random profiles
        log.info(f"Finding {num_members} random profiles...")
        names, profile_ids = get_random_profiles(
            client,
            num_members,
            placeholder_prefix=self._get_placeholder_prefix(args.role),
        )

        # Get the group
        group_suffix = self._get_group_suffix(args.role)
        group_id = f"{args.venue_id}/{group_suffix}"

        try:
            group = client.get_group(group_id)
            log.info(f"Found existing group: {group_id}")
            existing_members = set(group.members or [])
        except Exception:
            log.info(f"Group {group_id} does not exist yet.")
            log.info("Creating it would require appropriate permissions.")
            existing_members = set()

        # Display the members that would be added
        log.info(f"\n{role_display.capitalize()} to add:")
        new_count = 0
        duplicate_count = 0

        for name, profile_id in zip(names, profile_ids):
            if profile_id in existing_members:
                log.info(f"  - {name} ({profile_id}) [ALREADY A MEMBER]")
                duplicate_count += 1
            else:
                log.info(f"  - {name} ({profile_id})")
                new_count += 1

        log.info("\nSummary:")
        log.info(f"  New {role_display}: {new_count}")
        log.info(f"  Already members: {duplicate_count}")
        log.info(f"  Total: {len(profile_ids)}")

        if new_count > 0:
            # Prepare the updated members list
            new_members = list(existing_members.union(set(profile_ids)))

            if args.only_show:
                log.info(
                    f"\nTo add these {role_display}, the group would need to be updated with:"
                )
                log.info(f"  Group ID: {group_id}")
                log.info(f"  Total members after addition: {len(new_members)}")
                log.info(
                    f"\nNote: This is a preview only. Run without --only-show to actually add {role_display}."
                )
            else:
                # Actually add the members
                log.info("\nUpdating group...")
                try:
                    # Add only the new members (not duplicates)
                    new_member_ids = [
                        pid for pid in profile_ids if pid not in existing_members
                    ]
                    client.add_members_to_group(group_id, new_member_ids)
                    log.info(
                        f"Successfully added {new_count} new {role_display} to {group_id}"
                    )
                    log.info(f"  Total members now: {len(new_members)}")
                except Exception as e:
                    log.error(f" Failed to update group: {e}")
        else:
            log.info(f"\nNo new {role_display} to add (all are already members).")

    def _dump_members(self, args: Namespace, client) -> None:
        """
        Dump all members of the specified role and output their information as JSON or RDF.
        """

        group_suffix = self._get_group_suffix(args.role)
        group_id = f"{args.venue_id}/{group_suffix}"
        role_display = self._get_role_display_name(args.role)

        # Get all related groups in one call (main, `/Invited`, `/Declined`)
        try:
            groups = client.get_groups(prefix=group_id)
        except Exception as e:
            log.error(f"Could not fetch groups with prefix {group_id}: {e}")
            return

        # Determine which members are confirmed, invited, or declined.
        confirmed_members = set()
        invited_members = set()
        declined_members = set()
        for group in groups:
            if group.id == group_id:
                confirmed_members = set(group.members or [])
            elif group.id == f"{group_id}/Invited":
                invited_members = set(group.members or [])
            elif group.id == f"{group_id}/Declined":
                declined_members = set(group.members or [])
        all_members = list(confirmed_members | invited_members | declined_members)
        confirmed_count = len(confirmed_members)
        declined_count = len(declined_members)
        pending_count = len(all_members) - confirmed_count - declined_count

        log.info(
            f"Fetching information for {len(all_members)} {role_display} "
            f"({confirmed_count} accepted, {declined_count} declined, "
            f"{pending_count} pending) ..."
        )

        # Fetch reduced_load data from recruitment notes (keyed by email)
        reduced_loads = self._get_reduced_loads(args, client)
        if reduced_loads:
            log.info(f"Found {len(reduced_loads)} members with reduced load")

        # Fetch profile data for each member
        members_data = []
        profile_with_papers = ProfileWithPapers(
            cache_dir=args.cache_dir, recache=args.recache
        )

        for member_id in all_members:
            # Determine member status
            if member_id in confirmed_members:
                member_status = "accepted"
            elif member_id in declined_members:
                member_status = "declined"
            else:
                member_status = "pending"

            # Get profile information (defaults to empty profile on failure)
            profile_with_papers.get_profile(member_id)
            member_info = profile_with_papers.asJson()
            member_info["status"] = member_status

            # Check if this member has a reduced_load (match by email)
            member_emails = member_info.get("content", {}).get("emails", [])
            for email in member_emails:
                if email in reduced_loads:
                    member_info["reduced_load"] = reduced_loads[email]
                    break

            members_data.append(member_info)

        # Generate output based on format
        if args.dump == "rdf":
            # Generate RDF output
            rdf = Rdf()

            # Get the RDF class for this role
            rdf_class = self._get_rdf_class(args.role)

            # Add a triple for each member using the already-fetched profile data
            for member_info in members_data:
                profile_id = member_info.get("id")
                if profile_id:  # Skip if no ID
                    person_iri = rdf.personIri(profile_id)
                    rdf.add_triple(person_iri, "a", ":Person")
                    rdf.add_triple(person_iri, "a", rdf_class)
                    rdf.add_triple(
                        person_iri,
                        ":status",
                        rdf.literal(member_info.get("status", "pending")),
                    )
                    # Add reduced_load if present
                    if "reduced_load" in member_info:
                        rdf.add_triple(
                            person_iri,
                            ":reduced_load",
                            str(member_info["reduced_load"]),
                        )
                    # Add profile data
                    profile_with_papers.addToRdf(rdf, member_info, profile_id)

            output_content = rdf.as_turtle()
        else:
            # Generate JSON output
            accepted_count = len(
                [m for m in members_data if m.get("status") == "accepted"]
            )
            declined_count = len(
                [m for m in members_data if m.get("status") == "declined"]
            )
            pending_count = len(
                [m for m in members_data if m.get("status") == "pending"]
            )

            output_data = {
                "venue_id": args.venue_id,
                "role": args.role,
                "group_id": group_id,
                "total_count": len(members_data),
                "accepted_count": accepted_count,
                "declined_count": declined_count,
                "pending_count": pending_count,
                "members": members_data,
            }
            output_content = json.dumps(output_data, indent=2)

        # Output to file or stdout
        if args.output:
            with open(args.output, "w") as f:
                f.write(output_content)
            log.info(f"Members saved to {args.output} in {args.dump.upper()} format")
        else:
            print(output_content)
