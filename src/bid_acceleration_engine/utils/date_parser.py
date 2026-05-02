"""Date parsing utilities."""

from datetime import date, datetime


def parse_date_string(raw: str) -> date | None:
    """Parse a date string in common government bid formats.

    Supported formats:
    - "March 15, 2026" (Month Day, Year)
    - "2026-03-15" (ISO 8601)
    - "15/03/2026" (DD/MM/YYYY)

    Args:
        raw: Raw date string to parse.

    Returns:
        Parsed date object, or None if parsing fails.
    """
    if not raw or not isinstance(raw, str):
        return None

    raw = raw.strip()
    if not raw:
        return None

    # Try common formats in order
    formats = [
        "%B %d, %Y",  # March 15, 2026
        "%b %d, %Y",  # Mar 15, 2026
        "%Y-%m-%d",   # 2026-03-15 (ISO 8601)
        "%d/%m/%Y",   # 15/03/2026
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(raw, fmt)
            return parsed.date()
        except ValueError:
            continue

    return None
