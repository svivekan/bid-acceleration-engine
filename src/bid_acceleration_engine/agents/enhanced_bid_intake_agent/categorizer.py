"""Categorize sections and count items for Phase 1.5 Enhancement Agent."""

import re

from bid_acceleration_engine.schemas.enhanced_bid import EnhancedBidSection


def categorize_sections(sections: list[EnhancedBidSection]) -> tuple[list[EnhancedBidSection], int, int]:
    """Tag sections with semantic type and count mandatory/optional items.

    Tags sections based on heading keywords:
    - "MANDATORY" → section_type = "mandatory"
    - "OPTIONAL" → section_type = "optional"
    - "EVALUATION" → section_type = "evaluation"
    - "BACKGROUND", "OVERVIEW", "PURPOSE" → section_type = "background"
    - Others → section_type = None

    Counts bulleted/numbered items within mandatory and optional sections.

    Returns: (tagged_sections, mandatory_count, optional_count)
    """
    mandatory_count = 0
    optional_count = 0

    for section in sections:
        if not section.heading:
            continue

        heading_upper = section.heading.upper()

        # Tag section type
        if "MANDATORY" in heading_upper:
            section.section_type = "mandatory"
        elif "OPTIONAL" in heading_upper:
            section.section_type = "optional"
        elif "EVALUATION" in heading_upper:
            section.section_type = "evaluation"
        elif any(x in heading_upper for x in ["BACKGROUND", "OVERVIEW", "PURPOSE", "INTRODUCTION"]):
            section.section_type = "background"

        # Count items in body (if this is a mandatory/optional section)
        if section.section_type in ("mandatory", "optional"):
            # Count lines that look like list items: numbered, bulleted, dashed
            item_pattern = r"^\s*(?:\d+\.|[-•\*])\s+"
            items = [line for line in section.body.splitlines() if re.match(item_pattern, line)]
            item_count = len(items)

            if section.section_type == "mandatory":
                mandatory_count += item_count
            else:
                optional_count += item_count

    return sections, mandatory_count, optional_count
