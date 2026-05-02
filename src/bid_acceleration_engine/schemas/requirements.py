"""Extracted requirements schema."""

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RequirementType(StrEnum):
    """Classification of a requirement."""

    MANDATORY = "mandatory"
    OPTIONAL = "optional"
    INFORMATIONAL = "informational"


class ExtractedRequirement(BaseModel):
    """A single requirement extracted from a bid document."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    bid_id: UUID
    requirement_type: RequirementType
    raw_text: str
    section_reference: str | None
    keywords: list[str]
