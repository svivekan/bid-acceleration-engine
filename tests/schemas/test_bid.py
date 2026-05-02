"""Tests for BidDocument and related schemas."""

import json
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from bid_acceleration_engine.schemas.bid import (
    BidDocument,
    BidMetadata,
    BidSection,
)


@pytest.fixture
def sample_metadata():
    """Sample BidMetadata for testing."""
    now = datetime.now()
    return BidMetadata(
        title="Test RFP",
        issuer="Test Agency",
        due_date=now,
        word_count=500,
        source_file=Path("/tmp/test.txt"),
        ingested_at=now,
    )


@pytest.fixture
def sample_sections():
    """Sample BidSection list for testing."""
    return [
        BidSection(heading="Introduction", body="This is the introduction.", order=1),
        BidSection(heading="Requirements", body="Mandatory requirements here.", order=2),
        BidSection(heading=None, body="Additional notes.", order=3),
    ]


def test_bid_section_with_heading(sample_sections):
    """Test BidSection with a heading."""
    section = sample_sections[0]
    assert section.heading == "Introduction"
    assert section.body == "This is the introduction."
    assert section.order == 1


def test_bid_section_without_heading(sample_sections):
    """Test BidSection with heading=None."""
    section = sample_sections[2]
    assert section.heading is None
    assert section.body == "Additional notes."
    assert section.order == 3


def test_bid_metadata_full(sample_metadata):
    """Test BidMetadata with all fields populated."""
    assert sample_metadata.title == "Test RFP"
    assert sample_metadata.issuer == "Test Agency"
    assert sample_metadata.word_count == 500
    assert isinstance(sample_metadata.due_date, datetime)


def test_bid_metadata_nullable_fields():
    """Test BidMetadata with nullable fields."""
    now = datetime.now()
    metadata = BidMetadata(
        title="Minimal RFP",
        issuer=None,
        due_date=None,
        word_count=100,
        source_file=Path("/tmp/minimal.txt"),
        ingested_at=now,
    )

    assert metadata.title == "Minimal RFP"
    assert metadata.issuer is None
    assert metadata.due_date is None


def test_bid_document_full(sample_metadata, sample_sections):
    """Test BidDocument with complete data."""
    doc_id = uuid4()
    doc = BidDocument(
        id=doc_id,
        metadata=sample_metadata,
        raw_text="Full bid text here.\nWith multiple lines.",
        sections=sample_sections,
    )

    assert doc.id == doc_id
    assert isinstance(doc.id, UUID)
    assert doc.metadata.title == "Test RFP"
    assert len(doc.sections) == 3
    assert doc.sections[0].order == 1


def test_bid_document_model_dump(sample_metadata, sample_sections):
    """Test BidDocument serialization via model_dump."""
    doc = BidDocument(
        id=uuid4(),
        metadata=sample_metadata,
        raw_text="Test content",
        sections=sample_sections,
    )

    dumped = doc.model_dump()
    assert "id" in dumped
    assert "metadata" in dumped
    assert "raw_text" in dumped
    assert "sections" in dumped
    assert len(dumped["sections"]) == 3


def test_bid_document_json_serializable(sample_metadata, sample_sections):
    """Test that BidDocument can be serialized to JSON."""
    doc = BidDocument(
        id=uuid4(),
        metadata=sample_metadata,
        raw_text="Test content",
        sections=sample_sections,
    )

    # Serialize to JSON mode (converts UUID and datetime to strings)
    dumped = doc.model_dump(mode="json")
    json_str = json.dumps(dumped)

    # Verify it's valid JSON
    parsed = json.loads(json_str)
    assert parsed["metadata"]["title"] == "Test RFP"
    assert isinstance(parsed["id"], str)  # UUID as string
    assert isinstance(parsed["metadata"]["ingested_at"], str)  # datetime as ISO 8601


def test_bid_document_rejects_extra_fields(sample_metadata, sample_sections):
    """Test that BidDocument forbids extra fields (extra='forbid')."""
    with pytest.raises(ValidationError) as exc_info:
        BidDocument(
            id=uuid4(),
            metadata=sample_metadata,
            raw_text="Test",
            sections=sample_sections,
            extra_field="not allowed",  # Should raise
        )

    assert "extra_forbidden" in str(exc_info.value).lower()


def test_bid_section_rejects_extra_fields():
    """Test that BidSection forbids extra fields."""
    with pytest.raises(ValidationError) as exc_info:
        BidSection(
            heading="Test",
            body="Body",
            order=1,
            invalid_field="not allowed",  # Should raise
        )

    assert "extra_forbidden" in str(exc_info.value).lower()


def test_bid_metadata_rejects_extra_fields():
    """Test that BidMetadata forbids extra fields."""
    with pytest.raises(ValidationError) as exc_info:
        BidMetadata(
            title="Test",
            issuer=None,
            due_date=None,
            word_count=100,
            source_file=Path("/tmp/test.txt"),
            ingested_at=datetime.now(),
            invalid_field="not allowed",  # Should raise
        )

    assert "extra_forbidden" in str(exc_info.value).lower()


def test_bid_document_empty_sections(sample_metadata):
    """Test BidDocument with empty sections list."""
    doc = BidDocument(
        id=uuid4(),
        metadata=sample_metadata,
        raw_text="No sections",
        sections=[],
    )

    assert len(doc.sections) == 0


def test_bid_document_preserves_word_count(sample_metadata, sample_sections):
    """Test that BidDocument preserves the word count from metadata."""
    doc = BidDocument(
        id=uuid4(),
        metadata=sample_metadata,
        raw_text="Any raw text content",
        sections=sample_sections,
    )

    assert doc.metadata.word_count == 500  # From sample_metadata fixture


def test_bid_section_order_validation(sample_metadata):
    """Test BidSection with various order values."""
    sections = [
        BidSection(heading="First", body="Content", order=0),
        BidSection(heading="Second", body="Content", order=1),
        BidSection(heading="Third", body="Content", order=99),
    ]

    doc = BidDocument(
        id=uuid4(),
        metadata=sample_metadata,
        raw_text="Test",
        sections=sections,
    )

    assert doc.sections[0].order == 0
    assert doc.sections[1].order == 1
    assert doc.sections[2].order == 99
