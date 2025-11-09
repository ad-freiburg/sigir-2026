#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import argparse
import json
import os
import random
import string
import sys
import tempfile
import openreview
import argcomplete
import numpy as np
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def get_client(baseurl, username, password):
    """Initialize and return OpenReview client."""
    return openreview.api.OpenReviewClient(
        baseurl=baseurl,
        username=username,
        password=password,
    )


def create_dummy_pdf(title, authors, abstract):
    """Create a simple dummy PDF for testing submissions."""
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False) as f:
        pdf = canvas.Canvas(f.name, pagesize=letter)
        width, height = letter
        max_width = width - 144

        # Title - wrap it like abstract
        pdf.setFont("Helvetica-Bold", 16)
        y = height - 72
        title_words = title.split()
        title_lines = []
        current_line = []

        for word in title_words:
            current_line.append(word)
            test_line = " ".join(current_line)
            if pdf.stringWidth(test_line, "Helvetica-Bold", 16) > max_width:
                current_line.pop()
                title_lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            title_lines.append(" ".join(current_line))

        for line in title_lines:
            pdf.drawString(72, y, line)
            y -= 20

        # Authors
        y -= 10
        pdf.setFont("Helvetica", 12)
        authors_text = ", ".join(authors)
        # Wrap authors too if needed
        if pdf.stringWidth(authors_text, "Helvetica", 12) > max_width:
            # Split into multiple lines if too long
            author_words = authors_text.split()
            author_lines = []
            current_line = []
            for word in author_words:
                current_line.append(word)
                test_line = " ".join(current_line)
                if pdf.stringWidth(test_line, "Helvetica", 12) > max_width:
                    current_line.pop()
                    author_lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                author_lines.append(" ".join(current_line))
            for line in author_lines:
                pdf.drawString(72, y, line)
                y -= 16
        else:
            pdf.drawString(72, y, authors_text)
            y -= 16

        # Abstract
        y -= 40
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(72, y, "Abstract")

        y -= 20
        pdf.setFont("Helvetica", 10)
        # Wrap abstract text
        max_width = width - 144
        words = abstract.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            if pdf.stringWidth(test_line, "Helvetica", 10) > max_width:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        for line in lines[:20]:  # Limit to 20 lines
            pdf.drawString(72, y, line)
            y -= 14
            if y < 72:
                break

        pdf.save()
        return f.name


def cmd_submissions(args):
    """
    Download all information about current submissions.
    """

    # Fetch submissions.
    submission_invitation = f"{args.venue_id}/-/Submission"
    print(
        f"Fetching all submissions from {args.venue_id} "
        f"using invitation  {submission_invitation} ..."
    )
    client = get_client(args.api_url, args.username, args.password)
    submissions = client.get_all_notes(invitation=submission_invitation)

    # Save to JSON file.
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


def cmd_invitations(args):
    """List all invitations for the venue."""
    client = get_client(args.api_url, args.username, args.password)

    print(f"Fetching invitations for venue: {args.venue_id}...")
    invitations = client.get_all_invitations(prefix=args.venue_id)

    print(f"Found {len(invitations)} invitations:")
    for inv in invitations:
        print(f"  - {inv.id}")


def cmd_users(args):
    """List users/profiles and groups for the venue."""
    client = get_client(args.api_url, args.username, args.password)

    if args.search:
        # Search for profiles
        print(f"Searching profiles with term: {args.search}...")
        profiles = client.search_profiles(term=args.search)

        print(f"Found {len(profiles)} profiles:")
        for profile in profiles:
            preferred_name = (
                profile.get_preferred_name()
                if hasattr(profile, "get_preferred_name")
                else "N/A"
            )
            preferred_email = (
                profile.get_preferred_email()
                if hasattr(profile, "get_preferred_email")
                else "N/A"
            )
            print(f"  - {profile.id}")
            print(f"    Name: {preferred_name}")
            print(f"    Email: {preferred_email}")

    elif args.groups:
        # List all groups for venue
        print(f"Fetching groups for venue: {args.venue_id}...")
        groups = client.get_all_groups(prefix=args.venue_id)

        print(f"Found {len(groups)} groups:")
        for group in groups:
            member_count = len(group.members) if group.members else 0
            print(f"  - {group.id} ({member_count} members)")

            if args.verbose and group.members:
                for member in group.members[:10]:  # Show first 10
                    print(f"      {member}")
                if member_count > 10:
                    print(f"      ... and {member_count - 10} more")

    else:
        # Get all users across all venue groups
        print(f"Fetching all users for venue: {args.venue_id}...")
        groups = client.get_all_groups(prefix=args.venue_id)

        # Collect all unique user IDs (not group IDs)
        all_users = set()
        for group in groups:
            if group.members:
                for member in group.members:
                    # Skip if it's a group ID (contains /)
                    if "/" not in member:
                        all_users.add(member)

        all_users = sorted(all_users)
        print(f"Found {len(all_users)} unique users:")

        for user in all_users:
            print(f"  - {user}")

            # Optionally get profile details
            if args.verbose:
                try:
                    # Check if it's a profile ID or email
                    if user.startswith("~") or "@" in user:
                        profile = client.get_profile(user)
                        name = (
                            profile.get_preferred_name()
                            if hasattr(profile, "get_preferred_name")
                            else "N/A"
                        )
                        email = (
                            profile.get_preferred_email()
                            if hasattr(profile, "get_preferred_email")
                            else "N/A"
                        )
                        print(f"    Name: {name}, Email: {email}")
                except Exception as e:
                    if args.verbose:
                        print(f"    Could not fetch profile: {e}")


def format_author_name(author_id):
    """Convert author ID to proper name format.

    Example: ~Hannah_Bast1 -> Hannah Bast
    """
    if author_id.startswith("~"):
        # Remove ~ and number suffix
        name = author_id[1:].rsplit("1", 1)[0]  # Remove trailing number
        # Replace underscores with spaces
        name = name.replace("_", " ")
        return name
    return author_id


def generate_random_paper(model, prompt, author_ids, api_key=None):
    """Generate a random SIGIR paper title, abstract, and author names using OpenAI API.

    Returns:
        tuple: (title, abstract, authors)
    """
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    try:
        client = OpenAI(api_key=api_key)

        # Add author IDs to the prompt
        author_list = ", ".join(author_ids)
        full_prompt = f"{prompt}\n\nAuthor IDs: {author_list}\n\nConvert author IDs (like ~Hannah_Bast1) to proper names (like Hannah Bast) in Firstname Lastname format."

        # Define JSON schema
        json_schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "paper_generation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "The paper title"},
                        "abstract": {
                            "type": "string",
                            "description": "The paper abstract (exactly three sentences)",
                        },
                        "authors": {
                            "type": "array",
                            "description": "List of author names in Firstname Lastname format",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["title", "abstract", "authors"],
                    "additionalProperties": False,
                },
            },
        }

        # GPT-5 models use max_completion_tokens and only support temperature=1
        if model.startswith("gpt-5"):
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in Information Retrieval and SIGIR conference papers.",
                    },
                    {"role": "user", "content": full_prompt},
                ],
                max_completion_tokens=500,
                response_format=json_schema,
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in Information Retrieval and SIGIR conference papers.",
                    },
                    {"role": "user", "content": full_prompt},
                ],
                max_tokens=500,
                temperature=0.9,
                response_format=json_schema,
            )

        content = response.choices[0].message.content.strip()

        # Parse JSON response
        data = json.loads(content)

        title = data["title"]
        abstract = data["abstract"]
        authors = data["authors"]

        # Ensure authors is a list
        if isinstance(authors, str):
            authors = [authors]

        # Ensure we have the right number of authors
        if len(authors) != len(author_ids):
            authors = [format_author_name(aid) for aid in author_ids]

        return title, abstract, authors

    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {e}")


def get_random_authors(client, num_authors):
    """Get random authors by searching with random two-letter strings."""
    authors = []
    authorids = []

    max_attempts = 50  # Prevent infinite loops
    attempts = 0

    while len(authors) < num_authors and attempts < max_attempts:
        # Generate random two-letter search string
        search_term = "".join(random.choices(string.ascii_lowercase, k=2))

        try:
            profiles = client.search_profiles(term=search_term)

            if profiles:
                # Pick a random profile from results
                profile = random.choice(profiles)
                profile_id = profile.id

                # Avoid duplicates
                if profile_id not in authorids:
                    authorids.append(profile_id)
                    # Get preferred name
                    name = (
                        profile.get_preferred_name()
                        if hasattr(profile, "get_preferred_name")
                        else profile_id
                    )
                    authors.append(name)
        except Exception:
            pass  # Continue trying with different search terms

        attempts += 1

    # If we couldn't find enough authors, pad with placeholder
    while len(authors) < num_authors:
        authors.append(f"Random Author {len(authors) + 1}")
        authorids.append(f"random{len(authors)}@example.com")

    return authors, authorids


def cmd_submit(args):
    """Submit papers to OpenReview."""
    client = get_client(args.api_url, args.username, args.password)

    # Construct the submission invitation ID
    submission_invitation = f"{args.venue_id}/-/Submission"

    # Handle random paper generation
    if args.random:
        print(f"Generating {args.random} random paper submissions...")
        print(f"Mean number of authors (Poisson λ): {args.mean_num_authors}")

        # Check if paper model should be used (not empty string)
        use_ai = args.paper_model and args.paper_model.strip()

        if use_ai:
            print(f"Using OpenAI model: {args.paper_model}")
        else:
            print("Using fallback paper generation (no AI)")
        print()

        # ANSI codes for bold
        BOLD = "\033[1m"
        RESET = "\033[0m"

        successful = 0
        failed = 0

        for i in range(args.random):
            # Generate number of authors from Poisson distribution
            num_authors = max(1, np.random.poisson(args.mean_num_authors))

            print(f"{BOLD}Paper {i + 1}/{args.random}{RESET}")
            print(f"Number of authors: {num_authors}")

            # Get random author IDs
            print(f"Finding {num_authors} random authors...")
            _, authorids = get_random_authors(client, num_authors)

            # Generate random title, abstract, and author names
            if use_ai:
                print(
                    f"Generating title, abstract, and author names using {args.paper_model}..."
                )
                title, abstract, authors = generate_random_paper(
                    args.paper_model, args.paper_prompt, authorids
                )
            else:
                title = (
                    f"Random Paper {i + 1}: A Study on Topic {random.randint(1, 1000)}"
                )
                abstract = (
                    f"This is a randomly generated abstract for paper {i + 1}. "
                    f"It explores various aspects of the research topic with {num_authors} authors."
                )
                authors = [format_author_name(aid) for aid in authorids]

            # Print metadata
            print(f"Title: {title}")
            print(f"Authors: {', '.join(authors)}")
            print(f"Author IDs: {', '.join(authorids)}")
            print(f"Abstract: {abstract}")

            # Submit or just show
            if not args.only_show:
                pdf_path = None
                try:
                    print("Submitting to OpenReview...")

                    # Get the logged-in user's profile ID for signatures
                    user_profile = client.get_profile(args.username)
                    user_signature = user_profile.id

                    # Ensure we have at least one keyword
                    keywords = (
                        args.keywords.split(",")
                        if args.keywords
                        else ["Information Retrieval"]
                    )

                    # Create dummy PDF
                    print("Creating PDF...")
                    pdf_path = create_dummy_pdf(title, authors, abstract)

                    # Upload PDF
                    print("Uploading PDF...")
                    pdf_url = client.put_attachment(
                        pdf_path, submission_invitation, "pdf"
                    )

                    # Create submission note
                    note = openreview.api.Note(
                        content={
                            "title": {"value": title},
                            "abstract": {"value": abstract},
                            "authors": {"value": authors},
                            "authorids": {"value": authorids},
                            "keywords": {"value": keywords},
                            "pdf": {"value": pdf_url},
                        }
                    )

                    # Submit the note
                    submission = client.post_note_edit(
                        invitation=submission_invitation,
                        signatures=[user_signature],
                        note=note,
                    )

                    submission_id = submission["note"]["id"]
                    print(f"✓ Submitted successfully: {submission_id}")
                    successful += 1

                except Exception as e:
                    print(f"✗ Submission failed: {e}")
                    failed += 1
                finally:
                    # Clean up temporary PDF
                    if pdf_path and os.path.exists(pdf_path):
                        os.unlink(pdf_path)

            print()

        # Print summary if actually submitting
        if not args.only_show and args.random > 0:
            print(f"{BOLD}Summary{RESET}")
            print(f"Successful: {successful}")
            print(f"Failed: {failed}")
            print(f"Total: {args.random}")

        return

    # Original submission logic
    # Get author information
    if not args.authors or not args.authorids:
        print("ERROR: --authors and --authorids are required for submission")
        print(
            "Example: --authors 'Alice Smith,Bob Jones' --authorids 'alice@example.com,bob@example.com'"
        )
        sys.exit(1)

    authors = [a.strip() for a in args.authors.split(",")]
    authorids = [a.strip() for a in args.authorids.split(",")]

    if len(authors) != len(authorids):
        print(
            f"ERROR: Number of authors ({len(authors)}) must match number of authorids ({len(authorids)})"
        )
        sys.exit(1)

    # Process each PDF file
    successful = 0
    failed = 0

    for pdf_path in args.pdf_files:
        # Check if PDF exists
        if not os.path.exists(pdf_path):
            print(f"ERROR: PDF not found: {pdf_path}")
            failed += 1
            continue

        # Look for corresponding JSON file
        base_name = os.path.splitext(pdf_path)[0]
        json_path = base_name + ".json"

        if not os.path.exists(json_path):
            print(f"ERROR: JSON file not found for {pdf_path}: {json_path}")
            failed += 1
            continue

        # Load JSON metadata
        try:
            with open(json_path, "r") as f:
                metadata = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {json_path}: {e}")
            failed += 1
            continue

        # Extract title and abstract
        title = metadata.get("title", "")
        abstract = metadata.get("summary", "")

        if not title:
            print(f"ERROR: No title found in {json_path}")
            failed += 1
            continue

        if not abstract:
            print(
                f"WARNING: No summary/abstract found in {json_path}, using empty abstract"
            )

        # Extract keywords if available
        keywords = args.keywords.split(",") if args.keywords else []

        print(f"\nSubmitting: {title}")
        print(f"  PDF: {pdf_path}")
        print(f"  Authors: {', '.join(authors)}")

        try:
            # Upload PDF
            print("  Uploading PDF...")
            pdf_url = client.put_attachment(pdf_path, submission_invitation, "pdf")

            # Create submission note
            print("  Creating submission...")
            note = openreview.api.Note(
                content={
                    "title": {"value": title},
                    "abstract": {"value": abstract},
                    "authors": {"value": authors},
                    "authorids": {"value": authorids},
                    "keywords": {"value": keywords},
                    "pdf": {"value": pdf_url},
                }
            )

            # Submit the note
            submission = client.post_note_edit(
                invitation=submission_invitation,
                signatures=[authorids[0]],  # Use first author as signature
                note=note,
            )

            print(f"  ✓ SUCCESS: Submitted with ID: {submission['note']['id']}")
            successful += 1

        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1

    # Summary
    print(f"\n{'=' * 50}")
    print("Submission Summary:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {successful + failed}")


def main():
    parser = argparse.ArgumentParser(description="OpenReview CLI tool for SIGIR 2026")

    # Global arguments
    parser.add_argument(
        "--api-url",
        default="https://devapi2.openreview.net",
        help="OpenReview API URL (default: https://devapi2.openreview.net)",
    )
    parser.add_argument(
        "--username",
        default="bast@informatik.uni-freiburg.de",
        help="OpenReview username (default: bast@informatik.uni-freiburg.de)",
    )
    parser.add_argument(
        "--password",
        default="isaOO77!!!",
        help="OpenReview password",
    )
    parser.add_argument(
        "--venue-id",
        default="SIGIR/2026/Test",
        help="Venue ID (default: SIGIR/2026/Test)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Submissions command.
    submissions_parser = subparsers.add_parser(
        "submissions", help="Download all information about current submissions"
    )
    submissions_parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: submissions.json)",
        default="submissions.json",
    )
    submissions_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print detailed information about each submission",
    )
    submissions_parser.set_defaults(func=cmd_submissions)

    # Invitations command (for debugging).
    invitations_parser = subparsers.add_parser(
        "invitations", help="List all invitations for the venue"
    )
    invitations_parser.set_defaults(func=cmd_invitations)

    # Users command.
    users_parser = subparsers.add_parser(
        "users", help="List users, profiles, and groups"
    )
    users_parser.add_argument(
        "--search",
        help="Search for profiles by term (in username or email)",
    )
    users_parser.add_argument(
        "--groups",
        action="store_true",
        help="List all groups for the venue",
    )
    users_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed information",
    )
    users_parser.set_defaults(func=cmd_users)

    # Submit command.
    submit_parser = subparsers.add_parser(
        "submit",
        help="Submit papers to OpenReview (requires matching PDF and JSON files)",
    )
    submit_parser.add_argument(
        "pdf_files",
        nargs="*",
        help="PDF files to submit (will look for matching .json files)",
    )
    submit_parser.add_argument(
        "--authors",
        help="Comma-separated list of author names (e.g., 'Alice Smith,Bob Jones')",
    )
    submit_parser.add_argument(
        "--authorids",
        help="Comma-separated list of author IDs/emails (e.g., 'alice@example.com,bob@example.com')",
    )
    submit_parser.add_argument(
        "--keywords",
        help="Comma-separated list of keywords (optional)",
    )
    submit_parser.add_argument(
        "--random",
        type=int,
        metavar="K",
        help="Generate K random paper submissions (for testing)",
    )
    submit_parser.add_argument(
        "--only-show",
        action="store_true",
        help="Only show paper metadata without actually submitting to OpenReview",
    )
    submit_parser.add_argument(
        "--mean-num-authors",
        type=float,
        default=3.0,
        help="Mean number of authors for Poisson distribution (default: 3.0)",
    )
    submit_parser.add_argument(
        "--paper-model",
        default="gpt-4o-mini",
        help="OpenAI model for paper generation (default: 'gpt-4o-mini'). Try 'gpt-5-mini' if available. Requires OPENAI_API_KEY env var. Use empty string to disable.",
    )
    submit_parser.add_argument(
        "--paper-prompt",
        default=(
            "Generate a title, abstract, and author names for a creative and diverse research paper that could be submitted to "
            "SIGIR 2026 (International ACM SIGIR Conference on Research and Development in Information Retrieval). "
            "Be creative and explore diverse topics within information retrieval. Consider various research areas such as: "
            "classical IR models, neural ranking, query processing, semantic search, cross-lingual retrieval, "
            "multilingual IR, question answering, knowledge graphs for search, information extraction, "
            "document understanding, query expansion, relevance feedback, evaluation metrics, user studies, "
            "personalization, federated search, enterprise search, web search, social media search, "
            "voice search, mobile search, conversational agents, interactive IR, search result diversification, "
            "domain-specific retrieval, legal IR, medical IR, scientific IR, patent search, code search, "
            "image search, video search, music IR, or any other IR-related topic. "
            "Vary your approach and be original - avoid repetitive patterns.\n\n"
            "Respond with JSON in this exact format:\n"
            "{\n"
            '  "title": "paper title",\n'
            '  "abstract": "exactly three sentences describing motivation, methods, and key findings",\n'
            '  "authors": ["Firstname Lastname", "Firstname Middlename Lastname", ...]\n'
            "}"
        ),
        help="Prompt for generating paper title, abstract, and author names",
    )
    submit_parser.set_defaults(func=cmd_submit)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
