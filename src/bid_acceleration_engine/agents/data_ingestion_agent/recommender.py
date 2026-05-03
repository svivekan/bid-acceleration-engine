"""Tool recommender: Fabric Pipelines vs Data Factory vs Event Hubs + Stream Analytics."""

from bid_acceleration_engine.schemas.data_ingestion import IngestionTool
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


def recommend_tool(
    is_streaming: bool,
    complexity_score: int | None,
) -> IngestionTool:
    """Recommend ingestion tool based on streaming status and complexity.

    Decision logic:
    - If streaming: Event Hubs + Stream Analytics
    - If batch AND score ≥3: Data Factory
    - If batch AND score <3: Fabric Pipelines

    Args:
        is_streaming: Whether streaming ingestion is required.
        complexity_score: Batch complexity score (None if streaming).

    Returns:
        Recommended IngestionTool.
    """
    if is_streaming:
        logger.info("Recommending Event Hubs + Stream Analytics for streaming")
        return IngestionTool.EVENT_HUBS_STREAM_ANALYTICS

    if complexity_score is None:
        raise ValueError("complexity_score required for batch ingestion")

    if complexity_score >= 3:
        logger.info(f"Recommending Data Factory (score: {complexity_score})")
        return IngestionTool.DATA_FACTORY
    else:
        logger.info(f"Recommending Fabric Pipelines (score: {complexity_score})")
        return IngestionTool.FABRIC_PIPELINE


def get_architecture_pattern(
    tool: IngestionTool,
    has_on_premise: bool,
) -> str:
    """Get recommended architecture pattern for the tool.

    Args:
        tool: Recommended IngestionTool.
        has_on_premise: Whether on-premise sources are involved.

    Returns:
        Architecture pattern string.
    """
    if tool == IngestionTool.EVENT_HUBS_STREAM_ANALYTICS:
        return "Event Source → Event Hubs → Stream Analytics → Data Lake / Lakehouse"

    if has_on_premise:
        if tool == IngestionTool.FABRIC_PIPELINE:
            return "On-Prem Source → Self-Hosted IR → Fabric Data Pipeline → Lakehouse"
        else:  # DATA_FACTORY
            return "On-Prem Source → Self-Hosted IR → Data Factory → Synapse / Data Lake"

    # Cloud-only sources
    if tool == IngestionTool.FABRIC_PIPELINE:
        return "Cloud Source → Fabric Data Pipeline → Lakehouse"
    else:  # DATA_FACTORY
        return "Cloud Source → Data Factory → Synapse / Data Lake"


def get_key_services(tool: IngestionTool) -> list[str]:
    """Get list of key Azure services for the recommended tool.

    Args:
        tool: Recommended IngestionTool.

    Returns:
        List of Azure service names.
    """
    if tool == IngestionTool.EVENT_HUBS_STREAM_ANALYTICS:
        return [
            "Azure Event Hubs",
            "Azure Stream Analytics",
            "Azure Data Lake Storage",
            "Fabric Lakehouse",
        ]

    if tool == IngestionTool.FABRIC_PIPELINE:
        return [
            "Data Factory Self-Hosted IR",
            "Fabric Data Pipeline",
            "Fabric Lakehouse",
        ]

    # DATA_FACTORY
    return [
        "Azure Data Factory",
        "Self-Hosted Integration Runtime",
        "Azure Synapse Analytics",
        "Azure Data Lake Storage",
    ]
