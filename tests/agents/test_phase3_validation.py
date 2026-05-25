"""Phase 3 validation tests against realistic UK government RFP scenarios."""

import json
from datetime import datetime

import pytest

from bid_acceleration_engine.agents.data_ingestion_agent.agent import DataIngestionAgent
from bid_acceleration_engine.schemas.requirements import ExtractedRequirement


class TestPhase3Validation:
    """Validate Phase 3 recommendations against realistic UK government RFPs."""

    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        return DataIngestionAgent("data_ingestion_agent")

    def _print_recommendation(self, scenario_name: str, requirements: list[ExtractedRequirement], agent):
        """Print Phase 3 recommendation for manual review."""
        result = agent.run(requirements)
        output = result.output

        print("\n" + "=" * 80)
        print(f"SCENARIO: {scenario_name}")
        print("=" * 80)
        print(f"Status: {result.status.value}")
        print(f"\nInput Requirements: {len(requirements)}")
        for i, req in enumerate(requirements, 1):
            print(f"  {i}. {req.source_text[:70]}...")

        print(f"\n--- PHASE 3 RECOMMENDATION ---")
        print(f"Tool: {output.tool.value}")
        print(f"Is Streaming: {output.is_streaming}")
        print(f"Complexity Score: {output.complexity_score}")
        print(f"Detected Sources: {output.detected_sources}")
        print(f"On-Premise Sources: {output.on_premise_sources}")
        print(f"Data Volume: {output.detected_volume}")
        print(f"Freshness Requirement: {output.detected_freshness}")
        print(f"Dependencies: {output.detected_dependencies}")

        print(f"\n--- DECISION RATIONALE ---")
        print(f"{output.tool_decision}")
        if output.complexity_factors:
            print(f"Complexity Factors:")
            for factor in output.complexity_factors:
                print(f"  - {factor}")

        print(f"\n--- ARCHITECTURE ---")
        print(f"Pattern: {output.architecture_pattern}")
        print(f"Key Services: {output.key_services}")

        if output.shir_config:
            print(f"\n--- SHIR CONFIGURATION ---")
            print(f"Required: {output.shir_config.required}")
            print(f"Placement: {output.shir_config.placement}")
            print(f"HA Required: {output.shir_config.ha_required}")
            if output.shir_config.ha_required:
                print(f"HA Nodes: {output.shir_config.ha_nodes}")
            print(f"Network Security Layer: {output.shir_config.network_security_layer}")
            print(f"Authentication Method: {output.shir_config.authentication_method}")
            print(f"Managed Identity Possible: {output.shir_config.managed_identity_possible}")
            print(f"Encryption in Transit: {output.shir_config.encryption_in_transit}")
            print(f"Encryption at Rest: {output.shir_config.encryption_at_rest}")
            print(f"Column-Level Encryption for PII: {output.shir_config.column_level_encryption_for_pii}")
            print(f"UK Region Required: {output.shir_config.uk_region_required}")
            if output.shir_config.azure_regions:
                print(f"Azure Regions: {output.shir_config.azure_regions}")
            print(f"GDPR Compliant: {output.shir_config.gdpr_compliant}")
            print(f"Audit Logging Required: {output.shir_config.audit_logging_required}")
            print(f"Data Movement Audit Trail: {output.shir_config.data_movement_audit_trail}")
            print(f"Concurrent Connections: {output.shir_config.concurrent_connections}")
            print(f"Estimated Daily Volume GB: {output.shir_config.estimated_daily_volume_gb}")

            if output.shir_config.firewall_rules:
                print(f"\nFirewall Rules:")
                for rule in output.shir_config.firewall_rules:
                    print(f"  - {rule}")

            if output.shir_config.security_recommendations:
                print(f"\nSecurity Recommendations:")
                for rec in output.shir_config.security_recommendations:
                    print(f"  - {rec}")

            if output.shir_config.compliance_checklist:
                print(f"\nCompliance Checklist ({len(output.shir_config.compliance_checklist)} items):")
                for item in output.shir_config.compliance_checklist[:5]:
                    print(f"  {item}")
                if len(output.shir_config.compliance_checklist) > 5:
                    print(f"  ... and {len(output.shir_config.compliance_checklist) - 5} more items")

        print(f"\n--- CONSIDERATIONS ---")
        for consideration in output.considerations:
            print(f"  - {consideration}")

        print("\n" + "=" * 80)
        return result

    def test_scenario_local_council(self, agent, uk_local_council_requirements):
        """Validate Local Council data analytics scenario."""
        result = self._print_recommendation(
            "Local Council Data Analytics",
            uk_local_council_requirements,
            agent,
        )
        output = result.output

        # Basic assertions to ensure reasonable output
        assert result.status.value == "success"
        assert output.tool is not None
        assert not output.is_streaming  # Batch processing

    def test_scenario_nhs_trust(self, agent, nhs_trust_requirements):
        """Validate NHS Trust hospital systems scenario."""
        result = self._print_recommendation(
            "NHS Trust Hospital Systems Integration",
            nhs_trust_requirements,
            agent,
        )
        output = result.output

        assert result.status.value == "success"
        assert output.tool is not None
        assert output.shir_config is not None
        assert len(output.on_premise_sources) > 0

    def test_scenario_transport_authority(self, agent, transport_authority_requirements):
        """Validate Transport Authority intelligent traffic scenario."""
        result = self._print_recommendation(
            "Transport Authority Intelligent Traffic System",
            transport_authority_requirements,
            agent,
        )
        output = result.output

        assert result.status.value == "success"
        assert output.tool is not None
        assert output.is_streaming  # Real-time processing expected

    def test_scenario_water_authority(self, agent, water_authority_requirements):
        """Validate Water Authority customer service scenario."""
        result = self._print_recommendation(
            "Water Authority Customer Service Platform",
            water_authority_requirements,
            agent,
        )
        output = result.output

        assert result.status.value == "success"
        assert output.tool is not None
        assert not output.is_streaming  # Batch billing cycles
        assert output.shir_config is not None
        assert len(output.on_premise_sources) > 0
