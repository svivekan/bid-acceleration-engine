"""Text extraction parsers for bid document intake."""

import re
from datetime import datetime

from bid_acceleration_engine.schemas.bid import BidSection
from bid_acceleration_engine.utils.date_parser import parse_date_string


def extract_title(text: str) -> str:
    """Extract the title from bid text (first non-empty line).

    Args:
        text: Raw bid document text.

    Returns:
        The first non-empty line, stripped of whitespace.
    """
    lines = text.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def extract_issuer(text: str) -> str | None:
    """Extract the issuer/contracting authority from bid text.

    Looks for common patterns like "Issued by:", "Contracting Authority:", "Agency:".

    Args:
        text: Raw bid document text.

    Returns:
        The issuer name if found, None otherwise.
    """
    patterns = [
        r"Issued by:\s*(.+?)(?:\n|$)",
        r"Contracting Authority:\s*(.+?)(?:\n|$)",
        r"Agency:\s*(.+?)(?:\n|$)",
        r"Contracting Officer:\s*(.+?)(?:\n|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            issuer = match.group(1).strip()
            if issuer:
                return issuer

    return None


def extract_due_date(text: str) -> datetime | None:
    """Extract the due date from bid text.

    Looks for common patterns like "Closing Date:", "Due:", "Deadline:".
    Then delegates to parse_date_string to parse the date.

    Args:
        text: Raw bid document text.

    Returns:
        Parsed due date as datetime, or None if not found.
    """
    patterns = [
        r"Closing Date:\s*(.+?)(?:\n|$)",
        r"Due:\s*(.+?)(?:\n|$)",
        r"Deadline:\s*(.+?)(?:\n|$)",
        r"Response Deadline:\s*(.+?)(?:\n|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            # Remove time component if present (e.g., "April 15, 2026 at 2 PM")
            date_str = re.sub(r"\s+at\s+.+", "", date_str, flags=re.IGNORECASE)
            date_str = re.sub(r"\s+\d{1,2}:\d{2}.+", "", date_str)

            parsed_date = parse_date_string(date_str)
            if parsed_date:
                # Return as datetime (start of day)
                return datetime.combine(parsed_date, datetime.min.time())

    return None


def count_words(text: str) -> int:
    """Count words in text.

    Args:
        text: Text to count.

    Returns:
        Number of words (split by whitespace).
    """
    return len(text.split())


def extract_sections(text: str) -> list[BidSection]:
    """Extract sections from bid text.

    Identifies sections by:
    - ALL CAPS headings (SECTION, OVERVIEW, etc.)
    - Numbered headings (1., 2., I., A., etc.)

    Args:
        text: Raw bid document text.

    Returns:
        List of BidSection objects in order.
    """
    lines = text.split("\n")
    sections: list[BidSection] = []
    current_heading: str | None = None
    current_body_lines: list[str] = []
    section_order = 0

    heading_pattern = re.compile(r"^([\dIVXLCDMivxlcdm]+\.?\s+|[A-Z\s]+)$")

    for line in lines:
        stripped = line.strip()

        # Check if this line is a heading
        is_heading = (
            # ALL CAPS heading
            (stripped and stripped.isupper() and len(stripped) > 3)
            # Numbered heading (1., 2., I., A., etc.)
            or (stripped and heading_pattern.match(stripped))
        )

        if is_heading:
            # Save previous section if any
            if current_body_lines or current_heading is not None:
                body = "\n".join(current_body_lines).strip()
                sections.append(
                    BidSection(
                        heading=current_heading,
                        body=body,
                        order=section_order,
                    )
                )
                section_order += 1
                current_body_lines = []

            # Start new section
            current_heading = stripped
        else:
            # Add line to current body
            if stripped or current_body_lines:  # Skip leading blank lines
                current_body_lines.append(line.rstrip())

    # Save final section
    if current_body_lines or current_heading is not None:
        body = "\n".join(current_body_lines).strip()
        sections.append(
            BidSection(
                heading=current_heading,
                body=body,
                order=section_order,
            )
        )

    return sections
