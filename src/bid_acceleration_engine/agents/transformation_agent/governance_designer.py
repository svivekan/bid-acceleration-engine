"""Governance and compliance framework design."""

from bid_acceleration_engine.agents.transformation_agent import detector
from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.schemas.transformation import GovernanceConfiguration
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


def design_governance_configuration(
    requirements: list[ExtractedRequirement],
    is_uk_gov: bool = False,
) -> GovernanceConfiguration:
    """Design governance and compliance framework.

    Args:
        requirements: List of extracted requirements.
        is_uk_gov: Whether this is a UK government RFP (from Phase 3 or external context).

    Returns:
        GovernanceConfiguration with lineage, audit, compliance settings.
    """
    # Detect governance signals
    has_governance = detector.detect_governance_requirements(requirements)
    has_pii = detector.detect_pii_requirements(requirements)
    compliance_frameworks = detector.detect_compliance_frameworks(requirements)

    # Derive UK government and GDPR from compliance frameworks
    is_gdpr = "GDPR" in compliance_frameworks
    is_nhs = "NHS DSPT" in compliance_frameworks

    logger.info(
        f"Governance signals: governance={has_governance}, PII={has_pii}, "
        f"frameworks={compliance_frameworks}, GDPR={is_gdpr}, NHS={is_nhs}"
    )

    # Determine lineage requirement
    lineage_enabled = has_governance or has_pii or is_uk_gov or is_gdpr or is_nhs

    # Determine retention policy based on compliance frameworks
    retention_policy = None
    if is_nhs:
        retention_policy = "Retain 7 years per NHS Records Management Code"
    elif is_gdpr:
        retention_policy = "Delete or anonymise after purpose fulfilled (data minimisation principle)"

    # UK data residency requirement
    uk_residency = is_uk_gov or is_gdpr or is_nhs

    logger.info(
        f"Governance configuration: lineage={lineage_enabled}, "
        f"uk_residency={uk_residency}, retention={retention_policy}"
    )

    return GovernanceConfiguration(
        lineage_enabled=lineage_enabled,
        lineage_tool="Microsoft Purview" if lineage_enabled else "",
        audit_logging="Azure Monitor",
        retention_policy=retention_policy,
        compliance_frameworks=compliance_frameworks,
        pii_masking_required=has_pii,
        uk_data_residency=uk_residency,
    )
