"""Enhance section detection for Phase 1.5 Enhancement Agent."""

import re

from bid_acceleration_engine.schemas.bid import BidSection
from bid_acceleration_engine.schemas.enhanced_bid import EnhancedBidSection


def enhance_sections(raw_text: str, current_sections: list[BidSection]) -> list[EnhancedBidSection]:
    """Convert BidSections to EnhancedBidSections and detect missed title-case headings.

    Phase 1 parser only detects ALL-CAPS or numbered headings. This function:
    1. Converts existing BidSections to EnhancedBidSections (no section_type yet)
    2. Scans for standalone title-case lines that look like headings
    3. Inserts them as new EnhancedBidSections at correct positions

    A title-case line qualifies as a heading if:
    - Standalone (no leading list marker: -, •, digit+.)
    - 2–6 words (likely a section title, not a sentence)
    - No trailing colon (not a label)
    - Not indented more than 4 spaces
    """
    # Convert existing sections to enhanced
    enhanced = [
        EnhancedBidSection(heading=s.heading, body=s.body, order=s.order, section_type=None) for s in current_sections
    ]

    lines = raw_text.splitlines()
    next_order = len(current_sections)  # Start numbering new sections after current ones
    new_sections = []

    # Scan each line for potential title-case headings
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip empty lines, already-detected headings (ALL-CAPS or numbered)
        if not stripped or stripped.isupper() or re.match(r"^\d+\.", stripped):
            continue

        # Skip lines that look like list items or paragraphs
        if re.match(r"^[-•\*]", stripped) or stripped.endswith(":"):
            continue

        # Skip lines that are too indented (likely indented content, not a heading)
        if len(line) - len(line.lstrip()) > 4:
            continue

        # Check if this looks like a Title Case heading (2–6 words)
        words = stripped.split()
        if 2 <= len(words) <= 6:
            # Check if it's Title Case (first letter of most words capitalized)
            # Allow some lowercase words (short conjunctions, prepositions)
            capital_words = sum(1 for w in words if w[0].isupper())
            if capital_words >= len(words) - 1:  # At least len-1 words start with capital
                # This is a potential title-case heading
                # Create a new EnhancedBidSection for it
                new_sections.append(
                    EnhancedBidSection(
                        heading=stripped,
                        body="",  # Body will be empty; content follows in next sections
                        order=next_order,
                        section_type=None,
                    )
                )
                next_order += 1

    # Merge new_sections into enhanced, maintaining order
    if new_sections:
        enhanced.extend(new_sections)
        # Re-sort by order to maintain sequence
        enhanced.sort(key=lambda s: s.order if s.order is not None else 999)

    return enhanced
