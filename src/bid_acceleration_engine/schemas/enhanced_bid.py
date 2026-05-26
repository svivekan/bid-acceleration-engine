"""Enhanced Bid schemas with confidence scores and categorization.

Phase 1.5 Enhancement Agent produces EnhancedBidDocument, which extends BidDocument
with title source/confidence, date type/confidence, issuer confidence, requirement
categorization counts, and a log of corrections applied.
"""

from pydantic import ConfigDict

from bid_acceleration_engine.schemas.bid import BidDocument, BidMetadata, BidSection


class EnhancedBidSection(BidSection):
    """BidSection with semantic categorization."""

    model_config = ConfigDict(extra="forbid")

    section_type: str | None = None  # "mandatory", "optional", "evaluation", "background", etc.


class EnhancedBidMetadata(BidMetadata):
    """BidMetadata with Phase 1.5 enhancements and confidence scores."""

    model_config = ConfigDict(extra="forbid")

    title_source: str = "first_line"  # "solicitation_title_field" | "first_line" | "inferred"
    title_confidence: float = 1.0  # 0.0-1.0
    due_date_type: str | None = None  # "submission_deadline" | "questions_due" | None
    due_date_confidence: float = 1.0  # 0.0-1.0
    issuer_confidence: float = 1.0  # 0.0-1.0, lower if compound name with parentheticals
    mandatory_count: int | None = None  # item count in MANDATORY sections
    optional_count: int | None = None  # item count in OPTIONAL sections


class EnhancedBidDocument(BidDocument):
    """BidDocument enriched by Phase 1.5 Enhancement Agent.

    This is a strict subclass of BidDocument with enhanced metadata and sections.
    Downstream agents (Phase 2+) accept this transparently as BidDocument.
    """

    model_config = ConfigDict(extra="forbid")

    metadata: EnhancedBidMetadata  # overrides BidDocument.metadata type
    sections: list[EnhancedBidSection]  # overrides BidDocument.sections type
    corrections_applied: list[str] = []  # human-readable log of what was enhanced
