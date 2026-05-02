"""Bid document schema and related models."""

from datetime import datetime
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BidSection(BaseModel):
    """A section within a bid document."""

    model_config = ConfigDict(extra="forbid")

    heading: str | None
    body: str
    order: int


class BidMetadata(BaseModel):
    """Metadata extracted from a bid document."""

    model_config = ConfigDict(extra="forbid")

    title: str
    issuer: str | None
    due_date: datetime | None
    word_count: int
    source_file: Path
    ingested_at: datetime


class BidDocument(BaseModel):
    """Complete bid document with extracted metadata and sections."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    metadata: BidMetadata
    raw_text: str
    sections: list[BidSection]
