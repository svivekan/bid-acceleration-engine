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


@pytest.fixture
def nhs_trust_requirements() -> list[ExtractedRequirement]:
    """Extracted requirements from NHS Trust Hospital Systems Integration RFP."""
    return [
        ExtractedRequirement(
            id=uuid4(),
            source_text="Integrate 12 hospital systems (Oracle EBS, SQL Server, Cerner EMR, legacy HL7 feeds)",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="PROJECT SCOPE",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Support 24/7 real-time patient record access across hospital network",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="TECHNICAL REQUIREMENTS",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Handle 3TB+ daily ingest from EHR systems and medical devices",
            category=RequirementCategory.PERFORMANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="TECHNICAL REQUIREMENTS",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="NHS DSPT compliance mandatory, encryption at rest and in transit required",
            category=RequirementCategory.COMPLIANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="DATA GOVERNANCE",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Patient data confidentiality, pseudonymisation for analytics",
            category=RequirementCategory.COMPLIANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="DATA GOVERNANCE",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Audit logging for all clinical data access, data residency in UK",
            category=RequirementCategory.COMPLIANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="DATA GOVERNANCE",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="99.95% uptime SLA for critical patient pathways",
            category=RequirementCategory.PERFORMANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="OPERATIONAL REQUIREMENTS",
        ),
    ]


@pytest.fixture
def transport_authority_requirements() -> list[ExtractedRequirement]:
    """Extracted requirements from Transport Authority Intelligent Traffic RFP."""
    return [
        ExtractedRequirement(
            id=uuid4(),
            source_text="Ingest real-time traffic flow data from 500+ sensors and CCTV cameras across region",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="PROJECT SCOPE",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Continuous streaming data processing, sub-second latency for traffic light coordination",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="TECHNICAL REQUIREMENTS",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Integrate with legacy on-premise SCADA system and cloud traffic API feeds",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="TECHNICAL REQUIREMENTS",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="1000+ events per second ingest, high availability and failover required",
            category=RequirementCategory.PERFORMANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="TECHNICAL REQUIREMENTS",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="GDPR compliance for vehicle tracking data, data residency in UK",
            category=RequirementCategory.COMPLIANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="DATA GOVERNANCE",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="99.9% uptime SLA, disaster recovery plan required",
            category=RequirementCategory.PERFORMANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="OPERATIONAL REQUIREMENTS",
        ),
    ]


@pytest.fixture
def water_authority_requirements() -> list[ExtractedRequirement]:
    """Extracted requirements from Water Authority Customer Service RFP."""
    return [
        ExtractedRequirement(
            id=uuid4(),
            source_text="Consolidate customer billing from 4 legacy on-premise systems (IBM mainframe, SQL Server, Oracle)",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.COMPLEX,
            mandatory=True,
            section_heading="PROJECT SCOPE",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="200GB daily billing and consumption data from smart meters and legacy systems",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="TECHNICAL REQUIREMENTS",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Batch processing overnight for billing cycles, daily data refresh",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="TECHNICAL REQUIREMENTS",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="GDPR compliance for customer personal data, audit trail for regulatory reporting",
            category=RequirementCategory.COMPLIANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="DATA GOVERNANCE",
        ),
        ExtractedRequirement(
            id=uuid4(),
            source_text="Support 100+ concurrent users, sub-2 second query response times",
            category=RequirementCategory.PERFORMANCE,
            priority=RequirementPriority.HIGH,
            estimated_complexity=EstimatedComplexity.MODERATE,
            mandatory=True,
            section_heading="TECHNICAL REQUIREMENTS",
        ),
    ]
