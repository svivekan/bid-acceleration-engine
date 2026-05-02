"""Tests for date_parser utility."""

from datetime import date

from bid_acceleration_engine.utils.date_parser import parse_date_string


def test_parse_month_day_year_format():
    """Test parsing 'Month Day, Year' format (e.g., 'March 15, 2026')."""
    result = parse_date_string("March 15, 2026")
    assert result == date(2026, 3, 15)


def test_parse_month_abbrev_day_year_format():
    """Test parsing abbreviated month format (e.g., 'Mar 15, 2026')."""
    result = parse_date_string("Mar 15, 2026")
    assert result == date(2026, 3, 15)


def test_parse_iso8601_format():
    """Test parsing ISO 8601 format (e.g., '2026-03-15')."""
    result = parse_date_string("2026-03-15")
    assert result == date(2026, 3, 15)


def test_parse_dmy_format():
    """Test parsing DD/MM/YYYY format (e.g., '15/03/2026')."""
    result = parse_date_string("15/03/2026")
    assert result == date(2026, 3, 15)


def test_parse_with_leading_trailing_whitespace():
    """Test that leading/trailing whitespace is handled."""
    result = parse_date_string("  March 15, 2026  ")
    assert result == date(2026, 3, 15)


def test_parse_invalid_string_returns_none():
    """Test that invalid date strings return None."""
    result = parse_date_string("not a date")
    assert result is None


def test_parse_empty_string_returns_none():
    """Test that empty string returns None."""
    result = parse_date_string("")
    assert result is None


def test_parse_whitespace_only_returns_none():
    """Test that whitespace-only string returns None."""
    result = parse_date_string("   ")
    assert result is None


def test_parse_none_returns_none():
    """Test that None input returns None."""
    result = parse_date_string(None)  # type: ignore
    assert result is None


def test_parse_various_months():
    """Test parsing various month names."""
    test_cases = [
        ("January 1, 2026", date(2026, 1, 1)),
        ("February 28, 2026", date(2026, 2, 28)),
        ("April 30, 2026", date(2026, 4, 30)),
        ("December 31, 2026", date(2026, 12, 31)),
    ]

    for input_str, expected in test_cases:
        result = parse_date_string(input_str)
        assert result == expected, f"Failed for {input_str}"


def test_parse_single_digit_day():
    """Test parsing dates with single-digit days."""
    result = parse_date_string("March 5, 2026")
    assert result == date(2026, 3, 5)


def test_parse_leap_year():
    """Test parsing leap year date."""
    result = parse_date_string("2024-02-29")
    assert result == date(2024, 2, 29)


def test_parse_uk_format_day_month_year():
    """Test parsing UK format 'Day Month Year' (e.g., '15 May 2026')."""
    result = parse_date_string("15 May 2026")
    assert result == date(2026, 5, 15)


def test_parse_uk_format_abbreviated_month():
    """Test parsing UK format with abbreviated month (e.g., '15 May 2026')."""
    result = parse_date_string("10 January 2026")
    assert result == date(2026, 1, 10)


def test_parse_uk_format_various_months():
    """Test parsing UK format with various months."""
    test_cases = [
        ("1 March 2026", date(2026, 3, 1)),
        ("30 April 2026", date(2026, 4, 30)),
        ("25 December 2026", date(2026, 12, 25)),
        ("2 July 2026", date(2026, 7, 2)),
    ]

    for input_str, expected in test_cases:
        result = parse_date_string(input_str)
        assert result == expected, f"Failed for {input_str}"
