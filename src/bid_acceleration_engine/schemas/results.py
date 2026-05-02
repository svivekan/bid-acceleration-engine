"""Agent result wrapper and status enum."""

from datetime import datetime
from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class AgentStatus(StrEnum):
    """Status of an agent execution."""

    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"


class AgentResult(BaseModel, Generic[T]):  # noqa: UP046
    """Typed result wrapper for all agent outputs."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    agent_name: str
    status: AgentStatus
    output: T | None
    error_message: str | None = None
    duration_seconds: float
    produced_at: datetime
