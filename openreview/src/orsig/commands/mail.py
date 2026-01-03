"""
Mail command for sending emails via OpenReview.
"""

import os
import re
from argparse import ArgumentParser, Namespace

from ..command import Command
from ..client import get_client
from ..log import log
from ..qlever import recipients_from_query


class MailCommand(Command):
    """
    Send emails from a file with headers and body via OpenReview.
    """

    separator = "\n\n----------"

    @property
    def name(self) -> str:
        return "mail"

    @property
    def help(self) -> str:
        return "Send emails via OpenReview from a file with headers and body"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """
        Add mail command arguments.
        """
        parser.add_argument(
            "file",
            help="File containing email headers and body (blank line separates headers from body)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and show the email without sending",
        )
        parser.add_argument(
            "--recipients-from-sparql-query",
            metavar="HASH",
            help="Replace To: recipients with results from a SPARQL query (short hash)",
        )

    def _get_name(self, profile) -> str:
        """
        Get the name from a profile: first name if available, otherwise full name.
        """
        content = profile.content if hasattr(profile, "content") else {}
        names = content.get("names", [])
        if names:
            first_name = names[0].get("first")
            if first_name:
                return first_name
            fullname = names[0].get("fullname", "")
            if fullname:
                return fullname
        return ""

    def _parse_from_header(self, from_header: str) -> dict:
        """
        Parse From header into sender dict with fromName and fromEmail.
        Handles formats like: "Name <email>" or just "email"
        """
        match = re.match(r"(.+?)\s*<(.+?)>", from_header)
        if match:
            return {
                "fromName": match.group(1).strip(),
                "fromEmail": match.group(2).strip(),
            }
        return {"fromName": "", "fromEmail": from_header.strip()}

    def execute(self, args: Namespace) -> None:
        """
        Send email from a file with headers and body via OpenReview.
        """
        client = get_client()

        # Read the file
        with open(args.file, "r") as f:
            content = f.read()

        # Replace To: recipients from SPARQL query if requested
        if args.recipients_from_sparql_query:
            if not content.startswith("To:"):
                log.error(
                    "Mail file must start with 'To:' when using --recipients-from-sparql-query"
                )
                return
            query_recipients = recipients_from_query(args.recipients_from_sparql_query)
            new_to_line = "To: " + ", ".join(query_recipients)
            # Replace the first line (To: ...) with the new recipients
            content = new_to_line + content[content.index("\n") :]
            # Write updated content back to file
            with open(args.file, "w") as f:
                f.write(content)

        # Split headers and body (separated by blank line)
        parts = content.split("\n\n", 1)
        if len(parts) < 2:
            log.error(
                "Invalid email format: no blank line separating headers from body"
            )
            return

        headers_section, body = parts

        # Clean up body: remove trailing empty lines
        body = body.rstrip()

        # Parse headers
        headers = {}
        for line in headers_section.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        # Validate required headers
        if "To" not in headers:
            log.error("Missing required header: To")
            return
        if "Subject" not in headers:
            log.error("Missing required header: Subject")
            return

        # Get From header from file or environment
        if "From" not in headers:
            from_env = os.environ.get("MAIL_FROM")
            if from_env:
                headers["From"] = from_env
            else:
                log.error("Missing required header: From (set in file or $MAIL_FROM)")
                return

        # Parse sender - only use if email ends with @openreview.net
        parsed_sender = self._parse_from_header(headers["From"])
        if parsed_sender["fromEmail"].endswith("@openreview.net"):
            sender = parsed_sender
        else:
            sender = None  # Let OpenReview use default

        # Parse recipients (To and Cc) - extract email/profile ID from "Name <email>" format
        recipients = []
        for r in headers.get("To", "").split(","):
            r = r.strip()
            parsed = self._parse_from_header(r)
            recipients.append(parsed["fromEmail"] if "<" in r else r)

        cc_recipients = []
        if "Cc" in headers:
            for r in headers["Cc"].split(","):
                r = r.strip()
                parsed = self._parse_from_header(r)
                cc_recipients.append(parsed["fromEmail"] if "<" in r else r)

        # Get Reply-To (with or without hyphen), keep full format with name
        reply_to_header = headers.get("Reply-To") or headers.get("Reply To")
        if reply_to_header:
            reply_to = reply_to_header.strip()
        else:
            reply_to = headers["From"]

        # Check if personalization is needed
        needs_personalization = "{{name}}" in body

        # Show what we're sending
        log.info("")
        log.info(f"From: {headers.get('From')}")
        log.info(f"To: {headers.get('To')}")
        if cc_recipients:
            log.info(f"Cc: {headers.get('Cc')}")
        if reply_to != headers["From"]:
            log.info(f"Reply-To: {reply_to}")
        log.info(f"Subject: {headers.get('Subject')}")
        log.info(f"\n{body}")

        n = len(recipients)
        num_recipients = "one recipient" if n == 1 else f"{n} recipients"

        if args.dry_run:
            log.warning(
                f"Dry run: without --dry-run, email would be sent to {num_recipients}: "
                f"{headers.get('To')}"
            )
            return

        # Confirm before sending
        try:
            input(
                f"\n\033[94mPress CTRL+C to abort, RETURN to send email to {num_recipients}: "
                f"{headers.get('To')} \033[0m"
            )
        except KeyboardInterrupt:
            log.warning("\nAborted")
            return

        # Build invitation ID for messaging
        invitation = f"{args.venue_id}/-/Edit"

        # Send the email(s) to To recipients
        sent_count = 0
        failed_count = 0
        if needs_personalization:
            # Send individual personalized messages
            for recipient in recipients:
                # Get profile to find name
                try:
                    profile = client.get_profile(recipient)
                    name = self._get_name(profile)
                except Exception:
                    name = ""

                # Personalize body
                personalized_body = body.replace("{{name}}", name if name else "")

                try:
                    client.post_message(
                        subject=headers["Subject"],
                        recipients=[recipient],
                        message=personalized_body + self.separator,
                        invitation=invitation,
                        sender=sender,
                        replyTo=reply_to,
                    )
                    sent_count += 1
                except Exception as e:
                    log.warning(f"Failed to send to {recipient}: {e}")
                    failed_count += 1
        else:
            # Send single message to all To recipients
            try:
                client.post_message(
                    subject=headers["Subject"],
                    recipients=recipients,
                    message=body + self.separator,
                    invitation=invitation,
                    sender=sender,
                    replyTo=reply_to,
                )
                sent_count = len(recipients)
            except Exception as e:
                log.error(f"Failed to send email: {e}")
                failed_count = len(recipients)

        # Report results
        def pluralize(n):
            return "one recipient" if n == 1 else f"{n} recipients"

        if failed_count == 0:
            log.info(f"Email sent successfully to {pluralize(sent_count)}")
        else:
            log.info(
                f"Email sent to {pluralize(sent_count)}, failed for {pluralize(failed_count)}"
            )

        # Send FYI to Cc recipients
        if cc_recipients:
            fyi_subject = f"FYI: {headers['Subject']}"
            fyi_body = (
                f"FYI, the mail below was sent to {num_recipients}: "
                f"{headers.get('To')}"
                f"{self.separator}\n\n"
                f"{body}"
                f"{self.separator}"
            )

            try:
                client.post_message(
                    subject=fyi_subject,
                    recipients=cc_recipients,
                    message=fyi_body,
                    invitation=invitation,
                    sender=sender,
                )
                log.info(f"FYI sent to Cc: {headers.get('Cc')}")
            except Exception as e:
                log.error(f"Failed to send FYI to Cc: {e}")
