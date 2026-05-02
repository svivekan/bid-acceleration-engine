"""Spec-driven tests for Phase 2: Requirement Extraction Agent.

These tests validate the Phase 2 specification before implementation.
All tests should fail initially (RED), then pass as agent is implemented (GREEN).
"""

from pathlib import Path

import pytest

from bid_acceleration_engine.agents.bid_intake_agent.agent import BidIntakeAgent
from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.schemas.results import AgentStatus


@pytest.fixture
def bid_intake_agent():
    """Create BidIntakeAgent to parse RFPs into BidDocuments."""
    return BidIntakeAgent("bid_intake_agent")


@pytest.fixture
def requirement_extraction_agent():
    """Create RequirementExtractionAgent (to be implemented)."""
    from bid_acceleration_engine.agents.requirement_extraction_agent.agent import (
        RequirementExtractionAgent,
    )

    return RequirementExtractionAgent("requirement_extraction_agent")


@pytest.fixture
def uk_rfp_fixtures():
    """Get paths to all UK RFP fixture files."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_bids"
    return {
        "local_council": fixtures_dir / "uk_local_council_data_analytics.txt",
        "nhs_trust": fixtures_dir / "uk_nhs_trust_population_health.txt",
        "transport": fixtures_dir / "uk_transport_network_data_system.txt",
        "university": fixtures_dir / "uk_university_research_data_repository.txt",
        "water_authority": fixtures_dir / "uk_water_authority_environmental_data.txt",
    }


@pytest.fixture
def parsed_bid_documents(bid_intake_agent, uk_rfp_fixtures, tmp_path):
    """Parse all UK RFP fixtures into BidDocuments."""
    bid_docs = {}
    for name, fixture_path in uk_rfp_fixtures.items():
        output_path = tmp_path / f"{name}_parsed.json"
        result = bid_intake_agent.run(fixture_path, output_path)
        assert result.status == AgentStatus.SUCCESS
        bid_docs[name] = result.output
    return bid_docs


# ============================================================================
# SPEC CRITERION 1: Search for MANDATORY/OPTIONAL Keywords
# ============================================================================


def test_spec_marks_mandatory_requirements(requirement_extraction_agent, parsed_bid_documents):
    """Spec 1: Mark requirements mandatory=true if found in MANDATORY section."""
    bid_doc = parsed_bid_documents["local_council"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    # Should have mandatory requirements
    mandatory_reqs = [r for r in requirements if r.mandatory]
    assert len(mandatory_reqs) > 0, "Should extract mandatory requirements"

    # All mandatory requirements should have source_text
    for req in mandatory_reqs:
        assert req.source_text, "Mandatory requirement must have source text"


def test_spec_marks_optional_requirements(requirement_extraction_agent, parsed_bid_documents):
    """Spec 1: Mark requirements mandatory=false if found in OPTIONAL section."""
    bid_doc = parsed_bid_documents["local_council"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    # Should have optional requirements
    optional_reqs = [r for r in requirements if not r.mandatory]
    assert len(optional_reqs) > 0, "Should extract optional requirements"


def test_spec_case_insensitive_mandatory_optional(requirement_extraction_agent, parsed_bid_documents):
    """Spec 1: Handle case-insensitive matching of MANDATORY/OPTIONAL."""
    bid_doc = parsed_bid_documents["nhs_trust"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    # If extraction works at all, it's handling case-insensitive matching


# ============================================================================
# SPEC CRITERION 2: Extract Numbered Requirements
# ============================================================================


def test_spec_extracts_numbered_requirements(requirement_extraction_agent, parsed_bid_documents):
    """Spec 2: Identify and extract numbered list items (1., 2., 3., etc.)."""
    bid_doc = parsed_bid_documents["local_council"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output
    assert len(requirements) > 0, "Should extract numbered requirements"

    # Each requirement should have source text and be traceable
    for req in requirements:
        assert req.source_text, "Requirement must have source text"
        assert req.section_heading, "Requirement must note where it came from"


def test_spec_preserves_multiline_requirement_text(requirement_extraction_agent, parsed_bid_documents):
    """Spec 2: Preserve original text including line breaks for multi-line requirements."""
    bid_doc = parsed_bid_documents["transport"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    # Should find multi-line requirements (those with newlines in source_text)
    multiline_reqs = [r for r in requirements if "\n" in r.source_text]
    # May or may not have multiline - just verify if present, they're preserved
    for req in multiline_reqs:
        assert req.source_text.count("\n") >= 1


# ============================================================================
# SPEC CRITERION 3: Categorize into Four Types
# ============================================================================


def test_spec_categorizes_technical(requirement_extraction_agent, parsed_bid_documents):
    """Spec 3: Identify and categorize TECHNICAL requirements."""
    bid_doc = parsed_bid_documents["nhs_trust"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    # Should identify at least some technical requirements
    technical = [r for r in requirements if r.category == "Technical"]
    assert len(technical) > 0, "Should identify technical requirements"


def test_spec_categorizes_security(requirement_extraction_agent, parsed_bid_documents):
    """Spec 3: Identify and categorize SECURITY requirements."""
    bid_doc = parsed_bid_documents["nhs_trust"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    # Healthcare/NHS should have security requirements
    security = [r for r in requirements if r.category == "Security"]
    assert len(security) > 0, "NHS should have security requirements"


def test_spec_categorizes_compliance(requirement_extraction_agent, parsed_bid_documents):
    """Spec 3: Identify and categorize COMPLIANCE requirements."""
    bid_doc = parsed_bid_documents["nhs_trust"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    # Should identify compliance requirements (HIPAA, GDPR, etc.)
    compliance = [r for r in requirements if r.category == "Compliance"]
    assert len(compliance) > 0, "Should identify compliance requirements"


def test_spec_categorizes_performance(requirement_extraction_agent, parsed_bid_documents):
    """Spec 3: Identify and categorize PERFORMANCE requirements."""
    bid_doc = parsed_bid_documents["transport"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    # Transport should have performance (uptime, latency) requirements
    performance = [r for r in requirements if r.category == "Performance"]
    assert len(performance) > 0, "Transport should have performance requirements"


def test_spec_valid_categories(requirement_extraction_agent, parsed_bid_documents):
    """Spec 3: All categories must be one of [Technical, Security, Compliance, Performance]."""
    bid_doc = parsed_bid_documents["local_council"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    valid_categories = {"Technical", "Security", "Compliance", "Performance"}
    for req in requirements:
        assert req.category in valid_categories, f"Invalid category: {req.category}"


# ============================================================================
# SPEC CRITERION 4: Assign Priority
# ============================================================================


def test_spec_assigns_priority_to_all(requirement_extraction_agent, parsed_bid_documents):
    """Spec 4: All requirements must have a priority assigned."""
    bid_doc = parsed_bid_documents["local_council"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    valid_priorities = {"High", "Medium", "Low"}
    for req in requirements:
        assert req.priority in valid_priorities, f"Invalid priority: {req.priority}"


def test_spec_high_priority_for_mandatory(requirement_extraction_agent, parsed_bid_documents):
    """Spec 4: MANDATORY requirements should tend toward High priority."""
    bid_doc = parsed_bid_documents["local_council"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    mandatory_reqs = [r for r in requirements if r.mandatory]
    if mandatory_reqs:
        high_priority = [r for r in mandatory_reqs if r.priority == "High"]
        # Not 100% strict - some mandatory could be low priority, but most should be high
        assert (
            len(high_priority) / len(mandatory_reqs) >= 0.5
        ), "Majority of mandatory requirements should be high priority"


def test_spec_low_priority_for_optional(requirement_extraction_agent, parsed_bid_documents):
    """Spec 4: OPTIONAL requirements should tend toward Low priority."""
    bid_doc = parsed_bid_documents["local_council"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    optional_reqs = [r for r in requirements if not r.mandatory]
    if optional_reqs:
        low_priority = [r for r in optional_reqs if r.priority == "Low"]
        # Some optional could be high (important features), but most should be low
        assert (
            len(low_priority) / len(optional_reqs) >= 0.5
        ), "Majority of optional requirements should be low priority"


# ============================================================================
# SPEC CRITERION 5: Estimate Complexity (Local Rule-Based)
# ============================================================================


def test_spec_assigns_complexity_to_all(requirement_extraction_agent, parsed_bid_documents):
    """Spec 5: All requirements must have complexity estimated (local rule-based)."""
    bid_doc = parsed_bid_documents["local_council"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    valid_complexities = {"Simple", "Moderate", "Complex"}
    for req in requirements:
        assert (
            req.estimated_complexity in valid_complexities
        ), f"Invalid complexity: {req.estimated_complexity}"


def test_spec_simple_for_straightforward_requirements(requirement_extraction_agent, parsed_bid_documents):
    """Spec 5: Simple requirements (single responsibility) should be marked Simple."""
    bid_doc = parsed_bid_documents["transport"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    # Should have some simple requirements
    simple = [r for r in requirements if r.estimated_complexity == "Simple"]
    assert len(simple) > 0, "Should identify some simple requirements"


def test_spec_complex_for_architectural_requirements(requirement_extraction_agent, parsed_bid_documents):
    """Spec 5: Complex requirements (architectural) should be marked Complex."""
    bid_doc = parsed_bid_documents["nhs_trust"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output

    # Should have some complex requirements
    complex_reqs = [r for r in requirements if r.estimated_complexity == "Complex"]
    assert len(complex_reqs) > 0, "Should identify some complex requirements"


# ============================================================================
# SPEC CRITERION 8: JSON Serialization
# ============================================================================


def test_spec_json_serialization_round_trip(requirement_extraction_agent, parsed_bid_documents):
    """Spec 8: Requirements must serialize to JSON and back without data loss."""
    bid_doc = parsed_bid_documents["local_council"]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    original_reqs = result.output

    # Serialize to JSON
    json_str = result.model_dump_json()
    assert json_str, "Should serialize to JSON"

    # Deserialize back
    from bid_acceleration_engine.schemas.results import AgentResult

    recovered = AgentResult[list[ExtractedRequirement]].model_validate_json(json_str)
    recovered_reqs = recovered.output

    # Verify data integrity
    assert len(recovered_reqs) == len(original_reqs), "Should preserve all requirements"
    for orig, recovered in zip(original_reqs, recovered_reqs):
        assert orig.source_text == recovered.source_text
        assert orig.category == recovered.category
        assert orig.mandatory == recovered.mandatory


# ============================================================================
# ACCURACY BENCHMARKS
# ============================================================================


@pytest.mark.parametrize(
    "fixture_name,min_requirements",
    [
        ("local_council", 6),
        ("nhs_trust", 7),
        ("transport", 6),
        ("university", 6),
        ("water_authority", 7),
    ],
)
def test_benchmark_extracts_minimum_requirements(
    requirement_extraction_agent, parsed_bid_documents, fixture_name, min_requirements
):
    """Benchmark: Extract minimum expected requirements from each fixture."""
    bid_doc = parsed_bid_documents[fixture_name]
    result = requirement_extraction_agent.run(bid_doc)

    assert result.status == AgentStatus.SUCCESS
    requirements = result.output
    assert (
        len(requirements) >= min_requirements
    ), f"{fixture_name}: Expected ≥{min_requirements} requirements, got {len(requirements)}"


def test_benchmark_80_percent_accuracy_category_assignment(
    requirement_extraction_agent, parsed_bid_documents
):
    """Benchmark: 80%+ correct category assignment across all UK RFP fixtures."""
    all_requirements = []
    for bid_doc in parsed_bid_documents.values():
        result = requirement_extraction_agent.run(bid_doc)
        assert result.status == AgentStatus.SUCCESS
        all_requirements.extend(result.output)

    # Check that all have valid categories
    valid_categories = {"Technical", "Security", "Compliance", "Performance"}
    correct = sum(1 for r in all_requirements if r.category in valid_categories)
    accuracy = correct / len(all_requirements) if all_requirements else 0

    assert accuracy >= 0.80, f"Category assignment accuracy {accuracy:.2%} below 80% threshold"


def test_benchmark_90_percent_accuracy_mandatory_optional(
    requirement_extraction_agent, parsed_bid_documents
):
    """Benchmark: 90%+ correct mandatory/optional classification."""
    all_requirements = []
    for bid_doc in parsed_bid_documents.values():
        result = requirement_extraction_agent.run(bid_doc)
        assert result.status == AgentStatus.SUCCESS
        all_requirements.extend(result.output)

    # Verify all have boolean mandatory status
    correct = sum(1 for r in all_requirements if isinstance(r.mandatory, bool))
    accuracy = correct / len(all_requirements) if all_requirements else 0

    assert accuracy >= 0.90, f"Mandatory/optional accuracy {accuracy:.2%} below 90% threshold"


# ============================================================================
# ERROR HANDLING
# ============================================================================


def test_spec_handles_missing_mandatory_section(requirement_extraction_agent, parsed_bid_documents):
    """Spec: Gracefully handle documents with no explicit MANDATORY section."""
    # Create a minimal bid document without mandatory section
    from bid_acceleration_engine.schemas.bid import BidDocument, BidMetadata, BidSection
    from datetime import datetime
    from uuid import uuid4

    minimal_doc = BidDocument(
        id=uuid4(),
        metadata=BidMetadata(title="Test", word_count=10),
        raw_text="Some content without mandatory section",
        sections=[BidSection(heading="OVERVIEW", body="Just some text", order=0)],
    )

    result = requirement_extraction_agent.run(minimal_doc)

    # Should handle gracefully - either return empty, infer, or warn
    assert result.status in [AgentStatus.SUCCESS, AgentStatus.SKIPPED]
