"""Data transformation architecture schema."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TransformationTool(StrEnum):
    """Recommended data transformation tool."""

    FABRIC_PIPELINE = "fabric_pipeline"
    DATA_FACTORY_DATAFLOW = "data_factory_dataflow"
    DATABRICKS = "databricks"
    STREAM_ANALYTICS = "stream_analytics"


class DataQualityRule(BaseModel):
    """A single data quality rule or framework component."""

    model_config = ConfigDict(extra="forbid")

    tier: str  # "deduplication" | "validation" | "reconciliation" | "pii_masking"
    description: str  # Human-readable rule
    implementation: str  # How to implement in Azure tooling


class DataQualityConfiguration(BaseModel):
    """Data quality framework and rules."""

    model_config = ConfigDict(extra="forbid")

    rules: list[DataQualityRule]
    has_pii: bool
    reconciliation_required: bool
    deduplication_required: bool


class GovernanceConfiguration(BaseModel):
    """Governance, compliance, and audit framework."""

    model_config = ConfigDict(extra="forbid")

    lineage_enabled: bool
    lineage_tool: str  # "Microsoft Purview"
    audit_logging: str  # "Azure Monitor"
    retention_policy: str | None  # "7 years per NHS Records Management Code" or None
    compliance_frameworks: list[str]  # ["GDPR", "NHS DSPT"]
    pii_masking_required: bool
    uk_data_residency: bool


class TransformationArchitecture(BaseModel):
    """Data transformation architecture recommendation."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    tool: TransformationTool
    is_streaming: bool
    complexity_score: int

    data_quality: DataQualityConfiguration
    governance: GovernanceConfiguration

    processing_pattern: str  # "Nightly batch ETL (9 PM–6 AM)" or "Real-time stream processing"
    architecture_pattern: str  # "Ingestion → Transform → Governed Data Lake"
    key_services: list[str]

    tool_decision: str  # Justification for tool selection
    complexity_factors: list[str]  # Breakdown of complexity score

    sla_targets: dict[str, str]  # {"data_freshness": "daily", "rto": "4 hours"}

    considerations: list[str]
    assumptions: list[str]

    created_at: datetime
