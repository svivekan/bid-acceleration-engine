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


# UK-Specific Parser Tests

def test_extract_due_date_uk_format_day_month_year():
    """Test extracting UK format dates (Day Month Year)."""
    text = "Closing Date: 15 May 2026"
    result = extract_due_date(text)
    assert isinstance(result, datetime)
    assert result.date() == date(2026, 5, 15)


def test_extract_due_date_uk_format_with_time():
    """Test extracting UK format dates with time component."""
    text = "Closing Date: 30 April 2026 16:00"
    result = extract_due_date(text)
    assert isinstance(result, datetime)
    assert result.date() == date(2026, 4, 30)


def test_extract_due_date_uk_format_abbreviated_month():
    """Test extracting UK format with abbreviated month name."""
    text = "Closing Date: 10 Mar 2026"
    result = extract_due_date(text)
    assert isinstance(result, datetime)
    assert result.date() == date(2026, 3, 10)


def test_extract_due_date_uk_format_various_months():
    """Test various UK date format month names."""
    test_cases = [
        ("Closing Date: 1 January 2026", date(2026, 1, 1)),
        ("Closing Date: 28 February 2026", date(2026, 2, 28)),
        ("Closing Date: 15 June 2026", date(2026, 6, 15)),
        ("Closing Date: 25 December 2026", date(2026, 12, 25)),
    ]

    for text, expected_date in test_cases:
        result = extract_due_date(text)
        assert isinstance(result, datetime)
        assert result.date() == expected_date, f"Failed for {text}"


def test_extract_issuer_uk_local_authority():
    """Test extracting UK local authority issuer."""
    text = """LOCAL AUTHORITY PROCUREMENT

Contracting Authority: Metropolitan London Borough Council"""
    result = extract_issuer(text)
    assert result == "Metropolitan London Borough Council"


def test_extract_issuer_uk_nhs_trust():
    """Test extracting UK NHS Trust issuer."""
    text = """NHS PROCUREMENT

Contracting Authority: North Regional Health System NHS Trust"""
    result = extract_issuer(text)
    assert result == "North Regional Health System NHS Trust"


def test_extract_issuer_uk_water_authority():
    """Test extracting UK water authority issuer."""
    text = """WATER AUTHORITY PROCUREMENT

Contracting Authority: Thames Valley Water Authority"""
    result = extract_issuer(text)
    assert result == "Thames Valley Water Authority"


def test_extract_issuer_uk_education_consortium():
    """Test extracting UK higher education consortium issuer."""
    text = """HIGHER EDUCATION PROCUREMENT

Contracting Authority: Northern Universities Consortium (8 institutions)"""
    result = extract_issuer(text)
    assert result == "Northern Universities Consortium (8 institutions)"


def test_extract_issuer_with_parenthetical_info():
    """Test extracting issuer that includes parenthetical information."""
    text = "Contracting Authority: Department (Office of Technology)"
    result = extract_issuer(text)
    assert result == "Department (Office of Technology)"


def test_extract_title_uk_procurement_format():
    """Test extracting title from UK procurement document."""
    text = "INTEGRATED COUNCIL DATA ANALYTICS PLATFORM\n\nProcurement Reference: LA-2026-DATA-001"
    result = extract_title(text)
    assert result == "INTEGRATED COUNCIL DATA ANALYTICS PLATFORM"


def test_extract_sections_uk_procurement_structure():
    """Test extracting sections from UK procurement document structure."""
    text = """EXECUTIVE SUMMARY

The project seeks a platform.

PROJECT SCOPE

Data Integration:
- Consolidate data sources
- Support integration

MANDATORY REQUIREMENTS

1. Process data
2. Support users"""

    sections = extract_sections(text)
    headings = [s.heading for s in sections if s.heading]
    assert any("EXECUTIVE SUMMARY" in h for h in headings)
    assert any("PROJECT SCOPE" in h for h in headings)
    assert any("MANDATORY" in h for h in headings)


def test_extract_sections_with_bullets_and_lists():
    """Test that section content with bullets and lists is preserved."""
    text = """SCOPE OF WORK

Data Integration:
- Collect real-time traffic data from sensors
- Integration with 50 state transportation agencies
- Traffic incident reporting from emergency services

REQUIREMENTS

Technical Requirements:
- Distributed stream processing
- Time-series database"""

    sections = extract_sections(text)
    scope_section = next((s for s in sections if s.heading and "SCOPE" in s.heading), None)
    assert scope_section is not None
    assert "Collect real-time traffic" in scope_section.body
    assert "Integration with 50 state" in scope_section.body
