"""Extract submission deadline for Phase 1.5 Enhancement Agent."""

import re
from datetime import datetime

from bid_acceleration_engine.utils.date_parser import parse_date_string  # noqa: E402

# Priority ranking for date labels (higher = more likely to be submission deadline)
DATE_LABEL_PRIORITY = {
    "closing date": 10,
    "closing": 9,
    "submission deadline": 10,
    "due date": 8,
    "deadline": 8,
    "response deadline": 8,
    "issue date": 1,
    "posted": 1,
    "published": 1,
    # Explicitly low priority — these are NOT submission dates
    "questions due": -1,
    "question deadline": -1,
}


def extract_submission_deadline(raw_text: str) -> tuple[datetime | None, str | None, float]:
    """Extract submission deadline using label priority ranking.

    Scans all date labels in the text, ranks by priority, and returns the
    highest-priority date found. Strips ordinal suffixes (1st, 2nd, 3rd, 4th)
    before parsing.

    Returns: (date, date_type, confidence)
    - date_type: "submission_deadline" if found; None otherwise
    - confidence: 1.0 for found deadline, 0.0 if no valid date
    """
    lines = raw_text.splitlines()
    best_date = None
    best_priority = -999

    for line in lines:
        # Try to match any known date label
        for label, priority in DATE_LABEL_PRIORITY.items():
            # Case-insensitive, label at start of line followed by colon and content
            # Also try without word boundary to catch label anywhere in the line
            pattern = rf"(?:^|\s){re.escape(label)}:\s*(.+?)(?:\n|$)"
            match = re.search(pattern, line, re.IGNORECASE)
            if match and priority > best_priority:
                date_str = match.group(1).strip()

                # Strip ordinal suffixes (1st, 2nd, 3rd, 4th, etc.)
                date_str = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)

                # Strip time components and UTC/EST/etc. indicators
                # E.g., "15 April, 2026 at 23:59 UTC" becomes "15 April, 2026"
                date_str = re.sub(r"\s+(at|by|@)\s+.*", "", date_str, flags=re.IGNORECASE)

                # Try to parse the date
                parsed = parse_date_string(date_str)
                if parsed:
                    best_date = parsed
                    best_priority = priority

    # If we found any date with positive priority, return it as submission deadline
    if best_date and best_priority > 0:
        date_type = "submission_deadline"
        return best_date, date_type, 1.0

    # If Phase 1 found a date, treat it as submission deadline by default
    # (Phase 1 already uses "Closing Date:" pattern which is high-priority)
    return None, None, 0.0
