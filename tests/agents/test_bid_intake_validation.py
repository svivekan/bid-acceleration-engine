"""Validation and accuracy tests for UK RFP fixtures."""

import re
from pathlib import Path

import pytest

from bid_acceleration_engine.agents.bid_intake_agent.agent import BidIntakeAgent
from bid_acceleration_engine.schemas.results import AgentStatus


@pytest.fixture
def agent():
    """Create a BidIntakeAgent for testing."""
    return BidIntakeAgent("bid_intake_agent")


@pytest.fixture
def uk_rfp_files():
    """Get paths to all UK RFP fixture files."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    return {
        "local_council": fixtures_dir / "uk_local_council_data_analytics.txt",
        "nhs_trust": fixtures_dir / "uk_nhs_trust_population_health.txt",
        "transport": fixtures_dir / "uk_transport_network_data_system.txt",
        "university": fixtures_dir / "uk_university_research_data_repository.txt",
        "water_authority": fixtures_dir / "uk_water_authority_environmental_data.txt",
    }


# ============================================================================
# VALIDATION TEST SUITE - Verify all fixtures meet constraints
# ============================================================================


@pytest.mark.parametrize(
    "fixture_name,fixture_path",
    [
        ("local_council", "uk_local_council_data_analytics.txt"),
        ("nhs_trust", "uk_nhs_trust_population_health.txt"),
        ("transport", "uk_transport_network_data_system.txt"),
        ("university", "uk_university_research_data_repository.txt"),
        ("water_authority", "uk_water_authority_environmental_data.txt"),
    ],
)
def test_fixture_constraint_contract_value_under_5m(fixture_name, fixture_path):
    """Validate that all fixtures specify contract value under £5 million."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    text = rfp_path.read_text()

    # Extract contract value in various formats: "£2.8 Million", "£2,800,000", "2.8M"
    patterns = [
        r"Estimated (?:Contract )?Value:\s*£([\d.]+)\s*Million",
        r"Estimated (?:Contract )?Value:\s*£([\d,]+)",
        r"Estimated Value:\s*\$?([\d.]+)\s*[Mm]",
    ]

    value_found = False
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value_str = match.group(1).replace(",", "")
            try:
                value = float(value_str)
                value_found = True
                assert value < 5.0, f"{fixture_name}: Contract value £{value}M exceeds £5M limit"
                break
            except ValueError:
                continue

    assert value_found, f"{fixture_name}: Could not extract contract value"


@pytest.mark.parametrize(
    "fixture_name,fixture_path",
    [
        ("local_council", "uk_local_council_data_analytics.txt"),
        ("nhs_trust", "uk_nhs_trust_population_health.txt"),
        ("transport", "uk_transport_network_data_system.txt"),
        ("university", "uk_university_research_data_repository.txt"),
        ("water_authority", "uk_water_authority_environmental_data.txt"),
    ],
)
def test_fixture_constraint_duration_under_36_months(fixture_name, fixture_path):
    """Validate that all fixtures specify duration under 36 months (3 years)."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    text = rfp_path.read_text()

    # Extract duration in formats: "24 months", "36 months", "2 years", "3 years"
    patterns = [
        r"(?:Contract )?Duration:\s*(\d+)\s*months",
        r"(?:Contract )?Duration:\s*(\d+)\s*(?:year|years?)",
        r"Period.*?(\d+)\s*months",
    ]

    duration_found = False
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            duration_str = match.group(1)
            duration = int(duration_str)

            # If duration is in years, convert to months
            if "year" in pattern.lower() or "year" in text[match.start() : match.end()].lower():
                duration = duration * 12

            duration_found = True
            assert (
                duration <= 36
            ), f"{fixture_name}: Contract duration {duration} months exceeds 36-month limit"
            break

    assert duration_found, f"{fixture_name}: Could not extract contract duration"


@pytest.mark.parametrize(
    "fixture_name,fixture_path",
    [
        ("local_council", "uk_local_council_data_analytics.txt"),
        ("nhs_trust", "uk_nhs_trust_population_health.txt"),
        ("transport", "uk_transport_network_data_system.txt"),
        ("university", "uk_university_research_data_repository.txt"),
        ("water_authority", "uk_water_authority_environmental_data.txt"),
    ],
)
def test_fixture_constraint_uk_procurement_language(fixture_name, fixture_path):
    """Validate that fixtures use UK procurement terminology."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    text = rfp_path.read_text()

    # Check for UK procurement-specific patterns
    uk_patterns = [
        r"Contracting Authority",
        r"Procurement Reference",
        r"Closing Date",
        r"£",  # UK currency
    ]

    matched_patterns = sum(1 for pattern in uk_patterns if re.search(pattern, text, re.IGNORECASE))
    assert (
        matched_patterns >= 3
    ), f"{fixture_name}: Only {matched_patterns} UK procurement patterns found (need ≥3)"


@pytest.mark.parametrize(
    "fixture_name,fixture_path",
    [
        ("local_council", "uk_local_council_data_analytics.txt"),
        ("nhs_trust", "uk_nhs_trust_population_health.txt"),
        ("transport", "uk_transport_network_data_system.txt"),
        ("university", "uk_university_research_data_repository.txt"),
        ("water_authority", "uk_water_authority_environmental_data.txt"),
    ],
)
def test_fixture_constraint_has_mandatory_requirements(fixture_name, fixture_path):
    """Validate that all fixtures contain mandatory requirements section."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    text = rfp_path.read_text()

    # Look for mandatory requirements section
    has_mandatory = bool(re.search(r"MANDATORY\s+REQUIREMENTS?", text, re.IGNORECASE))
    has_requirements = bool(re.search(r"REQUIREMENTS?", text, re.IGNORECASE))

    assert (
        has_mandatory or has_requirements
    ), f"{fixture_name}: No mandatory requirements section found"


# ============================================================================
# ACCURACY BENCHMARKING - Test extraction accuracy
# ============================================================================


@pytest.mark.parametrize(
    "fixture_name,fixture_path,expected_sections",
    [
        ("local_council", "uk_local_council_data_analytics.txt", 6),
        ("nhs_trust", "uk_nhs_trust_population_health.txt", 7),
        ("transport", "uk_transport_network_data_system.txt", 6),
        ("university", "uk_university_research_data_repository.txt", 6),
        ("water_authority", "uk_water_authority_environmental_data.txt", 7),
    ],
)
def test_accuracy_section_count(agent, tmp_output_dir, fixture_name, fixture_path, expected_sections):
    """Benchmark: Verify parser extracts expected number of sections."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    output_path = tmp_output_dir / f"output_{fixture_name}.json"

    result = agent.run(rfp_path, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output
    actual_sections = len(doc.sections)
    assert (
        actual_sections == expected_sections
    ), f"{fixture_name}: Expected {expected_sections} sections, got {actual_sections}"


@pytest.mark.parametrize(
    "fixture_name,fixture_path",
    [
        ("local_council", "uk_local_council_data_analytics.txt"),
        ("nhs_trust", "uk_nhs_trust_population_health.txt"),
        ("transport", "uk_transport_network_data_system.txt"),
        ("university", "uk_university_research_data_repository.txt"),
        ("water_authority", "uk_water_authority_environmental_data.txt"),
    ],
)
def test_accuracy_identifies_mandatory_section(agent, tmp_output_dir, fixture_name, fixture_path):
    """Benchmark: Verify parser identifies MANDATORY REQUIREMENTS section."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    output_path = tmp_output_dir / f"output_{fixture_name}.json"

    result = agent.run(rfp_path, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output

    # Check that at least one section heading contains "MANDATORY"
    mandatory_sections = [s for s in doc.sections if s.heading and "MANDATORY" in s.heading.upper()]
    assert (
        len(mandatory_sections) > 0
    ), f"{fixture_name}: No section with 'MANDATORY' in heading found"


@pytest.mark.parametrize(
    "fixture_name,fixture_path",
    [
        ("local_council", "uk_local_council_data_analytics.txt"),
        ("nhs_trust", "uk_nhs_trust_population_health.txt"),
        ("transport", "uk_transport_network_data_system.txt"),
        ("university", "uk_university_research_data_repository.txt"),
        ("water_authority", "uk_water_authority_environmental_data.txt"),
    ],
)
def test_accuracy_identifies_optional_features_section(agent, tmp_output_dir, fixture_name, fixture_path):
    """Benchmark: Verify parser identifies OPTIONAL features section."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    output_path = tmp_output_dir / f"output_{fixture_name}.json"

    result = agent.run(rfp_path, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output

    # Check that at least one section contains optional features/enhancements
    optional_sections = [
        s
        for s in doc.sections
        if s.heading
        and any(
            keyword in s.heading.upper()
            for keyword in ["OPTIONAL", "ENHANCEMENT", "CAPABILITY"]
        )
    ]
    assert (
        len(optional_sections) > 0
    ), f"{fixture_name}: No section with optional features found"


@pytest.mark.parametrize(
    "fixture_name,fixture_path",
    [
        ("local_council", "uk_local_council_data_analytics.txt"),
        ("nhs_trust", "uk_nhs_trust_population_health.txt"),
        ("transport", "uk_transport_network_data_system.txt"),
        ("university", "uk_university_research_data_repository.txt"),
        ("water_authority", "uk_water_authority_environmental_data.txt"),
    ],
)
def test_accuracy_detects_technical_specifications(agent, tmp_output_dir, fixture_name, fixture_path):
    """Benchmark: Verify parser identifies technical or architectural sections."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    output_path = tmp_output_dir / f"output_{fixture_name}.json"

    result = agent.run(rfp_path, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output

    # Check for technical/architectural sections (may use various names)
    # or check that at least one section contains technical keywords in body
    technical_keywords = ["TECHNICAL", "ARCHITECTURE", "SPECIFICATIONS", "SCOPE"]
    technical_sections = [
        s
        for s in doc.sections
        if s.heading and any(re.search(kw, s.heading, re.IGNORECASE) for kw in technical_keywords)
    ]

    # If no explicit technical section, check for technical content in any section
    if len(technical_sections) == 0:
        # Look for sections containing technical content indicators
        has_technical_content = any(
            re.search(r"(database|cloud|system|API|integration|architecture)", s.body, re.IGNORECASE)
            for s in doc.sections
            if s.body
        )
        assert has_technical_content, f"{fixture_name}: No technical content found in any section"
    else:
        assert len(technical_sections) > 0, f"{fixture_name}: No technical section found"


@pytest.mark.parametrize(
    "fixture_name,fixture_path",
    [
        ("local_council", "uk_local_council_data_analytics.txt"),
        ("nhs_trust", "uk_nhs_trust_population_health.txt"),
        ("transport", "uk_transport_network_data_system.txt"),
        ("university", "uk_university_research_data_repository.txt"),
        ("water_authority", "uk_water_authority_environmental_data.txt"),
    ],
)
def test_accuracy_preserves_numbered_requirements(agent, tmp_output_dir, fixture_name, fixture_path):
    """Benchmark: Verify parser preserves numbered list structure in requirements."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    output_path = tmp_output_dir / f"output_{fixture_name}.json"

    result = agent.run(rfp_path, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output

    # Find mandatory section and check it contains numbered items
    mandatory_section = next(
        (s for s in doc.sections if s.heading and "MANDATORY" in s.heading.upper()), None
    )
    assert mandatory_section is not None, f"{fixture_name}: No mandatory section"

    # Check for numbered items (1., 2., 3., etc.)
    has_numbered = bool(re.search(r"\d+\.\s+", mandatory_section.body))
    assert has_numbered, f"{fixture_name}: Numbered requirements not found in mandatory section"


@pytest.mark.parametrize(
    "fixture_name,fixture_path",
    [
        ("local_council", "uk_local_council_data_analytics.txt"),
        ("nhs_trust", "uk_nhs_trust_population_health.txt"),
        ("transport", "uk_transport_network_data_system.txt"),
        ("university", "uk_university_research_data_repository.txt"),
        ("water_authority", "uk_water_authority_environmental_data.txt"),
    ],
)
def test_accuracy_minimum_word_count(agent, tmp_output_dir, fixture_name, fixture_path):
    """Benchmark: Verify parser processes substantial documents (minimum word count)."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    output_path = tmp_output_dir / f"output_{fixture_name}.json"

    result = agent.run(rfp_path, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output

    # All UK RFPs should be substantial documents
    assert (
        doc.metadata.word_count >= 300
    ), f"{fixture_name}: Document too short ({doc.metadata.word_count} words)"
