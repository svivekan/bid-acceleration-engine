"""Shared pytest fixtures for bid-acceleration-engine tests."""

from pathlib import Path
from uuid import uuid4

import pytest

from bid_acceleration_engine.schemas.requirements import (
    EstimatedComplexity,
    ExtractedRequirement,
    RequirementCategory,
    RequirementPriority,
)


@pytest.fixture
def sample_bid_path() -> Path:
    """Path to the simple RFP sample bid document."""
    path = Path(__file__).parent / "fixtures" / "sample_bids" / "simple_rfp.txt"
    return path


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Temporary output directory for test artifacts."""
    return tmp_path


@pytest.fixture
def uk_local_council_requirements() -> list[ExtractedRequirement]:
    """Extracted requirements from UK Local Council Data Analytics RFP."""
    return [
        ExtractedRequirement(
            id=uuid4(),
            source_text="Consolidate data from 8 legacy council systems (Oracle EBS, various case management systems)",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="PROJECT SCOPE",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Match records at household and individual level (pseudonymised)",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="PROJECT SCOPE",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Support both structured (transactional) and unstructured (case notes) data",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="PROJECT SCOPE",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Daily data refresh cycles from source systems",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="TECHNICAL REQUIREMENTS",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Sub-5 second query response times for standard dashboards",
            category=RequirementCategory.PERFORMANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="TECHNICAL REQUIREMENTS",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Support 50+ concurrent users across council departments",
            category=RequirementCategory.PERFORMANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="TECHNICAL REQUIREMENTS",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Ensure GDPR compliance with Data Protection Impact Assessment (DPIA)",
            category=RequirementCategory.COMPLIANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="DATA GOVERNANCE",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Maintain audit trail for all data access and modifications",
            category=RequirementCategory.COMPLIANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="DATA GOVERNANCE",
        ),
    ]
