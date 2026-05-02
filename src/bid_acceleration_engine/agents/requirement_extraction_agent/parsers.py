"""Requirement extraction parsers: extract numbered requirements from bid sections."""

import re
from dataclasses import dataclass

from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedRequirement:
    """Extracted requirement with metadata about its source."""

    text: str
    mandatory: bool
    section_heading: str
    source_location: str | None = None


def detect_mandatory_section(text: str) -> tuple[int, int] | None:
    """Find the start and end position of MANDATORY section.

    Matches: MANDATORY REQUIREMENTS, MANDATORY TECHNICAL SPECS, MANDATORY..., etc.

    Args:
        text: Full document text.

    Returns:
        (start_pos, end_pos) tuple or None if not found.
    """
    pattern = r"(?i)(mandatory\s+[A-Za-z\s]*)"
    match = re.search(pattern, text)
    if not match:
        return None

    start = match.start()
    # Find the end: either the next major section or end of document
    remaining = text[start:]
    next_section = re.search(r"(?i)\n[A-Z][A-Z\s]*\n", remaining[100:])
    if next_section:
        end = start + 100 + next_section.start()
    else:
        end = len(text)

    return (start, end)


def detect_optional_section(text: str) -> tuple[int, int] | None:
    """Find the start and end position of OPTIONAL section.

    Matches: OPTIONAL FEATURES, OPTIONAL ENHANCEMENTS, OPTIONAL..., etc.

    Args:
        text: Full document text.

    Returns:
        (start_pos, end_pos) tuple or None if not found.
    """
    pattern = r"(?i)(optional\s+[A-Za-z\s]*)"
    match = re.search(pattern, text)
    if not match:
        return None

    start = match.start()
    remaining = text[start:]
    next_section = re.search(r"(?i)\n[A-Z][A-Z\s]*\n", remaining[100:])
    if next_section:
        end = start + 100 + next_section.start()
    else:
        end = len(text)

    return (start, end)


def extract_numbered_requirements(section_text: str, section_heading: str, mandatory: bool) -> list[ParsedRequirement]:
    """Extract numbered requirements from a section.

    Handles:
    - Simple numbered items: "1. Requirement text"
    - Bullet-pointed items: "- Requirement text" or "* Requirement text"
    - Multi-line requirements (continue until next number/bullet)
    - Sub-items with letters (1. main, a. sub) treated as one requirement

    Args:
        section_text: Text of the section to extract from.
        section_heading: Name of the section (for source tracking).
        mandatory: Whether requirements in this section are mandatory.

    Returns:
        List of ParsedRequirement objects.
    """
    requirements = []

    lines = section_text.split("\n")
    current_req_id = None
    current_req_lines = []
    current_req_start_line = 0

    for i, line in enumerate(lines):
        # Check if this line starts a numbered requirement (1., 2., 3., etc.)
        numbered_match = re.match(r"^\s*(\d+)\.\s+(.+)", line)
        # Check if this line starts a bullet-pointed requirement (-, *, •, etc.)
        bullet_match = re.match(r"^\s*[-*•]\s+(.+)", line)

        if numbered_match:
            # Save previous requirement if any
            if current_req_id is not None and current_req_lines:
                req_text = "\n".join(current_req_lines).strip()
                if req_text:
                    requirements.append(
                        ParsedRequirement(
                            text=req_text,
                            mandatory=mandatory,
                            section_heading=section_heading,
                            source_location=str(current_req_start_line),
                        )
                    )

            # Start new numbered requirement
            current_req_id = numbered_match.group(1)
            current_req_lines = [numbered_match.group(2)]
            current_req_start_line = i

        elif bullet_match:
            # Save previous requirement if any
            if current_req_id is not None and current_req_lines:
                req_text = "\n".join(current_req_lines).strip()
                if req_text:
                    requirements.append(
                        ParsedRequirement(
                            text=req_text,
                            mandatory=mandatory,
                            section_heading=section_heading,
                            source_location=str(current_req_start_line),
                        )
                    )

            # Start new bullet-pointed requirement
            current_req_id = f"bullet_{i}"
            current_req_lines = [bullet_match.group(1)]
            current_req_start_line = i

        elif current_req_id is not None:
            # Continuation of current requirement
            if line.strip():  # Only add non-empty lines
                current_req_lines.append(line)

    # Don't forget the last requirement
    if current_req_id is not None and current_req_lines:
        req_text = "\n".join(current_req_lines).strip()
        if req_text:
            requirements.append(
                ParsedRequirement(
                    text=req_text,
                    mandatory=mandatory,
                    section_heading=section_heading,
                    source_location=str(current_req_start_line),
                )
            )

    return requirements


def extract_requirements_from_document(raw_text: str) -> list[ParsedRequirement]:
    """Extract all requirements from a document.

    Identifies MANDATORY and OPTIONAL sections, then extracts numbered requirements
    from each section.

    Args:
        raw_text: Full document text.

    Returns:
        List of all parsed requirements.
    """
    all_requirements = []

    # Find mandatory section
    mandatory_range = detect_mandatory_section(raw_text)
    if mandatory_range:
        start, end = mandatory_range
        mandatory_text = raw_text[start:end]
        mandatory_heading = re.search(r"(?i)(mandatory\s+[A-Za-z\s]*)", mandatory_text)
        if mandatory_heading:
            heading_text = mandatory_heading.group(1).strip()
            section_text = mandatory_text[mandatory_heading.end() :]
            reqs = extract_numbered_requirements(section_text, heading_text, mandatory=True)
            all_requirements.extend(reqs)

    # Find optional section
    optional_range = detect_optional_section(raw_text)
    if optional_range:
        start, end = optional_range
        optional_text = raw_text[start:end]
        optional_heading = re.search(r"(?i)(optional\s+[A-Za-z\s]*)", optional_text)
        if optional_heading:
            heading_text = optional_heading.group(1).strip()
            section_text = optional_text[optional_heading.end() :]
            reqs = extract_numbered_requirements(section_text, heading_text, mandatory=False)
            all_requirements.extend(reqs)

    logger.info(f"Extracted {len(all_requirements)} requirements from document")
    return all_requirements
