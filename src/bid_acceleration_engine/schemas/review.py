"""Review and annotation schema."""

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AnnotationSeverity(StrEnum):
    """Severity level of a review annotation."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class ReviewAnnotation(BaseModel):
    """An annotation flagging a gap or inconsistency."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    bid_id: UUID
    severity: AnnotationSeverity
    category: str
    description: str
    referenced_artifact: str
    suggested_action: str | None
