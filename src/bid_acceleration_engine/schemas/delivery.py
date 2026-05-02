"""Delivery plan schema."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Milestone(BaseModel):
    """A milestone in the delivery plan."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    target_date: date | None
    dependencies: list[str]


class DeliveryPlan(BaseModel):
    """Phased delivery timeline and milestones."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    bid_id: UUID
    milestones: list[Milestone]
    overall_timeline_weeks: int | None
    risks: list[str]
    generated_at: datetime
