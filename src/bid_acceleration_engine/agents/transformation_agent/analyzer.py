"""Complexity scoring and analysis for transformation architecture."""

from bid_acceleration_engine.agents.transformation_agent import detector
from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


def calculate_complexity_score(
    is_streaming: bool,
    source_count: int,
    detected_freshness: str | None,
    requirements: list[ExtractedRequirement],
) -> int:
    """Calculate transformation complexity score.

    Scoring:
      is_streaming:                +2
      source_count >= 8:           +2
      has_ml_complexity:           +2
      has_governance requirements: +1
      has_pii:                     +1

    Decision:
      Score 0–1  → FABRIC_PIPELINE
      Score 2–3  → DATA_FACTORY_DATAFLOW
      Score 4+   → DATABRICKS (if batch) or STREAM_ANALYTICS (if streaming)

    Args:
        is_streaming: Whether ingestion is streaming (from Phase 3).
        source_count: Number of data sources (from Phase 3).
        detected_freshness: Freshness requirement (from Phase 3).
        requirements: List of extracted requirements.

    Returns:
        Complexity score (integer).
    """
    score = 0

    if is_streaming:
        score += 2
        logger.debug("Streaming detected: +2")

    if source_count >= 8:
        score += 2
        logger.debug(f"Source count {source_count} >= 8: +2")

    if detector.detect_ml_complexity(requirements):
        score += 2
        logger.debug("ML complexity detected: +2")

    if detector.detect_governance_requirements(requirements):
        score += 1
        logger.debug("Governance requirements detected: +1")

    if detector.detect_pii_requirements(requirements):
        score += 1
        logger.debug("PII requirements detected: +1")

    logger.info(f"Calculated complexity score: {score}")
    return score


def determine_processing_pattern(
    is_streaming: bool,
    detected_freshness: str | None,
) -> str:
    """Determine processing pattern based on streaming and freshness.

    Args:
        is_streaming: Whether ingestion is streaming (from Phase 3).
        detected_freshness: Freshness requirement (from Phase 3, e.g., "real-time", "daily", "hourly").

    Returns:
        Processing pattern string (e.g., "Real-time stream processing", "Nightly batch ETL (9 PM–6 AM)").
    """
    if is_streaming:
        return "Real-time stream processing"

    if detected_freshness == "real-time":
        return "Real-time stream processing"
    elif detected_freshness == "hourly":
        return "Hourly micro-batch ETL"
    elif detected_freshness == "daily":
        return "Nightly batch ETL (9 PM–6 AM)"
    else:
        return "Batch ETL (schedule to be determined)"
