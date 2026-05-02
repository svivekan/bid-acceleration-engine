"""Technical architecture schema."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ArchitectureComponent(BaseModel):
    """A technical component in the proposed architecture."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    technology_choices: list[str]
    interfaces: list[str]


class ArchitectureDraft(BaseModel):
    """Technical architecture for the proposed solution."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    bid_id: UUID
    components: list[ArchitectureComponent]
    integration_notes: str | None
    assumptions: list[str]
    generated_at: datetime
