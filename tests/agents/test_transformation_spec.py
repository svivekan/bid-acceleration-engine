"""Phase 4 Transformation Agent spec-driven tests."""

from datetime import datetime
from uuid import uuid4

import pytest

from bid_acceleration_engine.agents.transformation_agent.agent import TransformationAgent
from bid_acceleration_engine.schemas.data_ingestion import DataIngestionArchitecture, IngestionTool
from bid_acceleration_engine.schemas.requirements import (
    EstimatedComplexity,
    ExtractedRequirement,
    RequirementCategory,
    RequirementPriority,
)
from bid_acceleration_engine.schemas.results import AgentStatus
from bid_acceleration_engine.schemas.transformation import TransformationTool


class TestTransformationAgent:
    """Test Transformation Agent against spec requirements."""

    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        return TransformationAgent("transformation_agent")

    def _make_requirement(self, text: str, category=RequirementCategory.TECHNICAL) -> ExtractedRequirement:
        """Helper to create a requirement."""
        return ExtractedRequirement(
            id=uuid4(),
            source_text=text,
            category=category,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.SIMPLE,
            mandatory=True,
            section_heading="Requirements",
        )

    def _make_ingestion_arch(
        self,
        tool: IngestionTool = IngestionTool.FABRIC_PIPELINE,
        is_streaming: bool = False,
        on_premise_sources: list[str] | None = None,
        detected_sources: list[str] | None = None,
        detected_volume: str | None = None,
        detected_freshness: str | None = None,
    ) -> DataIngestionArchitecture:
        """Helper to create a DataIngestionArchitecture."""
        if on_premise_sources is None:
            on_premise_sources = []
        if detected_sources is None:
            detected_sources = []

        return DataIngestionArchitecture(
            id=uuid4(),
            tool=tool,
            is_streaming=is_streaming,
            complexity_score=0,
            detected_sources=detected_sources,
            on_premise_sources=on_premise_sources,
            detected_volume=detected_volume,
            detected_freshness=detected_freshness,
            detected_dependencies=0,
            tool_decision="Test ingestion architecture",
            complexity_factors=[],
            architecture_pattern="Test pattern",
            key_services=[],
            shir_config=None,
            considerations=[],
            assumptions=[],
            created_at=datetime.now(),
        )

    # ========================================================================
    # Test 1: Simple Batch (Fabric Ingestion, Daily)
    # ========================================================================
    def test_simple_batch_fabric_recommends_fabric_transform(self, agent):
        """Simple batch (Fabric ingestion, daily) → Fabric Pipeline for transform."""
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.FABRIC_PIPELINE,
            is_streaming=False,
            detected_freshness="daily",
        )
        requirements = [
            self._make_requirement("Daily batch ETL, simple transformations"),
        ]

        result = agent.run(ingestion_arch, requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should recommend Fabric Pipeline
        assert output.tool == TransformationTool.FABRIC_PIPELINE
        assert output.is_streaming is False

        # Should have basic quality rules
        assert len(output.data_quality.rules) > 0
        assert output.data_quality.has_pii is False

    # ========================================================================
    # Test 2: Complex Batch (8+ Sources, Governance)
    # ========================================================================
    def test_complex_batch_multisource_recommends_data_factory(self, agent):
        """Complex batch (8+ sources, governance) → Data Factory for transform."""
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.DATA_FACTORY,
            is_streaming=False,
            on_premise_sources=["Sql Server", "Oracle", "Postgresql", "Mysql", "Db2"],
            detected_sources=["File Share", "Sftp", "Case Management"],
            detected_freshness="daily",
        )
        requirements = [
            self._make_requirement("Consolidate 8+ legacy systems with complex orchestration"),
            self._make_requirement("Data lineage and audit trail required", RequirementCategory.COMPLIANCE),
            self._make_requirement("Enterprise governance framework"),
        ]

        result = agent.run(ingestion_arch, requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should recommend Data Factory (8+ sources + governance = complexity >= 2)
        assert output.tool == TransformationTool.DATA_FACTORY_DATAFLOW
        assert output.complexity_score >= 2

        # Should have governance enabled
        assert output.governance.lineage_enabled is True
        assert output.governance.lineage_tool == "Microsoft Purview"

    # ========================================================================
    # Test 3: Streaming Ingestion
    # ========================================================================
    def test_streaming_recommends_stream_analytics(self, agent):
        """Streaming ingestion (Event Hubs) → Stream Analytics for transform."""
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.EVENT_HUBS_STREAM_ANALYTICS,
            is_streaming=True,
            detected_freshness="real-time",
        )
        requirements = [
            self._make_requirement("Real-time event processing, continuous transformations"),
        ]

        result = agent.run(ingestion_arch, requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should detect streaming and recommend Stream Analytics
        assert output.tool == TransformationTool.STREAM_ANALYTICS
        assert output.is_streaming is True
        assert "Real-time" in output.processing_pattern

    # ========================================================================
    # Test 4: High Complexity + ML Requirements
    # ========================================================================
    def test_high_complexity_ml_recommends_databricks(self, agent):
        """High complexity + ML → Databricks."""
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.DATA_FACTORY,
            is_streaming=False,
            on_premise_sources=["Sql Server", "Oracle", "Postgresql", "Mysql"],
            detected_sources=["File Share", "Sftp", "Case Management", "Api"],
            detected_freshness="daily",
        )
        requirements = [
            self._make_requirement("Machine learning model scoring pipeline"),
            self._make_requirement("Advanced analytics and predictive forecasting"),
            self._make_requirement("Complex data transformations and feature engineering"),
            self._make_requirement("Data governance and lineage required", RequirementCategory.COMPLIANCE),
        ]

        result = agent.run(ingestion_arch, requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should detect ML complexity and 8+ sources, recommend Databricks
        assert output.tool == TransformationTool.DATABRICKS
        assert output.complexity_score >= 4

    # ========================================================================
    # Test 5: GDPR/PII Requirements
    # ========================================================================
    def test_gdpr_pii_requirements(self, agent):
        """GDPR/PII → PII masking rule, Purview lineage."""
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.FABRIC_PIPELINE,
            is_streaming=False,
        )
        requirements = [
            self._make_requirement(
                "GDPR compliance required, personal data protection",
                RequirementCategory.COMPLIANCE,
            ),
            self._make_requirement("PII masking for analytics datasets"),
        ]

        result = agent.run(ingestion_arch, requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should detect PII and GDPR
        assert output.data_quality.has_pii is True
        assert output.governance.pii_masking_required is True
        assert output.governance.lineage_enabled is True
        assert "GDPR" in output.governance.compliance_frameworks

        # Should have PII masking rule
        assert any(rule.tier == "pii_masking" for rule in output.data_quality.rules)

        # Should have Purview
        assert output.governance.lineage_tool == "Microsoft Purview"

    # ========================================================================
    # Test 6: NHS Compliance
    # ========================================================================
    def test_nhs_compliance(self, agent):
        """NHS DSPT compliance → 7-year retention, Data Factory or Databricks."""
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.DATA_FACTORY,
            is_streaming=False,
        )
        requirements = [
            self._make_requirement(
                "NHS Data Security and Protection Toolkit (DSPT) compliance",
                RequirementCategory.COMPLIANCE,
            ),
            self._make_requirement(
                "Healthcare data integration, clinical audit trails",
                RequirementCategory.COMPLIANCE,
            ),
        ]

        result = agent.run(ingestion_arch, requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should detect NHS framework
        assert "NHS DSPT" in output.governance.compliance_frameworks

        # Should have 7-year retention policy
        assert output.governance.retention_policy is not None
        assert "7 year" in output.governance.retention_policy.lower()

        # Should have governance enabled
        assert output.governance.lineage_enabled is True

    # ========================================================================
    # Test 7: Governance-Only (Audit Trail, Lineage)
    # ========================================================================
    def test_governance_only_audit_and_lineage(self, agent):
        """Governance signals → lineage enabled, Purview, Monitor."""
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.FABRIC_PIPELINE,
            is_streaming=False,
        )
        requirements = [
            self._make_requirement(
                "Data lineage and provenance tracking required",
                RequirementCategory.COMPLIANCE,
            ),
            self._make_requirement("Complete audit trail for all data movements"),
        ]

        result = agent.run(ingestion_arch, requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should enable governance
        assert output.governance.lineage_enabled is True
        assert output.governance.lineage_tool == "Microsoft Purview"
        assert output.governance.audit_logging == "Azure Monitor"

    # ========================================================================
    # Test 8: Empty Requirements
    # ========================================================================
    def test_empty_requirements(self, agent):
        """Empty requirements → defaults (Fabric, no PII, basic quality)."""
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.FABRIC_PIPELINE,
            is_streaming=False,
        )
        requirements = []

        result = agent.run(ingestion_arch, requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should default to Fabric
        assert output.tool == TransformationTool.FABRIC_PIPELINE
        assert output.complexity_score == 0

        # Should have basic quality rules
        assert len(output.data_quality.rules) > 0
        assert output.data_quality.has_pii is False

        # Should not have governance by default
        assert output.governance.lineage_enabled is False

    # ========================================================================
    # Test 9: Serialization Round-Trip
    # ========================================================================
    def test_output_serialization_roundtrip(self, agent):
        """Validate JSON serialization round-trip."""
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.FABRIC_PIPELINE,
            is_streaming=False,
        )
        requirements = [
            self._make_requirement("GDPR compliance, PII masking, lineage required"),
        ]

        result = agent.run(ingestion_arch, requirements)
        output = result.output

        # Should serialize to JSON without errors
        json_dict = output.model_dump(mode="json")
        assert json_dict is not None
        assert json_dict["id"] is not None
        assert json_dict["tool"] is not None

        # Should deserialize back
        from bid_acceleration_engine.schemas.transformation import TransformationArchitecture

        reconstructed = TransformationArchitecture(**json_dict)
        assert reconstructed.tool == output.tool
        assert reconstructed.is_streaming == output.is_streaming
        assert len(reconstructed.data_quality.rules) == len(output.data_quality.rules)

    # ========================================================================
    # Test 10: Deduplication & Reconciliation
    # ========================================================================
    def test_deduplication_and_reconciliation_rules(self, agent):
        """Data quality: dedup and reconciliation → rules generated."""
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.FABRIC_PIPELINE,
            is_streaming=False,
        )
        requirements = [
            self._make_requirement("Deduplication on customer ID required"),
            self._make_requirement("Reconciliation checks: input ≈ output ±5%"),
        ]

        result = agent.run(ingestion_arch, requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should detect dedup and reconciliation needs
        assert output.data_quality.deduplication_required is True
        assert output.data_quality.reconciliation_required is True

        # Should have corresponding rules
        assert any(rule.tier == "deduplication" for rule in output.data_quality.rules)
        assert any(rule.tier == "reconciliation" for rule in output.data_quality.rules)

    # ========================================================================
    # Test 11: Complex Streaming with ML
    # ========================================================================
    def test_streaming_with_ml_complexity(self, agent):
        """Streaming + ML → Stream Analytics with complexity factors."""
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.EVENT_HUBS_STREAM_ANALYTICS,
            is_streaming=True,
            detected_freshness="real-time",
        )
        requirements = [
            self._make_requirement("Real-time event streaming and processing"),
            self._make_requirement("Predictive anomaly detection model scoring"),
        ]

        result = agent.run(ingestion_arch, requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should recommend Stream Analytics (streaming dominates)
        assert output.tool == TransformationTool.STREAM_ANALYTICS
        assert output.is_streaming is True

        # Should still have complexity factors recorded
        assert len(output.complexity_factors) > 0

    # ========================================================================
    # Integration Tests with UK RFP Fixtures
    # ========================================================================
    def test_integration_local_council_rfp(self, agent, uk_local_council_requirements):
        """Integration: Local Council RFP fixture."""
        # Create a corresponding Phase 3 ingestion architecture
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.DATA_FACTORY,
            is_streaming=False,
            on_premise_sources=["Oracle", "Sql Server"],
            detected_sources=["Case Management"],
            detected_freshness="daily",
        )

        result = agent.run(ingestion_arch, uk_local_council_requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should recommend Data Factory or Fabric (local council, batch)
        assert output.tool in (TransformationTool.FABRIC_PIPELINE, TransformationTool.DATA_FACTORY_DATAFLOW)

        # Should detect UK government compliance
        assert output.governance.uk_data_residency is True
        assert "GDPR" in output.governance.compliance_frameworks

    def test_integration_nhs_rfp(self, agent, nhs_trust_requirements):
        """Integration: NHS Trust RFP fixture."""
        # Create a corresponding Phase 3 ingestion architecture
        ingestion_arch = self._make_ingestion_arch(
            tool=IngestionTool.DATA_FACTORY,
            is_streaming=False,
            on_premise_sources=["Sql Server", "Oracle"],
            detected_freshness="daily",
        )

        result = agent.run(ingestion_arch, nhs_trust_requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should detect NHS DSPT compliance
        assert "NHS DSPT" in output.governance.compliance_frameworks

        # Should have 7-year retention
        assert output.governance.retention_policy is not None
        assert "7 year" in output.governance.retention_policy.lower()

        # Should enable lineage
        assert output.governance.lineage_enabled is True
