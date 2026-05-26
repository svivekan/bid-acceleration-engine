"""Extract accurate RFP titles for Phase 1.5 Enhancement Agent."""

import re


def extract_enhanced_title(raw_text: str, current_title: str) -> tuple[str, str, float]:
    """Extract title from RFP, with phase 1.5 improvements.

    Handles two cases:
    1. UK RFPs: Look for "Solicitation Title:" field (line 3)
    2. US RFPs: Strip "REQUEST FOR PROPOSAL:" or "RFP -" prefix from first line

    Returns: (title, source, confidence)
    - source: "solicitation_title_field" | "first_line"
    - confidence: 0.99 for explicit field, 0.85 for cleaned first-line title
    """
    lines = raw_text.splitlines()

    # Check first 10 lines for explicit "Solicitation Title:" field (UK RFPs)
    for line in lines[:10]:
        match = re.match(r"^Solicitation Title:\s*(.+)", line.strip(), re.IGNORECASE)
        if match:
            extracted_title = match.group(1).strip()
            return extracted_title, "solicitation_title_field", 0.99

    # Try stripping known RFP prefixes (US RFPs)
    prefixes = ["REQUEST FOR PROPOSAL:", "RFP -", "RFP:"]
    for prefix in prefixes:
        if current_title.upper().startswith(prefix.upper()):
            cleaned = current_title[len(prefix) :].strip(" -").strip()
            return cleaned, "first_line", 0.85

    # No improvement found; return current title
    return current_title, "first_line", 0.85
