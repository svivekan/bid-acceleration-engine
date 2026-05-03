"""Signal detection: streaming, on-premise sources, volume, freshness, dependencies."""

import re

from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)

# Streaming keywords - ANY match triggers streaming classification
STREAMING_KEYWORDS = [
    "real-time",
    "streaming",
    "event",
    "continuous",
    "live",
    "kafka",
    "event hub",
    "message queue",
]

# On-premise data sources
ON_PREMISE_SOURCES = [
    "sql server",
    "oracle",
    "db2",
    "postgresql",
    "mysql",
    "file share",
    "sftp",
    "on-prem",
    "on-premise",
    "legacy",
    "case management",
    "mainframe",
]

# Cloud/streaming sources
CLOUD_SOURCES = [
    "blob storage",
    "data lake",
    "cosmos db",
    "azure sql",
    "synapse",
    "azure storage",
    "event hub",
    "kafka",
]


def detect_streaming(requirements: list[ExtractedRequirement]) -> bool:
    """Detect if requirements indicate streaming data ingestion.

    Returns True if ANY streaming keyword appears in requirement text.

    Args:
        requirements: List of extracted requirements.

    Returns:
        True if streaming keywords detected, False otherwise.
    """
    for req in requirements:
        text_lower = req.source_text.lower()
        for keyword in STREAMING_KEYWORDS:
            if keyword in text_lower:
                logger.debug(f"Detected streaming keyword '{keyword}' in: {req.source_text[:80]}")
                return True
    return False


def detect_on_premise_sources(requirements: list[ExtractedRequirement]) -> list[str]:
    """Detect on-premise data sources mentioned in requirements.

    Args:
        requirements: List of extracted requirements.

    Returns:
        List of on-premise sources detected (deduplicated).
    """
    sources = set()
    for req in requirements:
        text_lower = req.source_text.lower()
        for source in ON_PREMISE_SOURCES:
            if source in text_lower:
                # Capitalize nicely for output
                sources.add(source.title())
                logger.debug(f"Detected on-prem source '{source}' in: {req.source_text[:80]}")
    return sorted(list(sources))


def detect_data_volume(requirements: list[ExtractedRequirement]) -> str | None:
    """Detect data volume from requirements (GB, TB, PB).

    Args:
        requirements: List of extracted requirements.

    Returns:
        Volume string (e.g., "2TB", "500GB") or None if not found.
    """
    for req in requirements:
        text_lower = req.source_text.lower()
        # Pattern: number followed by GB/TB/PB
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:gb|tb|pb)", text_lower)
        if match:
            volume_str = match.group(0)
            logger.debug(f"Detected volume: {volume_str}")
            return volume_str
    return None


def detect_freshness_requirement(requirements: list[ExtractedRequirement]) -> str | None:
    """Detect data freshness requirement (real-time, daily, hourly, etc.).

    Args:
        requirements: List of extracted requirements.

    Returns:
        Freshness requirement string or None if not found.
    """
    freshness_patterns = {
        "real-time": r"real-?time|immediate|sub-?second|millisecond",
        "hourly": r"hourly|every hour",
        "daily": r"daily|every day|24 hours",
        "batch": r"batch|periodic|scheduled",
    }

    for req in requirements:
        text_lower = req.source_text.lower()
        for freshness, pattern in freshness_patterns.items():
            if re.search(pattern, text_lower):
                logger.debug(f"Detected freshness: {freshness}")
                return freshness
    return None


def detect_orchestration_dependencies(requirements: list[ExtractedRequirement]) -> int:
    """Estimate number of orchestration dependencies.

    Looks for keywords indicating system integrations and dependencies.

    Args:
        requirements: List of extracted requirements.

    Returns:
        Estimated number of dependencies.
    """
    dependency_keywords = [
        "integrate",
        "sync",
        "consolidate",
        "combine",
        "match",
        "join",
        "link",
        "connect",
        "multiple systems",
        "cross-system",
        "end-to-end",
    ]

    dependency_count = 0
    for req in requirements:
        text_lower = req.source_text.lower()
        for keyword in dependency_keywords:
            if keyword in text_lower:
                dependency_count += 1
    return dependency_count


def count_data_sources(requirements: list[ExtractedRequirement]) -> int:
    """Count number of data sources mentioned in requirements.

    Counts references to databases, files, APIs, systems.

    Args:
        requirements: List of extracted requirements.

    Returns:
        Estimated number of data sources.
    """
    all_sources = (
        ON_PREMISE_SOURCES
        + CLOUD_SOURCES
        + [
            "api",
            "database",
            "system",
            "platform",
            "file",
            "source",
        ]
    )

    source_mentions = set()
    for req in requirements:
        text_lower = req.source_text.lower()
        for source in all_sources:
            if source in text_lower:
                source_mentions.add(source)

    # Count is based on unique sources mentioned
    return len(source_mentions)
