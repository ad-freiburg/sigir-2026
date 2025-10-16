#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
"""
Generate structured reviews for academic papers in PDF format,
using OpenAI's GPT-4 API.
"""

import argparse
import json
import sys
import base64
import time
import threading
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List
from openai import OpenAI
import argcomplete
from pdf2image import convert_from_path


# ANSI color codes
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Model and pricing configuration
MODEL = "gpt-4o"
INPUT_PRICE_PER_MILLION_TOKENS = 2.50
OUTPUT_PRICE_PER_MILLION_TOKENS = 10.00

DEFAULT_PROMPT = """Write a succinct review with the following parts: (1) Extract the title of the paper; (2) A short summary of what the paper is about and what its contribution is; (3) A summary of the methods used in the paper; (4) A summary of the results presented in the paper; (5) The strengths of the paper if any numbered (S1), (S2), ...; (6) The weaknesses of the paper if any numbered (W1), (W2), ...; (7) A recommendation from the scale: REJECT (-2), WEAK REJECT (-1), BORDERLINE (0), ACCEPT (1), STRONG ACCEPT (2)"""


class Spinner:
    """ANSI spinner animation for indicating progress."""

    def __init__(self):
        self.spinning = False
        self.spinner_thread = None
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current_frame = 0

    def _spin(self):
        """Internal method to run the spinner animation."""
        while self.spinning:
            frame = self.frames[self.current_frame % len(self.frames)]
            sys.stdout.write(f"\r{YELLOW}{frame} Waiting for API response ...{RESET}")
            sys.stdout.flush()
            self.current_frame += 1
            time.sleep(0.1)

    def start(self):
        """Start the spinner animation."""
        self.spinning = True
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.start()

    def stop(self):
        """Stop the spinner animation and clear the line."""
        self.spinning = False
        if self.spinner_thread:
            self.spinner_thread.join()
        sys.stdout.write("\r\033[K")  # Clear the line
        sys.stdout.flush()


def pdf_to_base64_images(pdf_path: Path, dpi: int = 150) -> List[str]:
    """
    Convert PDF pages to base64-encoded PNG images.

    Args:
        pdf_path: Path to PDF file
        dpi: Resolution for conversion (default: 150)

    Returns:
        List of base64-encoded PNG images, one per page
    """
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=dpi)

    base64_images = []
    for image in images:
        # Convert PIL Image to base64 PNG
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        base64_img = base64.b64encode(img_bytes).decode("utf-8")
        base64_images.append(base64_img)

    return base64_images


def review_pdf(
    client: OpenAI,
    pdf_path: Path,
    prompt: str,
    schema: Dict[str, Any],
    model: str = MODEL,
) -> tuple[Dict[str, Any], int, int]:
    """
    Send PDF to GPT-4 API and get structured review.

    Returns:
        Tuple of (review_dict, input_tokens, output_tokens)
    """
    # Convert PDF pages to base64 images
    base64_images = pdf_to_base64_images(pdf_path)

    # Prepare the content array with prompt text and all images
    content = [{"type": "text", "text": prompt}]

    # Add each page as an image
    for base64_img in base64_images:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_img}"},
            }
        )

    # Prepare the API request
    messages = [{"role": "user", "content": content}]

    # Start spinner before API request
    spinner = Spinner()
    spinner.start()

    try:
        # Make API request with JSON schema
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "review", "schema": schema, "strict": True},
            },
            max_tokens=4096,
        )
    finally:
        # Stop spinner after API request completes
        spinner.stop()

    # Extract response
    review_text = response.choices[0].message.content
    review_dict = json.loads(review_text)

    # Get token usage
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    return review_dict, input_tokens, output_tokens


def print_review(
    pdf_path: Path,
    review_dict: Dict[str, Any],
    input_tokens: int,
    output_tokens: int,
    elapsed_time: float,
) -> None:
    """Print review with ANSI colored formatting and save to JSON file."""
    # Calculate price
    price = (
        input_tokens * INPUT_PRICE_PER_MILLION_TOKENS / 1_000_000
        + output_tokens * OUTPUT_PRICE_PER_MILLION_TOKENS / 1_000_000
    )
    price = round(price, 2)

    # Add statistics to the JSON at the beginning
    output_dict = {
        "statistics": {
            "num_input_tokens": input_tokens,
            "num_output_tokens": output_tokens,
            "price_dollars": price,
            "time_seconds": round(elapsed_time, 1),
        },
        **review_dict,
    }

    # Pretty-printed JSON
    json_str = json.dumps(output_dict, indent=2, ensure_ascii=False)
    print(json_str)
    print()

    # Write JSON to file
    json_path = pdf_path.with_suffix(".json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json_str)


def main():
    """Main function to process PDF reviews."""
    parser = argparse.ArgumentParser(
        description="Generate structured reviews for academic papers using GPT-4"
    )
    parser.add_argument("pdfs", nargs="+", type=Path, help="PDF files to review")
    parser.add_argument(
        "--prompt",
        type=str,
        default=DEFAULT_PROMPT,
        help="Custom prompt for the review",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=MODEL,
        help=f"OpenAI model to use (default: {MODEL})",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).parent / "schema.json",
        help="JSON schema file for response structure (default: schema.json)",
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    # Initialize OpenAI client (reads API key from OPENAI_API_KEY environment variable)
    client = OpenAI()

    # Load JSON schema
    try:
        with open(args.schema, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except FileNotFoundError:
        print(f"Error: Schema file not found: {args.schema}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in schema file: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate PDF files
    pdf_files = []
    for pdf_path in args.pdfs:
        if not pdf_path.exists():
            print(f"Error: File not found: {pdf_path}", file=sys.stderr)
            sys.exit(1)
        if not pdf_path.suffix.lower() == ".pdf":
            print(f"Error: Not a PDF file: {pdf_path}", file=sys.stderr)
            sys.exit(1)
        pdf_files.append(pdf_path)

    # Process each PDF
    total = len(pdf_files)
    try:
        for index, pdf_path in enumerate(pdf_files, start=1):
            try:
                # Print header before making the request
                print(
                    f"{BLUE}[{index}/{total}] Generating review for paper {pdf_path.name}{RESET}"
                )

                # Track start time
                start_time = time.time()

                review_dict, input_tokens, output_tokens = review_pdf(
                    client=client,
                    pdf_path=pdf_path,
                    prompt=args.prompt,
                    schema=schema,
                    model=args.model,
                )

                # Calculate elapsed time
                elapsed_time = time.time() - start_time

                print_review(
                    pdf_path=pdf_path,
                    review_dict=review_dict,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    elapsed_time=elapsed_time,
                )

            except Exception as e:
                print(f"Error processing {pdf_path}: {e}", file=sys.stderr)
                continue
    except KeyboardInterrupt:
        print()
        print(f"{YELLOW}Ctrl+C pressed, exiting ...{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
