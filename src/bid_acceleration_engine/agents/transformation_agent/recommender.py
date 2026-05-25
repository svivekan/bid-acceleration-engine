"""Tool recommendation and architecture pattern selection."""

from bid_acceleration_engine.schemas.transformation import TransformationTool
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


def recommend_tool(
    is_streaming: bool,
    complexity_score: int | None,
) -> TransformationTool:
    """Recommend transformation tool based on streaming flag and complexity.

    Decision matrix:
      If streaming: STREAM_ANALYTICS
      If batch (complexity):
        Score 0–1  → FABRIC_PIPELINE
        Score 2–3  → DATA_FACTORY_DATAFLOW
        Score 4+   → DATABRICKS

    Args:
        is_streaming: Whether ingestion is streaming (from Phase 3).
        complexity_score: Transformation complexity score (None for streaming, int for batch).

    Returns:
        Recommended TransformationTool.
    """
    if is_streaming:
        logger.info("Streaming detected: recommending STREAM_ANALYTICS")
        return TransformationTool.STREAM_ANALYTICS

    # Batch ingestion: use complexity score
    if complexity_score is None:
        complexity_score = 0

    if complexity_score <= 1:
        logger.info(f"Batch ingestion, complexity {complexity_score}: recommending FABRIC_PIPELINE")
        return TransformationTool.FABRIC_PIPELINE
    elif complexity_score <= 3:
        logger.info(f"Batch ingestion, complexity {complexity_score}: recommending DATA_FACTORY_DATAFLOW")
        return TransformationTool.DATA_FACTORY_DATAFLOW
    else:
        logger.info(f"Batch ingestion, complexity {complexity_score}: recommending DATABRICKS")
        return TransformationTool.DATABRICKS


def get_architecture_pattern(
    tool: TransformationTool,
    is_streaming: bool,
) -> str:
    """Get architecture pattern based on tool selection.

    Args:
        tool: Selected transformation tool.
        is_streaming: Whether ingestion is streaming (from Phase 3).

    Returns:
        Architecture pattern description.
    """
    if is_streaming:
        return "Event Hubs → Stream Analytics → Data Lake → Analytics (Real-time)"

    patterns = {
        TransformationTool.FABRIC_PIPELINE: "Ingestion → Fabric Pipeline → Lakehouse → Power BI",
        TransformationTool.DATA_FACTORY_DATAFLOW: (
            "Ingestion → Data Factory → Data Flows → Governed Data Lake → Synapse Analytics"
        ),
        TransformationTool.DATABRICKS: "Ingestion → Databricks (Unity Catalog) → Data Lakehouse → Analytics",
        TransformationTool.STREAM_ANALYTICS: "Event Hubs → Stream Analytics → Data Lake → Analytics (Real-time)",
    }

    pattern = patterns.get(tool, "Data Ingestion → Transform → Governed Data Lake")
    logger.debug(f"Architecture pattern for {tool.value}: {pattern}")
    return pattern


def get_key_services(tool: TransformationTool) -> list[str]:
    """Get key Azure services for transformation tool.

    Args:
        tool: Selected transformation tool.

    Returns:
        List of key Azure services.
    """
    services = {
        TransformationTool.FABRIC_PIPELINE: [
            "Fabric Pipeline",
            "Data Lakehouse",
            "Power BI",
            "Microsoft Purview",
            "Azure Monitor",
        ],
        TransformationTool.DATA_FACTORY_DATAFLOW: [
            "Data Factory",
            "Data Flows",
            "Synapse Analytics",
            "Microsoft Purview",
            "Azure Key Vault",
            "Azure Monitor",
        ],
        TransformationTool.DATABRICKS: [
            "Databricks",
            "Unity Catalog",
            "Data Lakehouse",
            "Azure Synapse",
            "Microsoft Purview",
            "Azure Monitor",
        ],
        TransformationTool.STREAM_ANALYTICS: [
            "Event Hubs",
            "Stream Analytics",
            "Data Lake Storage",
            "Azure Synapse",
            "Microsoft Purview",
            "Azure Monitor",
        ],
    }

    key_services = services.get(tool, [])
    logger.debug(f"Key services for {tool.value}: {', '.join(key_services)}")
    return key_services


def get_sla_targets(
    tool: TransformationTool,
    detected_freshness: str | None,
    is_streaming: bool,
) -> dict[str, str]:
    """Get SLA targets based on tool and freshness requirements.

    Args:
        tool: Selected transformation tool.
        detected_freshness: Freshness requirement from Phase 3.
        is_streaming: Whether ingestion is streaming (from Phase 3).

    Returns:
        SLA targets dictionary.
    """
    sla_targets = {}

    # Data freshness SLA
    if is_streaming:
        sla_targets["data_freshness"] = "Real-time (seconds)"
    elif detected_freshness == "hourly":
        sla_targets["data_freshness"] = "Hourly"
    elif detected_freshness == "daily":
        sla_targets["data_freshness"] = "Daily"
    else:
        sla_targets["data_freshness"] = "As defined in schedule"

    # RTO and RPO based on tool
    if tool == TransformationTool.STREAM_ANALYTICS:
        sla_targets["rto"] = "5 minutes"
        sla_targets["rpo"] = "1 minute"
        sla_targets["availability"] = "99.9%"
    elif tool == TransformationTool.DATABRICKS:
        sla_targets["rto"] = "15 minutes"
        sla_targets["rpo"] = "5 minutes"
        sla_targets["availability"] = "99.95%"
    elif tool == TransformationTool.DATA_FACTORY_DATAFLOW:
        sla_targets["rto"] = "30 minutes"
        sla_targets["rpo"] = "15 minutes"
        sla_targets["availability"] = "99.9%"
    else:  # FABRIC_PIPELINE
        sla_targets["rto"] = "1 hour"
        sla_targets["rpo"] = "30 minutes"
        sla_targets["availability"] = "99.9%"

    logger.debug(f"SLA targets for {tool.value}: {sla_targets}")
    return sla_targets


def get_tool_decision(
    tool: TransformationTool,
    complexity_score: int | None,
    is_streaming: bool,
) -> str:
    """Generate justification for tool selection.

    Args:
        tool: Selected transformation tool.
        complexity_score: Transformation complexity score.
        is_streaming: Whether ingestion is streaming (from Phase 3).

    Returns:
        Tool decision justification string.
    """
    if is_streaming:
        return (
            "Streaming transformation required: Stream Analytics for real-time processing, "
            "windowing, and aggregation from Event Hubs."
        )

    if tool == TransformationTool.FABRIC_PIPELINE:
        return (
            f"Batch transformation, low-to-moderate complexity (score: {complexity_score}). "
            "Fabric Pipeline recommended for simple data flows with integrated Lakehouse and Power BI ecosystem."
        )
    elif tool == TransformationTool.DATA_FACTORY_DATAFLOW:
        return (
            f"Batch transformation, moderate-to-high complexity (score: {complexity_score}). "
            "Data Factory with Data Flows recommended for enterprise orchestration and "
            "multi-source transformations."
        )
    elif tool == TransformationTool.DATABRICKS:
        return (
            f"Batch transformation, high complexity (score: {complexity_score}). "
            "Databricks recommended for complex transformations, ML pipelines, or advanced analytics requirements."
        )

    return "Tool selection pending detailed requirements analysis."
