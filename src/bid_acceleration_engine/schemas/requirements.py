"""Extracted requirements schema."""

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RequirementCategory(StrEnum):
    """Category of a requirement."""

    TECHNICAL = "Technical"
    SECURITY = "Security"
    COMPLIANCE = "Compliance"
    PERFORMANCE = "Performance"


class RequirementPriority(StrEnum):
    """Priority level of a requirement."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class EstimatedComplexity(StrEnum):
    """Complexity estimate for implementing a requirement."""

    SIMPLE = "Simple"
    MODERATE = "Moderate"
    COMPLEX = "Complex"


class ExtractedRequirement(BaseModel):
    """A single requirement extracted from a bid document."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    source_text: str
    category: RequirementCategory
    priority: RequirementPriority
    estimated_complexity: EstimatedComplexity
    mandatory: bool
    section_heading: str
    source_location: str | None = None
