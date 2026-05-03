"""Batch complexity analyzer: scoring for Fabric vs Data Factory decision."""

import re

from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


def extract_volume_gb(volume_str: str | None) -> int | None:
    """Convert volume string to GB.

    Args:
        volume_str: Volume string like "2TB", "500GB", "1PB".

    Returns:
        Size in GB, or None if unparseable.
    """
    if not volume_str:
        return None

    match = re.search(r"(\d+(?:\.\d+)?)\s*(gb|tb|pb)", volume_str.lower())
    if not match:
        return None

    value = float(match.group(1))
    unit = match.group(2).lower()

    if unit == "pb":
        return int(value * 1_000_000)
    elif unit == "tb":
        return int(value * 1_000)
    else:  # gb
        return int(value)


def has_enterprise_governance(requirements: list[ExtractedRequirement]) -> bool:
    """Check if requirements indicate enterprise governance needs.

    Args:
        requirements: List of extracted requirements.

    Returns:
        True if enterprise, governance, SLA, audit, or compliance keywords found.
    """
    enterprise_keywords = [
        "enterprise",
        "governance",
        "sla",
        "audit",
        "compliance",
        "audit trail",
        "high availability",
        "disaster recovery",
        "business critical",
    ]

    for req in requirements:
        text_lower = req.source_text.lower()
        for keyword in enterprise_keywords:
            if keyword in text_lower:
                logger.debug(f"Detected enterprise governance signal: {keyword}")
                return True
    return False


def calculate_complexity_score(
    source_count: int,
    volume_gb: int | None,
    dependency_count: int,
    has_governance: bool,
) -> int:
    """Calculate batch ingestion complexity score.

    Scoring:
    - ≥5 sources: +2 points
    - >5TB volume: +2 points
    - >10 dependencies: +2 points
    - Enterprise governance: +1 point

    Decision:
    - Score ≥3 → Use Data Factory
    - Score <3 → Use Fabric Pipelines

    Args:
        source_count: Number of data sources.
        volume_gb: Data volume in GB.
        dependency_count: Number of orchestration dependencies.
        has_governance: Whether enterprise governance required.

    Returns:
        Complexity score (0-7).
    """
    score = 0

    # Sources (≥5 = +2)
    if source_count >= 5:
        score += 2
        logger.debug(f"Complexity +2 for {source_count} sources")

    # Volume (>5TB = +2)
    if volume_gb and volume_gb > 5_000:
        score += 2
        logger.debug(f"Complexity +2 for {volume_gb}GB volume (>5TB)")

    # Orchestration (>10 dependencies = +2)
    if dependency_count > 10:
        score += 2
        logger.debug(f"Complexity +2 for {dependency_count} dependencies")

    # Governance (+1)
    if has_governance:
        score += 1
        logger.debug("Complexity +1 for enterprise governance")

    logger.debug(f"Total complexity score: {score}")
    return score
