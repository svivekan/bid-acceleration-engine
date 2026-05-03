"""Data Ingestion Agent: Phase 3 of bid acceleration pipeline."""

from datetime import datetime
from uuid import uuid4

from bid_acceleration_engine.agents.bid_intake_agent.agent import BaseAgent
from bid_acceleration_engine.agents.data_ingestion_agent import (
    analyzer,
    compliance_checker,
    detector,
    recommender,
    security_analyzer,
    shir_configurator,
)
from bid_acceleration_engine.schemas.data_ingestion import (
    DataIngestionArchitecture,
    SHIRConfiguration,
)
from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.schemas.results import AgentResult, AgentStatus
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


class DataIngestionAgent(BaseAgent):
    """Analyzes requirements and recommends data ingestion architecture.

    Phase 3 of the bid acceleration pipeline.
    Input: ExtractedRequirement[] from Phase 2
    Output: DataIngestionArchitecture (with SHIR configuration if on-prem)
    """

    def run(
        self,
        requirements: list[ExtractedRequirement],
    ) -> AgentResult[DataIngestionArchitecture]:
        """Recommend data ingestion architecture.

        Args:
            requirements: List of extracted requirements from Phase 2.

        Returns:
            AgentResult containing DataIngestionArchitecture.
        """
        logger.info(f"DataIngestionAgent processing {len(requirements)} requirements")

        try:
            # ====================================================================
            # PHASE 1: Detect Signals
            # ====================================================================
            is_streaming = detector.detect_streaming(requirements)
            on_premise_sources = detector.detect_on_premise_sources(requirements)
            detected_volume = detector.detect_data_volume(requirements)
            detected_freshness = detector.detect_freshness_requirement(requirements)
            detected_dependencies = detector.detect_orchestration_dependencies(requirements)
            source_count = detector.count_data_sources(requirements)

            logger.info(
                f"Signals: streaming={is_streaming}, on-prem={len(on_premise_sources)}, "
                f"sources={source_count}, dependencies={detected_dependencies}"
            )

            # ====================================================================
            # PHASE 2: Tool Recommendation (Batch or Streaming)
            # ====================================================================
            if is_streaming:
                tool = recommender.recommend_tool(is_streaming=True, complexity_score=None)
                complexity_score = None
                complexity_factors = []
                tool_decision = (
                    "Streaming ingestion required: Event Hubs + Stream Analytics for real-time data processing"
                )
            else:
                # Score complexity for batch ingestion
                volume_gb = analyzer.extract_volume_gb(detected_volume)
                has_governance = analyzer.has_enterprise_governance(requirements)
                complexity_score = analyzer.calculate_complexity_score(
                    source_count=source_count,
                    volume_gb=volume_gb,
                    dependency_count=detected_dependencies,
                    has_governance=has_governance,
                )

                tool = recommender.recommend_tool(is_streaming=False, complexity_score=complexity_score)

                # Build complexity factors explanation
                complexity_factors = []
                if source_count >= 5:
                    complexity_factors.append(f"{source_count} sources (≥5 = +2)")
                if volume_gb and volume_gb > 5_000:
                    complexity_factors.append(f"{volume_gb}GB volume (>5TB = +2)")
                if detected_dependencies > 10:
                    complexity_factors.append(f"{detected_dependencies} dependencies (>10 = +2)")
                if has_governance:
                    complexity_factors.append("Enterprise governance required (+1)")

                if tool.value == "fabric_pipeline":
                    tool_decision = (
                        f"Batch ingestion, low-to-moderate complexity (score: {complexity_score}). "
                        "Fabric Pipelines recommended for integrated Lakehouse + Power BI flow."
                    )
                else:
                    tool_decision = (
                        f"Batch ingestion, complex requirements (score: {complexity_score}). "
                        "Data Factory recommended for enterprise-grade governance and orchestration."
                    )

            # ====================================================================
            # PHASE 3: Architecture Pattern
            # ====================================================================
            architecture_pattern = recommender.get_architecture_pattern(
                tool=tool,
                has_on_premise=len(on_premise_sources) > 0,
            )
            key_services = recommender.get_key_services(tool)

            # ====================================================================
            # Detect Compliance Requirements (always needed)
            # ====================================================================
            is_uk_gov = compliance_checker.check_uk_government(requirements)
            has_gdpr = compliance_checker.check_gdpr_requirement(requirements)
            is_healthcare = compliance_checker.check_healthcare_requirement(requirements)

            # ====================================================================
            # PHASE 4: SHIR Configuration (if on-premise sources)
            # ====================================================================
            shir_config = None
            if on_premise_sources:
                logger.info(f"Configuring SHIR for on-premise sources: {on_premise_sources}")

                placement = shir_configurator.determine_placement(
                    has_on_premise=True,
                    requirements=requirements,
                )
                ha_required, ha_nodes = shir_configurator.determine_ha_requirement(requirements)
                network_security_layer = shir_configurator.determine_network_security(requirements)
                auth_method, managed_identity_possible = shir_configurator.determine_authentication_method(requirements)
                concurrent_connections = shir_configurator.determine_concurrent_connections(
                    source_count=source_count,
                    freshness=detected_freshness,
                )
                estimated_daily_volume = shir_configurator.estimate_daily_volume_gb(detected_volume)

                # ================================================================
                # PHASE 5: Security Configuration
                # ================================================================
                encryption_in_transit, encryption_at_rest, column_level_pii = security_analyzer.determine_encryption(
                    requirements
                )
                firewall_rules = security_analyzer.determine_firewall_rules(on_premise_sources)

                security_recommendations = security_analyzer.generate_security_recommendations(
                    auth_method=auth_method,
                    network_security_layer=network_security_layer,
                    encryption_at_rest=encryption_at_rest,
                    column_level_encryption=column_level_pii,
                    requirements=requirements,
                )

                # ================================================================
                # PHASE 6: Compliance Configuration
                # ================================================================
                uk_residency = compliance_checker.check_uk_data_residency(requirements) or is_uk_gov

                uk_regions = compliance_checker.get_uk_regions() if uk_residency else []
                compliance_checklist = compliance_checker.generate_compliance_checklist(
                    is_uk_government=is_uk_gov,
                    has_gdpr=has_gdpr,
                    is_healthcare=is_healthcare,
                )

                # Build SHIR config
                shir_config = SHIRConfiguration(
                    required=True,
                    placement=placement,
                    ha_required=ha_required,
                    ha_nodes=ha_nodes,
                    failover_strategy="auto-registered-nodes" if ha_required else None,
                    network_security_layer=network_security_layer,
                    firewall_rules=firewall_rules,
                    private_endpoints_required=not is_streaming,
                    credentials_storage="azure-key-vault",
                    credentials_rotation_required=auth_method == "sql-auth",
                    managed_identity_possible=managed_identity_possible,
                    authentication_method=auth_method,
                    encryption_in_transit=encryption_in_transit,
                    encryption_at_rest=encryption_at_rest,
                    column_level_encryption_for_pii=column_level_pii,
                    uk_region_required=uk_residency,
                    azure_regions=uk_regions,
                    gdpr_compliant=has_gdpr,
                    audit_logging_required=is_uk_gov or has_gdpr or ha_required,
                    monitoring_enabled=True,
                    shir_connection_monitoring=True,
                    data_movement_audit_trail=is_uk_gov or has_gdpr or ha_required,
                    alerting_on_failures=True,
                    alerting_on_suspicious_access=is_uk_gov or has_gdpr or ha_required,
                    concurrent_connections=concurrent_connections,
                    estimated_daily_volume_gb=estimated_daily_volume,
                    retry_strategy="exponential-backoff",
                    security_recommendations=security_recommendations,
                    compliance_checklist=compliance_checklist,
                )

            # ====================================================================
            # Build Output
            # ====================================================================
            considerations = []
            if on_premise_sources:
                considerations.append(f"On-premise sources detected: {', '.join(on_premise_sources)}")
            if is_uk_gov:
                considerations.append("UK government compliance required (UK data residency)")
            if has_gdpr:
                considerations.append("GDPR compliance required (data protection, audit trails)")
            if is_healthcare:
                considerations.append("Healthcare compliance (NHS DSPT standards)")
            if detected_dependencies > 10:
                considerations.append(f"Complex orchestration ({detected_dependencies} dependencies)")

            assumptions = []
            if detected_freshness:
                assumptions.append(f"Data freshness requirement: {detected_freshness}")
            if detected_volume:
                assumptions.append(f"Data volume: {detected_volume}")
            if on_premise_sources:
                assumptions.append("Self-Hosted Integration Runtime (SHIR) infrastructure available")
            if architecture_pattern:
                assumptions.append(f"Architecture pattern: {architecture_pattern}")

            architecture = DataIngestionArchitecture(
                id=uuid4(),
                tool=tool,
                is_streaming=is_streaming,
                complexity_score=complexity_score,
                detected_sources=detector.ON_PREMISE_SOURCES + detector.CLOUD_SOURCES,
                on_premise_sources=on_premise_sources,
                detected_volume=detected_volume,
                detected_freshness=detected_freshness,
                detected_dependencies=detected_dependencies,
                tool_decision=tool_decision,
                complexity_factors=complexity_factors,
                architecture_pattern=architecture_pattern,
                key_services=key_services,
                shir_config=shir_config,
                considerations=considerations,
                assumptions=assumptions,
                created_at=datetime.now(),
            )

            logger.info(
                f"DataIngestionAgent completed: tool={tool.value}, "
                f"on_prem={len(on_premise_sources)}, complexity={complexity_score}"
            )

            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                output=architecture,
                error_message=None,
                duration_seconds=0,
                produced_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"DataIngestionAgent failed: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILURE,
                output=None,
                error_message=str(e),
                duration_seconds=0,
                produced_at=datetime.now(),
            )
