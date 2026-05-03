"""Data ingestion architecture schema."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IngestionTool(StrEnum):
    """Recommended data ingestion tool."""

    FABRIC_PIPELINE = "fabric_pipeline"
    DATA_FACTORY = "data_factory"
    EVENT_HUBS_STREAM_ANALYTICS = "event_hubs_stream_analytics"


class SHIRConfiguration(BaseModel):
    """Self-Hosted Integration Runtime configuration for on-premise sources."""

    model_config = ConfigDict(extra="forbid")

    required: bool
    placement: str  # "on-prem", "dmz", "azure-vm"

    # High Availability
    ha_required: bool
    ha_nodes: int
    failover_strategy: str | None = None

    # Network Security
    network_security_layer: str
    # "shir-only" | "shir-plus-vpn" | "shir-plus-expressroute"
    firewall_rules: list[str]
    private_endpoints_required: bool

    # Authentication & Secrets
    credentials_storage: str  # "azure-key-vault"
    credentials_rotation_required: bool
    managed_identity_possible: bool
    authentication_method: str
    # "windows-auth" | "sql-auth" | "managed-identity"

    # Encryption
    encryption_in_transit: str  # "tls-1-2-plus"
    encryption_at_rest: bool
    column_level_encryption_for_pii: bool

    # Data Residency & Compliance
    uk_region_required: bool
    azure_regions: list[str]
    gdpr_compliant: bool
    audit_logging_required: bool

    # Monitoring & Observability
    monitoring_enabled: bool
    shir_connection_monitoring: bool
    data_movement_audit_trail: bool
    alerting_on_failures: bool
    alerting_on_suspicious_access: bool

    # Performance
    concurrent_connections: int | None = None
    estimated_daily_volume_gb: int | None = None
    retry_strategy: str  # "exponential-backoff"

    # Security & Compliance Guidance
    security_recommendations: list[str]
    compliance_checklist: list[str]


class DataIngestionArchitecture(BaseModel):
    """Data ingestion architecture recommendation."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    tool: IngestionTool
    is_streaming: bool
    complexity_score: int | None = None

    # Detection & Analysis
    detected_sources: list[str]
    on_premise_sources: list[str]
    detected_volume: str | None = None
    detected_freshness: str | None = None
    detected_dependencies: int | None = None

    # Decision details
    tool_decision: str
    complexity_factors: list[str]

    # Architecture pattern
    architecture_pattern: str
    key_services: list[str]

    # SHIR Configuration (if on-prem sources detected)
    shir_config: SHIRConfiguration | None = None

    # Constraints & considerations
    considerations: list[str]
    assumptions: list[str]

    created_at: datetime
