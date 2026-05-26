"""Phase 1.5 Enhancement Agent tests — validation against golden set.

These tests verify that EnhancedBidIntakeAgent correctly enhances Phase 1
output, addressing the 5 documented gaps (title, date, sections, categorization, issuer).
"""

import json
from datetime import datetime
from pathlib import Path

import pytest

from bid_acceleration_engine.agents.bid_intake_agent.agent import BidIntakeAgent
from bid_acceleration_engine.agents.enhanced_bid_intake_agent.agent import (
    EnhancedBidIntakeAgent,
)
from bid_acceleration_engine.schemas.results import AgentStatus


@pytest.fixture
def golden_set():
    """Load the golden set metadata for validation."""
    golden_path = Path(__file__).parent.parent / "fixtures" / "phase1_5_golden_set.json"
    with open(golden_path) as f:
        return json.load(f)


@pytest.fixture
def bid_intake_agent():
    """Create a BidIntakeAgent instance for Phase 1."""
    return BidIntakeAgent("bid_intake_agent")


@pytest.fixture
def enhanced_agent():
    """Create an EnhancedBidIntakeAgent instance for Phase 1.5."""
    return EnhancedBidIntakeAgent("enhanced_bid_intake_agent")


class TestPhase1_5EnhancementAgent:
    """Validate Phase 1.5 Enhancement Agent against all fixtures and golden set."""

    # ========================================================================
    # UK RFP FIXTURES — Title Correction
    # ========================================================================

    @pytest.mark.parametrize(
        "fixture_name,expected_title",
        [
            ("uk_local_council_data_analytics", "Integrated Council Data Analytics Platform"),
            ("uk_nhs_trust_population_health", "Integrated Population Health Analytics System"),
            ("uk_transport_network_data_system", "Multi-Modal Transport Network Analytics Platform"),
            ("uk_university_research_data_repository", "Research Data Management and Discovery Platform"),
            ("uk_water_authority_environmental_data", "Water Quality and Environmental Monitoring Data Platform"),
        ],
    )
    def test_corrects_uk_rfp_titles(
        self, fixture_name, expected_title, bid_intake_agent, enhanced_agent, tmp_path, golden_set
    ):
        """All 5 UK RFPs have document-type headers as titles. Phase 1.5 should correct them."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_bids" / f"{fixture_name}.txt"
        phase1_output = tmp_path / "phase1.json"

        # Phase 1
        result1 = bid_intake_agent.run(fixture_path, phase1_output)
        assert result1.status == AgentStatus.SUCCESS
        phase1_doc = result1.output

        # Phase 1 gets the title wrong (document-type header)
        assert phase1_doc.metadata.title != expected_title

        # Phase 1.5
        result1_5 = enhanced_agent.run(phase1_doc)
        assert result1_5.status == AgentStatus.SUCCESS
        enhanced_doc = result1_5.output

        # Phase 1.5 corrects the title
        assert enhanced_doc.metadata.title == expected_title
        assert enhanced_doc.metadata.title_confidence > 0.9
        assert enhanced_doc.metadata.title_source == "solicitation_title_field"

        # Validate against golden set
        golden = golden_set["fixtures"][fixture_name]["golden_truth"]
        assert enhanced_doc.metadata.title == golden["title"]

    # ========================================================================
    # US RFP FIXTURES — Title Cleanup (strip prefixes)
    # ========================================================================

    def test_strips_rfp_prefix_from_simple_rfp(self, bid_intake_agent, enhanced_agent, tmp_path):
        """simple_rfp.txt has 'REQUEST FOR PROPOSAL: ENTERPRISE...' — Phase 1.5 should strip prefix."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_bids" / "simple_rfp.txt"
        phase1_output = tmp_path / "phase1.json"

        result1 = bid_intake_agent.run(fixture_path, phase1_output)
        phase1_doc = result1.output

        # Phase 1 extracts: "REQUEST FOR PROPOSAL: ENTERPRISE CLOUD INFRASTRUCTURE MODERNIZATION"
        assert phase1_doc.metadata.title.startswith("REQUEST FOR PROPOSAL:")

        result1_5 = enhanced_agent.run(phase1_doc)
        enhanced_doc = result1_5.output

        # Phase 1.5 strips the prefix
        assert enhanced_doc.metadata.title == "ENTERPRISE CLOUD INFRASTRUCTURE MODERNIZATION"

    def test_strips_rfp_dash_prefix_from_complex_rfp(self, bid_intake_agent, enhanced_agent, tmp_path):
        """complex_rfp.txt has 'RFP - DATA ANALYTICS...' — Phase 1.5 should strip 'RFP -' prefix."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_bids" / "complex_rfp.txt"
        phase1_output = tmp_path / "phase1.json"

        result1 = bid_intake_agent.run(fixture_path, phase1_output)
        phase1_doc = result1.output

        result1_5 = enhanced_agent.run(phase1_doc)
        enhanced_doc = result1_5.output

        # Phase 1.5 strips the prefix
        assert enhanced_doc.metadata.title == "DATA ANALYTICS PLATFORM DEVELOPMENT"

    # ========================================================================
    # DATE DISAMBIGUATION
    # ========================================================================

    @pytest.mark.parametrize(
        "fixture_name",
        [
            "uk_local_council_data_analytics",
            "uk_nhs_trust_population_health",
            "uk_transport_network_data_system",
            "uk_university_research_data_repository",
            "uk_water_authority_environmental_data",
        ],
    )
    def test_all_uk_rfps_have_submission_deadline(self, fixture_name, bid_intake_agent, enhanced_agent, tmp_path):
        """Parametrized test: all UK RFPs should get due_date_type = submission_deadline."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_bids" / f"{fixture_name}.txt"
        phase1_output = tmp_path / "phase1.json"

        result1 = bid_intake_agent.run(fixture_path, phase1_output)
        result1_5 = enhanced_agent.run(result1.output)
        enhanced_doc = result1_5.output

        assert enhanced_doc.metadata.due_date_type == "submission_deadline"

    def test_complex_rfp_date_disambiguation(self, bid_intake_agent, enhanced_agent, tmp_path):
        """complex_rfp.txt has 3 dates: Posted, Closing, Questions Due.
        Phase 1.5 should pick Closing (2026-04-15) over Questions Due.
        """
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_bids" / "complex_rfp.txt"
        phase1_output = tmp_path / "phase1.json"

        result1 = bid_intake_agent.run(fixture_path, phase1_output)
        result1_5 = enhanced_agent.run(result1.output)
        enhanced_doc = result1_5.output

        # Closing date is April 15, 2026
        expected_date = datetime(2026, 4, 15).date()
        assert enhanced_doc.metadata.due_date.date() == expected_date

    # ========================================================================
    # SECTION DETECTION — Title-Case Headings
    # ========================================================================

    def test_transport_detects_titlecase_evaluation_factors_heading(self, bid_intake_agent, enhanced_agent, tmp_path):
        """uk_transport_network_data_system.txt has 'Evaluation Factors' (title-case) at line 69.
        Phase 1 misses it. Phase 1.5 should detect it.
        """
        fixture_path = (
            Path(__file__).parent.parent / "fixtures" / "sample_bids" / "uk_transport_network_data_system.txt"
        )
        phase1_output = tmp_path / "phase1.json"

        result1 = bid_intake_agent.run(fixture_path, phase1_output)
        phase1_doc = result1.output
        phase1_headings = [s.heading for s in phase1_doc.sections if s.heading]

        # Phase 1 misses it
        assert "Evaluation Factors" not in phase1_headings

        # Phase 1.5 detects it
        result1_5 = enhanced_agent.run(phase1_doc)
        enhanced_doc = result1_5.output
        enhanced_headings = [s.heading for s in enhanced_doc.sections if s.heading]

        assert "Evaluation Factors" in enhanced_headings

    # ========================================================================
    # REQUIREMENT CATEGORIZATION — Mandatory/Optional Counts
    # ========================================================================

    @pytest.mark.parametrize(
        "fixture_name,expected_mandatory,expected_optional",
        [
            ("uk_local_council_data_analytics", 8, 5),
            ("uk_nhs_trust_population_health", 8, 5),
            ("uk_transport_network_data_system", 8, 4),
            ("uk_university_research_data_repository", 7, 5),
            ("uk_water_authority_environmental_data", 8, 6),
        ],
    )
    def test_requirement_counts_match_golden_set(
        self, fixture_name, expected_mandatory, expected_optional, bid_intake_agent, enhanced_agent, tmp_path
    ):
        """Phase 1.5 should count mandatory/optional items correctly."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_bids" / f"{fixture_name}.txt"
        phase1_output = tmp_path / "phase1.json"

        result1 = bid_intake_agent.run(fixture_path, phase1_output)
        result1_5 = enhanced_agent.run(result1.output)
        enhanced_doc = result1_5.output

        assert enhanced_doc.metadata.mandatory_count == expected_mandatory
        assert enhanced_doc.metadata.optional_count == expected_optional

    # ========================================================================
    # ISSUER CONFIDENCE — Compound Names
    # ========================================================================

    def test_issuer_confidence_penalty_for_compound_name(self, bid_intake_agent, enhanced_agent, tmp_path):
        """uk_university_research_data_repository.txt has compound issuer:
        'Northern Universities Consortium (8 institutions)'
        Phase 1.5 should detect parenthetical and apply confidence penalty (0.95).
        """
        fixture_path = (
            Path(__file__).parent.parent / "fixtures" / "sample_bids" / "uk_university_research_data_repository.txt"
        )
        phase1_output = tmp_path / "phase1.json"

        result1 = bid_intake_agent.run(fixture_path, phase1_output)
        result1_5 = enhanced_agent.run(result1.output)
        enhanced_doc = result1_5.output

        # Issuer should be preserved correctly
        assert "Northern Universities Consortium" in enhanced_doc.metadata.issuer
        assert "(8 institutions)" in enhanced_doc.metadata.issuer

        # Confidence should be reduced to 0.95
        assert enhanced_doc.metadata.issuer_confidence == 0.95

    # ========================================================================
    # CORRECTIONS LOG
    # ========================================================================

    def test_corrections_applied_log_is_nonempty(self, bid_intake_agent, enhanced_agent, tmp_path):
        """Phase 1.5 should log all corrections made."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_bids" / "uk_local_council_data_analytics.txt"
        phase1_output = tmp_path / "phase1.json"

        result1 = bid_intake_agent.run(fixture_path, phase1_output)
        result1_5 = enhanced_agent.run(result1.output)
        enhanced_doc = result1_5.output

        assert len(enhanced_doc.corrections_applied) > 0
        # At least one correction should be about the title
        assert any("title:" in c for c in enhanced_doc.corrections_applied)

    # ========================================================================
    # TYPE COMPATIBILITY
    # ========================================================================

    def test_enhanced_doc_is_valid_bid_document(self, bid_intake_agent, enhanced_agent, tmp_path):
        """EnhancedBidDocument is-a BidDocument (Liskov substitution)."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_bids" / "uk_local_council_data_analytics.txt"
        phase1_output = tmp_path / "phase1.json"

        result1 = bid_intake_agent.run(fixture_path, phase1_output)
        result1_5 = enhanced_agent.run(result1.output)
        enhanced_doc = result1_5.output

        # Should be usable as a BidDocument (duck typing)
        assert hasattr(enhanced_doc, "id")
        assert hasattr(enhanced_doc, "metadata")
        assert hasattr(enhanced_doc, "raw_text")
        assert hasattr(enhanced_doc, "sections")

    # ========================================================================
    # SERIALIZATION
    # ========================================================================

    def test_serialization_round_trip(self, bid_intake_agent, enhanced_agent, tmp_path):
        """EnhancedBidDocument should serialize and deserialize correctly."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_bids" / "uk_local_council_data_analytics.txt"
        phase1_output = tmp_path / "phase1.json"

        result1 = bid_intake_agent.run(fixture_path, phase1_output)
        result1_5 = enhanced_agent.run(result1.output)
        enhanced_doc = result1_5.output

        # Serialize to JSON
        json_str = enhanced_doc.model_dump_json()

        # Deserialize from JSON
        from bid_acceleration_engine.schemas.enhanced_bid import EnhancedBidDocument

        restored = EnhancedBidDocument.model_validate_json(json_str)

        # Verify key fields match
        assert restored.metadata.title == enhanced_doc.metadata.title
        assert restored.metadata.title_confidence == enhanced_doc.metadata.title_confidence
        assert restored.metadata.mandatory_count == enhanced_doc.metadata.mandatory_count
        assert len(restored.corrections_applied) == len(enhanced_doc.corrections_applied)
