"""Solution outline schema."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SolutionSection(BaseModel):
    """A section of a solution outline."""

    model_config = ConfigDict(extra="forbid")

    title: str
    narrative: str
    addressed_requirement_ids: list[UUID]


class SolutionOutline(BaseModel):
    """High-level solution approach addressing extracted requirements."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    bid_id: UUID
    sections: list[SolutionSection]
    unaddressed_requirement_ids: list[UUID]
    generated_at: datetime
