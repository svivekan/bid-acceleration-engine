"""Integration tests for BidIntakeAgent."""

from pathlib import Path

import pytest

from bid_acceleration_engine.agents.bid_intake_agent.agent import BidIntakeAgent
from bid_acceleration_engine.schemas.bid import BidDocument
from bid_acceleration_engine.schemas.results import AgentStatus


@pytest.fixture
def agent():
    """Create a BidIntakeAgent for testing."""
    return BidIntakeAgent("bid_intake_agent")


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
