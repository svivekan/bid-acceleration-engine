"""Transformation Agent: Phase 4 of bid acceleration pipeline."""

from datetime import datetime
from uuid import uuid4

from bid_acceleration_engine.agents.bid_intake_agent.agent import BaseAgent
from bid_acceleration_engine.agents.data_ingestion_agent import (
    compliance_checker as ingestion_compliance,
)
from bid_acceleration_engine.agents.transformation_agent import (
    analyzer,
    detector,
    governance_designer,
    quality_designer,
    recommender,
)
from bid_acceleration_engine.schemas.data_ingestion import DataIngestionArchitecture
from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.schemas.results import AgentResult, AgentStatus
from bid_acceleration_engine.schemas.transformation import TransformationArchitecture
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


class TransformationAgent(BaseAgent):
    """Analyzes requirements and recommends data transformation architecture.

    Phase 4 of the bid acceleration pipeline.
    Input: DataIngestionArchitecture (from Phase 3) + ExtractedRequirement[] (from Phase 2)
    Output: TransformationArchitecture (with data quality and governance configuration)
    """

    def run(
        self,
        ingestion_arch: DataIngestionArchitecture,
        requirements: list[ExtractedRequirement],
    ) -> AgentResult[TransformationArchitecture]:
        """Recommend data transformation architecture.

        Args:
            ingestion_arch: Data ingestion architecture from Phase 3.
            requirements: List of extracted requirements from Phase 2.

        Returns:
            AgentResult containing TransformationArchitecture.
        """
        logger.info(
            f"TransformationAgent processing: tool={ingestion_arch.tool.value}, "
            f"streaming={ingestion_arch.is_streaming}, requirements={len(requirements)}"
        )

        try:
            # ====================================================================
            # PHASE 1: Signal Detection
            # ====================================================================
            has_pii = detector.detect_pii_requirements(requirements)
            has_governance = detector.detect_governance_requirements(requirements)
            has_ml = detector.detect_ml_complexity(requirements)
            dedup_required = detector.detect_deduplication_needs(requirements)
            reconciliation_required = detector.detect_reconciliation_needs(requirements)
            compliance_frameworks = detector.detect_compliance_frameworks(requirements)

            logger.info(
                f"Transformation signals: PII={has_pii}, governance={has_governance}, "
                f"ML={has_ml}, dedup={dedup_required}, reconciliation={reconciliation_required}, "
                f"frameworks={compliance_frameworks}"
            )

            # ====================================================================
            # PHASE 2: Complexity Scoring
            # ====================================================================
            complexity_score = analyzer.calculate_complexity_score(
                is_streaming=ingestion_arch.is_streaming,
                source_count=len(ingestion_arch.on_premise_sources) + len(ingestion_arch.detected_sources),
                detected_freshness=ingestion_arch.detected_freshness,
                requirements=requirements,
            )

            logger.info(f"Calculated transformation complexity score: {complexity_score}")

            # ====================================================================
            # PHASE 3: Tool Recommendation
            # ====================================================================
            tool = recommender.recommend_tool(
                is_streaming=ingestion_arch.is_streaming,
                complexity_score=complexity_score if not ingestion_arch.is_streaming else None,
            )
            tool_decision = recommender.get_tool_decision(
                tool=tool,
                complexity_score=complexity_score,
                is_streaming=ingestion_arch.is_streaming,
            )

            # ====================================================================
            # PHASE 4: Architecture Pattern & Services
            # ====================================================================
            architecture_pattern = recommender.get_architecture_pattern(
                tool=tool,
                is_streaming=ingestion_arch.is_streaming,
            )
            key_services = recommender.get_key_services(tool)
            processing_pattern = analyzer.determine_processing_pattern(
                is_streaming=ingestion_arch.is_streaming,
                detected_freshness=ingestion_arch.detected_freshness,
            )

            # ====================================================================
            # PHASE 5: SLA Targets
            # ====================================================================
            sla_targets = recommender.get_sla_targets(
                tool=tool,
                detected_freshness=ingestion_arch.detected_freshness,
                is_streaming=ingestion_arch.is_streaming,
            )

            # ====================================================================
            # PHASE 6: Data Quality Configuration
            # ====================================================================
            data_quality = quality_designer.design_data_quality_configuration(requirements)

            logger.info(f"Generated {len(data_quality.rules)} data quality rules")

            # ====================================================================
            # PHASE 7: Governance Configuration
            # ====================================================================
            # Check if UK government RFP from Phase 3 analysis
            is_uk_gov = ingestion_compliance.check_uk_government(requirements)
            governance = governance_designer.design_governance_configuration(
                requirements=requirements,
                is_uk_gov=is_uk_gov,
            )

            logger.info(
                f"Governance: lineage={governance.lineage_enabled}, "
                f"uk_residency={governance.uk_data_residency}, "
                f"frameworks={governance.compliance_frameworks}"
            )

            # ====================================================================
            # Build Complexity Factors Explanation
            # ====================================================================
            complexity_factors = []
            if ingestion_arch.is_streaming:
                complexity_factors.append("Streaming ingestion (+2)")
            if len(ingestion_arch.on_premise_sources) + len(ingestion_arch.detected_sources) >= 8:
                complexity_factors.append(
                    f"{len(ingestion_arch.on_premise_sources) + len(ingestion_arch.detected_sources)} sources (≥8 = +2)"
                )
            if has_ml:
                complexity_factors.append("ML/analytics complexity (+2)")
            if has_governance:
                complexity_factors.append("Governance requirements (+1)")
            if has_pii:
                complexity_factors.append("PII handling (+1)")

            # ====================================================================
            # Build Considerations & Assumptions
            # ====================================================================
            considerations = []
            if has_pii:
                considerations.append("PII masking and anonymisation required for analytics datasets")
            if has_governance:
                considerations.append("Data lineage and provenance tracking required (Microsoft Purview)")
            if reconciliation_required:
                considerations.append("Reconciliation checks required for data integrity validation")
            if has_ml:
                considerations.append("ML/advanced analytics complexity requires data science support")
            if is_uk_gov or "GDPR" in compliance_frameworks:
                considerations.append("UK government compliance and GDPR data residency required")
            if "NHS DSPT" in compliance_frameworks:
                considerations.append("NHS DSPT compliance and 7-year retention policy required")

            assumptions = []
            if ingestion_arch.detected_volume:
                assumptions.append(f"Data volume: {ingestion_arch.detected_volume}")
            if ingestion_arch.detected_freshness:
                assumptions.append(f"Data freshness requirement: {ingestion_arch.detected_freshness}")
            if ingestion_arch.shir_config:
                assumptions.append("Self-Hosted Integration Runtime (SHIR) available from Phase 3")
            assumptions.append(f"Transformation tool: {tool.value}")
            if len(data_quality.rules) > 0:
                assumptions.append(f"Data quality framework with {len(data_quality.rules)} rules applied")

            # ====================================================================
            # Build Output
            # ====================================================================
            architecture = TransformationArchitecture(
                id=uuid4(),
                tool=tool,
                is_streaming=ingestion_arch.is_streaming,
                complexity_score=complexity_score,
                data_quality=data_quality,
                governance=governance,
                processing_pattern=processing_pattern,
                architecture_pattern=architecture_pattern,
                key_services=key_services,
                tool_decision=tool_decision,
                complexity_factors=complexity_factors,
                sla_targets=sla_targets,
                considerations=considerations,
                assumptions=assumptions,
                created_at=datetime.now(),
            )

            logger.info(
                f"TransformationAgent completed: tool={tool.value}, "
                f"complexity={complexity_score}, quality_rules={len(data_quality.rules)}"
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
            logger.error(f"TransformationAgent failed: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILURE,
                output=None,
                error_message=str(e),
                duration_seconds=0,
                produced_at=datetime.now(),
            )
