"""Phase 3 Data Ingestion Agent spec-driven tests."""

from datetime import datetime
from uuid import uuid4

import pytest

from bid_acceleration_engine.agents.data_ingestion_agent.agent import DataIngestionAgent
from bid_acceleration_engine.schemas.data_ingestion import IngestionTool
from bid_acceleration_engine.schemas.requirements import (
    EstimatedComplexity,
    ExtractedRequirement,
    RequirementCategory,
    RequirementPriority,
)
from bid_acceleration_engine.schemas.results import AgentStatus


class TestDataIngestionAgent:
    """Test Data Ingestion Agent against spec requirements."""

    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        return DataIngestionAgent("data_ingestion_agent")

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

    # ========================================================================
    # Test 1: Simple On-Prem Batch (Fabric + Basic SHIR)
    # ========================================================================
    def test_simple_onprem_batch_recommends_fabric(self, agent):
        """Simple on-prem single source → Fabric Pipelines."""
        requirements = [
            self._make_requirement("Need to ingest from single on-prem SQL Server"),
            self._make_requirement("Daily batch refresh, 500GB data"),
        ]

        result = agent.run(requirements)

        assert result.status == AgentStatus.SUCCESS
        assert result.output is not None
        output = result.output

        # Should recommend Fabric Pipelines (low complexity)
        assert output.tool == IngestionTool.FABRIC_PIPELINE
        assert output.complexity_score is not None
        assert output.complexity_score < 3

        # Should have on-prem sources
        assert len(output.on_premise_sources) > 0
        assert "Sql Server" in output.on_premise_sources

        # Should have SHIR config
        assert output.shir_config is not None
        assert output.shir_config.required is True
        assert output.shir_config.placement == "on-prem"
        assert output.shir_config.ha_required is False
        assert output.shir_config.ha_nodes == 1
        assert output.shir_config.encryption_in_transit == "tls-1-2-plus"
        assert output.shir_config.network_security_layer == "shir-only"

    # ========================================================================
    # Test 2: Complex Multi-Source Enterprise (ADF + HA SHIR)
    # ========================================================================
    def test_complex_multisource_enterprise_recommends_adf(self, agent):
        """Complex 8 sources, enterprise governance → Data Factory + HA."""
        requirements = [
            self._make_requirement(
                "Consolidate 8 legacy systems (Oracle EBS, SQL Server, case management systems)"
            ),
            self._make_requirement("2TB data, daily refresh"),
            self._make_requirement("Enterprise governance required, 99.9% uptime SLA"),
        ]

        result = agent.run(requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should recommend Data Factory (high complexity)
        assert output.tool == IngestionTool.DATA_FACTORY
        assert output.complexity_score is not None
        assert output.complexity_score >= 3

        # Should have on-prem sources
        assert len(output.on_premise_sources) > 0

        # Should have HA SHIR
        assert output.shir_config is not None
        assert output.shir_config.ha_required is True
        assert output.shir_config.ha_nodes == 3
        assert output.shir_config.failover_strategy == "auto-registered-nodes"
        assert output.shir_config.monitoring_enabled is True
        assert output.shir_config.data_movement_audit_trail is True

    # ========================================================================
    # Test 3: UK Government GDPR (Data Factory + UK Regions + Audit)
    # ========================================================================
    def test_uk_government_gdpr_compliance(self, agent):
        """UK government RFP → Data Factory + UK regions + GDPR checklist."""
        requirements = [
            self._make_requirement(
                "Consolidate data from Oracle, SQL Server, PostgreSQL, MySQL, and legacy case management systems",
                RequirementCategory.TECHNICAL,
            ),
            self._make_requirement("GDPR compliance required, UK data residency", RequirementCategory.COMPLIANCE),
            self._make_requirement("Audit trail mandatory for all data access", RequirementCategory.COMPLIANCE),
        ]

        result = agent.run(requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should recommend Data Factory for 5+ sources
        assert output.tool == IngestionTool.DATA_FACTORY

        # Should have SHIR config
        assert output.shir_config is not None
        assert output.shir_config.uk_region_required is True
        assert output.shir_config.azure_regions == ["UK South", "UK West"]
        assert output.shir_config.gdpr_compliant is True
        assert output.shir_config.audit_logging_required is True
        assert output.shir_config.column_level_encryption_for_pii is True

        # Should have GDPR compliance checklist
        assert len(output.shir_config.compliance_checklist) > 0
        assert any("GDPR" in item for item in output.shir_config.compliance_checklist)
        assert any("data residency" in item.lower() for item in output.shir_config.compliance_checklist)

    # ========================================================================
    # Test 4: Streaming (Real-Time Events)
    # ========================================================================
    def test_streaming_recommends_event_hubs(self, agent):
        """Streaming requirement → Event Hubs + Stream Analytics."""
        requirements = [
            self._make_requirement("Ingest real-time streaming events from Kafka"),
            self._make_requirement("Continuous processing, low-latency requirements"),
        ]

        result = agent.run(requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should detect streaming
        assert output.is_streaming is True

        # Should recommend Event Hubs + Stream Analytics
        assert output.tool == IngestionTool.EVENT_HUBS_STREAM_ANALYTICS
        assert output.complexity_score is None

        # Should NOT have SHIR (streaming doesn't need SHIR)
        assert output.shir_config is None
        assert "Event Hubs" in output.architecture_pattern
        assert "Stream Analytics" in output.architecture_pattern

    # ========================================================================
    # Test 5: Enterprise Multi-Site with ExpressRoute
    # ========================================================================
    def test_enterprise_expressroute_recommendation(self, agent):
        """Enterprise multi-site → ExpressRoute recommendation."""
        requirements = [
            self._make_requirement("Multi-site on-prem Oracle + SQL Server"),
            self._make_requirement("Enterprise security requirement, high-security needed"),
            self._make_requirement("99.95% uptime SLA"),
        ]

        result = agent.run(requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should have SHIR config with ExpressRoute
        assert output.shir_config is not None
        assert output.shir_config.network_security_layer == "shir-plus-expressroute"
        assert output.shir_config.ha_required is True

        # Should recommend ExpressRoute
        assert any("ExpressRoute" in rec for rec in output.shir_config.security_recommendations)

    # ========================================================================
    # Test 6: Healthcare (NHS DSPT Compliance)
    # ========================================================================
    def test_healthcare_nhs_dspt_compliance(self, agent):
        """Healthcare RFP → NHS DSPT checklist."""
        requirements = [
            self._make_requirement(
                "NHS healthcare data integration, on-prem SQL Server",
                RequirementCategory.COMPLIANCE,
            ),
            self._make_requirement(
                "DSPT compliance required, encryption mandatory",
                RequirementCategory.COMPLIANCE,
            ),
        ]

        result = agent.run(requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should have SHIR config
        assert output.shir_config is not None
        assert output.shir_config.encryption_at_rest is True
        assert output.shir_config.column_level_encryption_for_pii is True
        assert output.shir_config.uk_region_required is True

        # Should have NHS DSPT checklist
        assert len(output.shir_config.compliance_checklist) > 0
        assert any("NHS" in item or "DSPT" in item for item in output.shir_config.compliance_checklist)

    # ========================================================================
    # Test 7: Cloud-Native Streaming (No On-Prem)
    # ========================================================================
    def test_cloud_native_streaming_no_shir(self, agent):
        """Cloud-native streaming → No SHIR required."""
        requirements = [
            self._make_requirement("Real-time event streaming from cloud APIs"),
            self._make_requirement("Continuous processing, cloud-native sources only"),
        ]

        result = agent.run(requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Streaming detected
        assert output.is_streaming is True

        # No on-prem sources
        assert len(output.on_premise_sources) == 0

        # No SHIR config
        assert output.shir_config is None

    # ========================================================================
    # Test 8: Modern Azure (Managed Identity)
    # ========================================================================
    def test_modern_azure_managed_identity(self, agent):
        """Modern Azure environment → Managed Identity recommended."""
        requirements = [
            self._make_requirement("Modern Azure environment, managed identity support"),
            self._make_requirement("On-prem SQL Server, single source"),
        ]

        result = agent.run(requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should have SHIR config
        assert output.shir_config is not None
        assert output.shir_config.managed_identity_possible is True
        assert output.shir_config.authentication_method == "managed-identity"

        # Should recommend Managed Identity
        assert any("Managed Identity" in rec for rec in output.shir_config.security_recommendations)

    # ========================================================================
    # Test 9: Legacy Domain (Windows Auth)
    # ========================================================================
    def test_legacy_domain_windows_auth(self, agent):
        """Windows domain environment → Windows authentication."""
        requirements = [
            self._make_requirement("Windows domain environment, on-prem SQL Server"),
            self._make_requirement("Kerberos support available"),
        ]

        result = agent.run(requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should have SHIR config
        assert output.shir_config is not None
        assert output.shir_config.authentication_method == "windows-auth"
        assert output.shir_config.managed_identity_possible is False

    # ========================================================================
    # Test 10: Streaming False Positive
    # ========================================================================
    def test_streaming_false_positive_dashboard(self, agent):
        """Dashboard use case (not true streaming) with on-prem source."""
        requirements = [
            self._make_requirement("Frequent dashboard refresh from on-prem data sources"),
            self._make_requirement("On-prem SQL Server as data source, daily batch updates"),
        ]

        result = agent.run(requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should NOT detect as streaming (batch updates, not event streaming)
        assert output.is_streaming is False

        # Should recommend Fabric (simple)
        assert output.tool == IngestionTool.FABRIC_PIPELINE

        # Should still have SHIR (on-prem source)
        assert output.shir_config is not None
        assert output.shir_config.required is True

    # ========================================================================
    # Integration Tests with UK RFP Fixtures
    # ========================================================================
    def test_integration_local_council_rfp(self, agent, uk_local_council_requirements):
        """Integration: Local Council RFP from fixture."""
        # uk_local_council_requirements comes from conftest.py fixture
        result = agent.run(uk_local_council_requirements)

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should recommend Data Factory (8 systems, governance)
        assert output.tool == IngestionTool.DATA_FACTORY
        assert output.complexity_score is not None
        assert output.complexity_score >= 3

        # Should have SHIR for on-prem sources
        assert output.shir_config is not None

        # Should detect UK government compliance
        assert output.shir_config.uk_region_required is True
        assert "UK South" in output.shir_config.azure_regions
        assert output.shir_config.audit_logging_required is True

    # ========================================================================
    # Edge Cases & Validation
    # ========================================================================
    def test_empty_requirements(self, agent):
        """Handle empty requirement list gracefully."""
        result = agent.run([])

        assert result.status == AgentStatus.SUCCESS
        output = result.output

        # Should default to Fabric (no complexity signals)
        assert output.tool == IngestionTool.FABRIC_PIPELINE
        assert output.complexity_score == 0
        assert output.shir_config is None

    def test_output_serialization_roundtrip(self, agent):
        """Validate JSON serialization round-trip."""
        requirements = [
            self._make_requirement("On-prem SQL Server, GDPR compliance, UK government"),
        ]

        result = agent.run(requirements)
        output = result.output

        # Should serialize to JSON without errors
        json_dict = output.model_dump(mode="json")
        assert json_dict is not None
        assert json_dict["id"] is not None
        assert json_dict["tool"] is not None

        # Should deserialize back
        from bid_acceleration_engine.schemas.data_ingestion import DataIngestionArchitecture

        reconstructed = DataIngestionArchitecture(**json_dict)
        assert reconstructed.tool == output.tool
        assert reconstructed.shir_config is not None or output.shir_config is None

    def test_firewall_rules_generation(self, agent):
        """Validate firewall rules are generated for on-prem sources."""
        requirements = [
            self._make_requirement("On-prem SQL Server and Oracle database"),
        ]

        result = agent.run(requirements)
        output = result.output

        # Should have firewall rules
        assert output.shir_config is not None
        assert len(output.shir_config.firewall_rules) > 0
        assert any("1433" in rule for rule in output.shir_config.firewall_rules)  # SQL Server
        assert any("1521" in rule for rule in output.shir_config.firewall_rules)  # Oracle
