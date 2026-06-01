"""Integration tests for BidIntakeAgent."""

from datetime import datetime
from pathlib import Path

import pytest

from bid_acceleration_engine.agents.bid_intake_agent.agent import BidIntakeAgent
from bid_acceleration_engine.schemas.bid import BidDocument
from bid_acceleration_engine.schemas.results import AgentStatus


@pytest.fixture
def agent():
    """Create a BidIntakeAgent for testing."""
    return BidIntakeAgent("bid_intake_agent")


@pytest.fixture
def uk_rfp_fixtures():
    """Provide paths to all UK RFP test fixtures."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    return {
        "local_council": fixtures_dir / "uk_local_council_data_analytics.txt",
        "nhs_trust": fixtures_dir / "uk_nhs_trust_population_health.txt",
        "transport": fixtures_dir / "uk_transport_network_data_system.txt",
        "university": fixtures_dir / "uk_university_research_data_repository.txt",
        "water_authority": fixtures_dir / "uk_water_authority_environmental_data.txt",
    }


def test_bid_intake_agent_happy_path(agent, sample_bid_path, tmp_output_dir):
    """Test successful bid intake from sample file."""
    output_path = tmp_output_dir / "output.json"

    result = agent.run(sample_bid_path, output_path)

    # Verify result structure
    assert result.agent_name == "bid_intake_agent"
    assert result.status == AgentStatus.SUCCESS
    assert result.output is not None
    assert result.duration_seconds >= 0.0

    # Verify output is BidDocument
    doc = result.output
    assert isinstance(doc, BidDocument)

    # Verify metadata was extracted
    assert doc.metadata.title != ""
    assert doc.metadata.word_count > 0
    assert doc.metadata.source_file == sample_bid_path
    assert doc.metadata.ingested_at is not None

    # Verify document structure
    assert len(doc.sections) > 0
    assert doc.raw_text == sample_bid_path.read_text(encoding="utf-8")
    assert doc.id is not None

    # Verify JSON output was written
    assert output_path.exists()
    content = output_path.read_text()
    assert doc.metadata.title in content or "title" in content


def test_bid_intake_agent_missing_file(agent, tmp_output_dir):
    """Test that missing file returns FAILURE status."""
    nonexistent_path = Path("/nonexistent/file/path.txt")
    output_path = tmp_output_dir / "output.json"

    result = agent.run(nonexistent_path, output_path)

    assert result.agent_name == "bid_intake_agent"
    assert result.status == AgentStatus.FAILURE
    assert result.output is None
    assert result.error_message is not None
    assert "File not found" in result.error_message


def test_bid_intake_agent_no_overwrite_collision(agent, sample_bid_path, tmp_output_dir):
    """Test that write_json collision is handled (overwrite=False)."""
    output_path = tmp_output_dir / "output.json"

    # First run should succeed
    result1 = agent.run(sample_bid_path, output_path)
    assert result1.status == AgentStatus.SUCCESS
    assert output_path.exists()

    # Second run to same path should fail (no overwrite)
    result2 = agent.run(sample_bid_path, output_path)
    assert result2.status == AgentStatus.FAILURE
    assert "already exists" in result2.error_message.lower() or "exists" in result2.error_message.lower()


def test_bid_intake_agent_extracts_title(agent, sample_bid_path, tmp_output_dir):
    """Test that agent extracts title correctly."""
    output_path = tmp_output_dir / "output.json"

    result = agent.run(sample_bid_path, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output
    # simple_rfp.txt starts with "REQUEST FOR PROPOSAL: ..."
    assert "REQUEST" in doc.metadata.title.upper() or "PROPOSAL" in doc.metadata.title.upper()


def test_bid_intake_agent_extracts_issuer(agent, sample_bid_path, tmp_output_dir):
    """Test that agent extracts issuer correctly."""
    output_path = tmp_output_dir / "output.json"

    result = agent.run(sample_bid_path, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output
    # simple_rfp.txt has "Issued by: General Services Administration"
    assert doc.metadata.issuer is not None
    assert "GSA" in doc.metadata.issuer or "General" in doc.metadata.issuer


def test_bid_intake_agent_extracts_due_date(agent, sample_bid_path, tmp_output_dir):
    """Test that agent extracts due date correctly."""
    output_path = tmp_output_dir / "output.json"

    result = agent.run(sample_bid_path, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output
    # simple_rfp.txt has "Closing Date: April 15, 2026"
    assert doc.metadata.due_date is not None
    assert doc.metadata.due_date.year == 2026
    assert doc.metadata.due_date.month == 4


def test_bid_intake_agent_document_is_json_serializable(agent, sample_bid_path, tmp_output_dir):
    """Test that output document can be read back from JSON."""
    output_path = tmp_output_dir / "output.json"

    result = agent.run(sample_bid_path, output_path)
    assert result.status == AgentStatus.SUCCESS

    # Read JSON back
    json_content = output_path.read_text()
    recovered_doc = BidDocument.model_validate_json(json_content)

    # Verify recovered document matches
    original_doc = result.output
    assert recovered_doc.id == original_doc.id
    assert recovered_doc.metadata.title == original_doc.metadata.title
    assert recovered_doc.metadata.word_count == original_doc.metadata.word_count
    assert len(recovered_doc.sections) == len(original_doc.sections)


def test_bid_intake_agent_sections_have_order(agent, sample_bid_path, tmp_output_dir):
    """Test that extracted sections have proper order values."""
    output_path = tmp_output_dir / "output.json"

    result = agent.run(sample_bid_path, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output

    # Verify section orders are sequential
    for i, section in enumerate(doc.sections):
        assert section.order == i


def test_bid_intake_agent_logs_errors(agent, tmp_output_dir, caplog):
    """Test that agent logs errors appropriately."""
    nonexistent_path = Path("/nonexistent/file.txt")
    output_path = tmp_output_dir / "output.json"

    result = agent.run(nonexistent_path, output_path)

    assert result.status == AgentStatus.FAILURE
    # Check that error was logged
    log_messages = [record.message.lower() for record in caplog.records]
    assert any("error" in msg or "file not found" in msg for msg in log_messages)


def test_bid_intake_agent_marks_duration(agent, sample_bid_path, tmp_output_dir):
    """Test that agent records execution duration."""
    output_path = tmp_output_dir / "output.json"

    result = agent.run(sample_bid_path, output_path)

    assert result.duration_seconds >= 0.0
    # Should be relatively fast for a small document
    assert result.duration_seconds < 10.0


def test_bid_intake_agent_with_minimal_bid(agent, tmp_output_dir):
    """Test agent with minimal RFP (no issuer, no date)."""
    # Create a minimal bid file
    minimal_bid = tmp_output_dir / "minimal.txt"
    minimal_bid.write_text("Minimal Bid\nSome content here")
    output_path = tmp_output_dir / "output.json"

    result = agent.run(minimal_bid, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output
    assert doc.metadata.title == "Minimal Bid"
    assert doc.metadata.issuer is None
    assert doc.metadata.due_date is None
    assert doc.metadata.word_count == 5  # "Minimal", "Bid", "Some", "content", "here"


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
def test_bid_intake_agent_parses_uk_rfps(agent, tmp_output_dir, fixture_name, fixture_path):
    """Test that agent successfully parses all 5 UK RFP fixtures."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    output_path = tmp_output_dir / f"output_{fixture_name}.json"

    # Verify fixture exists
    assert rfp_path.exists(), f"Fixture {fixture_path} not found"

    # Run agent
    result = agent.run(rfp_path, output_path)

    # Verify success
    assert result.status == AgentStatus.SUCCESS, f"Failed to parse {fixture_name}: {result.error_message}"
    assert result.output is not None
    assert isinstance(result.output, BidDocument)

    # Verify basic document properties
    doc = result.output
    assert doc.id is not None
    assert doc.metadata.title != "", f"{fixture_name}: title not extracted"
    assert doc.metadata.word_count > 100, f"{fixture_name}: word count too low"
    assert len(doc.sections) > 0, f"{fixture_name}: no sections extracted"
    assert doc.raw_text != "", f"{fixture_name}: raw text empty"

    # Verify JSON output
    assert output_path.exists(), f"Output JSON not created for {fixture_name}"


@pytest.mark.parametrize(
    "fixture_name,fixture_path,expected_issuer_keyword",
    [
        ("local_council", "uk_local_council_data_analytics.txt", "Metropolitan"),
        ("nhs_trust", "uk_nhs_trust_population_health.txt", "NHS"),
        ("transport", "uk_transport_network_data_system.txt", "Transport"),
        ("university", "uk_university_research_data_repository.txt", "Universities"),
        ("water_authority", "uk_water_authority_environmental_data.txt", "Water"),
    ],
)
def test_bid_intake_agent_extracts_issuer_from_uk_rfps(
    agent, tmp_output_dir, fixture_name, fixture_path, expected_issuer_keyword
):
    """Test that issuer is correctly extracted from UK RFP fixtures."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    output_path = tmp_output_dir / f"output_{fixture_name}.json"

    result = agent.run(rfp_path, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output
    assert doc.metadata.issuer is not None, f"{fixture_name}: issuer not extracted"
    assert expected_issuer_keyword in doc.metadata.issuer, (
        f"{fixture_name}: expected '{expected_issuer_keyword}' in issuer, "
        f"got '{doc.metadata.issuer}'"
    )


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
def test_bid_intake_agent_extracts_dates_from_uk_rfps(agent, tmp_output_dir, fixture_name, fixture_path):
    """Test that closing dates are extracted from UK RFP fixtures."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    output_path = tmp_output_dir / f"output_{fixture_name}.json"

    result = agent.run(rfp_path, output_path)

    assert result.status == AgentStatus.SUCCESS
    doc = result.output
    assert doc.metadata.due_date is not None, f"{fixture_name}: due_date not extracted"
    assert isinstance(doc.metadata.due_date, datetime), f"{fixture_name}: due_date not a datetime"
    assert doc.metadata.due_date.year == 2026, f"{fixture_name}: expected year 2026"


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
def test_bid_intake_agent_uk_rfps_are_json_serializable(agent, tmp_output_dir, fixture_name, fixture_path):
    """Test that parsed UK RFPs can be serialized and deserialized from JSON."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    rfp_path = fixtures_dir / fixture_path
    output_path = tmp_output_dir / f"output_{fixture_name}.json"

    result = agent.run(rfp_path, output_path)
    assert result.status == AgentStatus.SUCCESS

    # Read JSON back and verify round-trip
    json_content = output_path.read_text()
    recovered_doc = BidDocument.model_validate_json(json_content)

    original_doc = result.output
    assert recovered_doc.id == original_doc.id
    assert recovered_doc.metadata.title == original_doc.metadata.title
    assert recovered_doc.metadata.issuer == original_doc.metadata.issuer
    assert recovered_doc.metadata.due_date == original_doc.metadata.due_date
    assert len(recovered_doc.sections) == len(original_doc.sections)


def test_bid_intake_agent_processes_pdf_document(agent, tmp_output_dir):
    """Test that Phase 1.5 successfully processes PDF documents."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    pdf_path = fixtures_dir / "test_rfp_document.pdf"
    output_path = tmp_output_dir / "output_pdf.json"

    # Verify fixture exists
    assert pdf_path.exists(), "PDF test fixture not found"

    # Run agent
    result = agent.run(pdf_path, output_path)

    # Verify success
    assert result.status == AgentStatus.SUCCESS
    assert result.output is not None
    assert isinstance(result.output, BidDocument)

    # Verify metadata extraction
    doc = result.output
    assert doc.metadata.title != ""
    assert doc.metadata.word_count > 0
    assert doc.metadata.source_file == pdf_path
    assert doc.metadata.ingested_at is not None

    # Verify sections extracted
    assert len(doc.sections) > 0
    assert doc.raw_text != ""

    # Verify JSON serialization
    assert output_path.exists()
    recovered_doc = BidDocument.model_validate_json(output_path.read_text())
    assert recovered_doc.id == doc.id


def test_bid_intake_agent_processes_docx_document(agent, tmp_output_dir):
    """Test that Phase 1.5 successfully processes DOCX documents."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    docx_path = fixtures_dir / "test_rfp_document.docx"
    output_path = tmp_output_dir / "output_docx.json"

    # Verify fixture exists
    assert docx_path.exists(), "DOCX test fixture not found"

    # Run agent
    result = agent.run(docx_path, output_path)

    # Verify success
    assert result.status == AgentStatus.SUCCESS
    assert result.output is not None
    assert isinstance(result.output, BidDocument)

    # Verify metadata extraction
    doc = result.output
    assert doc.metadata.title != ""
    assert doc.metadata.word_count > 0
    assert doc.metadata.source_file == docx_path
    assert doc.metadata.ingested_at is not None

    # Verify sections extracted
    assert len(doc.sections) > 0
    assert doc.raw_text != ""

    # Verify JSON serialization
    assert output_path.exists()
    recovered_doc = BidDocument.model_validate_json(output_path.read_text())
    assert recovered_doc.id == doc.id


def test_bid_intake_agent_handles_unsupported_format(agent, tmp_output_dir):
    """Test that agent handles unsupported file formats gracefully."""
    # Create an unsupported file
    unsupported_path = tmp_output_dir / "document.xlsx"
    unsupported_path.write_text("This is not a valid format")
    output_path = tmp_output_dir / "output.json"

    result = agent.run(unsupported_path, output_path)

    assert result.status == AgentStatus.FAILURE
    assert result.output is None
    assert result.error_message is not None
    assert "Unsupported" in result.error_message or "format" in result.error_message
