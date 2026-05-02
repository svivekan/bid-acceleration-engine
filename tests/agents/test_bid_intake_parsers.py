"""Tests for bid_intake_agent parsers."""

from datetime import date, datetime

from bid_acceleration_engine.agents.bid_intake_agent.parsers import (
    count_words,
    extract_due_date,
    extract_issuer,
    extract_sections,
    extract_title,
)


def test_extract_title_first_non_empty_line():
    """Test extracting title from first non-empty line."""
    text = "REQUEST FOR PROPOSAL: INFRASTRUCTURE PROJECT\nIssued by: GSA"
    result = extract_title(text)
    assert result == "REQUEST FOR PROPOSAL: INFRASTRUCTURE PROJECT"


def test_extract_title_with_leading_blank_lines():
    """Test that blank lines at the start are skipped."""
    text = "\n\n\nProject Title Here\nMore content"
    result = extract_title(text)
    assert result == "Project Title Here"


def test_extract_title_empty_text():
    """Test with empty text."""
    result = extract_title("")
    assert result == ""


def test_extract_title_whitespace_only():
    """Test with whitespace-only text."""
    result = extract_title("   \n  \n  ")
    assert result == ""


def test_extract_issuer_issued_by_pattern():
    """Test extracting issuer with 'Issued by:' pattern."""
    text = "Title\nIssued by: General Services Administration"
    result = extract_issuer(text)
    assert result == "General Services Administration"


def test_extract_issuer_contracting_authority_pattern():
    """Test extracting issuer with 'Contracting Authority:' pattern."""
    text = "Title\nContracting Authority: Department of Energy"
    result = extract_issuer(text)
    assert result == "Department of Energy"


def test_extract_issuer_agency_pattern():
    """Test extracting issuer with 'Agency:' pattern."""
    text = "Title\nAgency: NASA"
    result = extract_issuer(text)
    assert result == "NASA"


def test_extract_issuer_case_insensitive():
    """Test that issuer extraction is case-insensitive."""
    text = "Title\nISSUED BY: Test Agency"
    result = extract_issuer(text)
    assert result == "Test Agency"


def test_extract_issuer_not_found():
    """Test when issuer is not found."""
    text = "Title\nNo issuer information here"
    result = extract_issuer(text)
    assert result is None


def test_extract_issuer_empty_after_pattern():
    """Test when pattern exists but has only whitespace after colon."""
    text = "Title\nIssued by:   "
    result = extract_issuer(text)
    # With only whitespace, no capture
    assert result is None


def test_extract_due_date_closing_date_pattern():
    """Test extracting due date with 'Closing Date:' pattern."""
    text = "Title\nClosing Date: April 15, 2026"
    result = extract_due_date(text)
    assert isinstance(result, datetime)
    assert result.date() == date(2026, 4, 15)


def test_extract_due_date_due_pattern():
    """Test extracting due date with 'Due:' pattern."""
    text = "Title\nDue: 2026-04-15"
    result = extract_due_date(text)
    assert isinstance(result, datetime)
    assert result.date() == date(2026, 4, 15)


def test_extract_due_date_with_time():
    """Test that time components are stripped."""
    text = "Title\nClosing Date: April 15, 2026 at 2 PM EST"
    result = extract_due_date(text)
    assert isinstance(result, datetime)
    assert result.date() == date(2026, 4, 15)


def test_extract_due_date_case_insensitive():
    """Test that due date extraction is case-insensitive."""
    text = "Title\nCLOSING DATE: March 10, 2026"
    result = extract_due_date(text)
    assert isinstance(result, datetime)
    assert result.date() == date(2026, 3, 10)


def test_extract_due_date_not_found():
    """Test when due date is not found."""
    text = "Title\nNo deadline here"
    result = extract_due_date(text)
    assert result is None


def test_count_words_simple():
    """Test word counting on simple text."""
    text = "This is a test"
    result = count_words(text)
    assert result == 4


def test_count_words_multiline():
    """Test word counting on multiline text."""
    text = "Line one\nLine two\nLine three"
    result = count_words(text)
    assert result == 6


def test_count_words_extra_whitespace():
    """Test that extra whitespace is handled."""
    text = "Word1  \t  Word2    Word3"
    result = count_words(text)
    assert result == 3


def test_count_words_empty():
    """Test word counting on empty text."""
    result = count_words("")
    assert result == 0


def test_extract_sections_all_caps_heading():
    """Test extracting sections with ALL CAPS headings."""
    text = """OVERVIEW
This is the overview section.

REQUIREMENTS
Mandatory requirements here."""

    sections = extract_sections(text)
    assert len(sections) >= 1
    assert any(s.heading and "OVERVIEW" in s.heading for s in sections)
    assert any(s.heading and "REQUIREMENTS" in s.heading for s in sections)


def test_extract_sections_numbered_heading():
    """Test extracting sections with numbered headings."""
    text = """1. INTRODUCTION
First section content.

2. SCOPE
Second section content."""

    sections = extract_sections(text)
    assert len(sections) >= 2


def test_extract_sections_none_heading():
    """Test that sections without headings have heading=None."""
    text = """Just some text without a heading.
More content here."""

    sections = extract_sections(text)
    assert len(sections) >= 1
    assert sections[0].heading is None or sections[0].heading == ""


def test_extract_sections_order():
    """Test that section order is set correctly."""
    text = """FIRST
Content 1

SECOND
Content 2

THIRD
Content 3"""

    sections = extract_sections(text)
    # Filter out empty sections
    non_empty = [s for s in sections if s.body.strip()]
    for i, section in enumerate(non_empty):
        assert section.order == i


def test_extract_sections_with_subheadings():
    """Test sections with various heading formats."""
    text = """I. MAIN SECTION
A. Subsection
Details here.

II. ANOTHER SECTION
More content."""

    sections = extract_sections(text)
    assert len(sections) >= 1


def test_extract_sections_multiline_content():
    """Test that multiline content is preserved."""
    text = """SECTION A
Line 1 of content
Line 2 of content
Line 3 of content

SECTION B
More content"""

    sections = extract_sections(text)
    section_a = next((s for s in sections if s.heading and "SECTION A" in s.heading), None)
    assert section_a is not None
    assert "Line 1" in section_a.body
    assert "Line 3" in section_a.body
