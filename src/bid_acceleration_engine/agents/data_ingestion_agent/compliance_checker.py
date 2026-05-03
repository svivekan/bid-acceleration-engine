"""Compliance checker: GDPR, NHS DSPT, Cabinet Office, UK data residency."""

from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


def check_uk_government(requirements: list[ExtractedRequirement]) -> bool:
    """Check if RFP is for UK government entity.

    Args:
        requirements: List of extracted requirements.

    Returns:
        True if UK government indicators found.
    """
    text = " ".join([r.source_text.lower() for r in requirements])
    return any(keyword in text for keyword in ["uk government", "council", "nhs", "local authority", "dpia"])


def check_gdpr_requirement(requirements: list[ExtractedRequirement]) -> bool:
    """Check if GDPR compliance is required.

    Args:
        requirements: List of extracted requirements.

    Returns:
        True if GDPR mentioned.
    """
    text = " ".join([r.source_text.lower() for r in requirements])
    return any(
        keyword in text
        for keyword in [
            "gdpr",
            "personal data",
            "pii",
            "data protection",
            "data residency",
            "privacy",
        ]
    )


def check_healthcare_requirement(requirements: list[ExtractedRequirement]) -> bool:
    """Check if healthcare/NHS compliance is required.

    Args:
        requirements: List of extracted requirements.

    Returns:
        True if healthcare indicators found.
    """
    text = " ".join([r.source_text.lower() for r in requirements])
    return any(keyword in text for keyword in ["nhs", "healthcare", "health", "dspt", "patient data"])


def check_uk_data_residency(requirements: list[ExtractedRequirement]) -> bool:
    """Check if UK data residency is required.

    Args:
        requirements: List of extracted requirements.

    Returns:
        True if UK residency requirement found.
    """
    text = " ".join([r.source_text.lower() for r in requirements])
    return any(
        keyword in text
        for keyword in [
            "uk data residency",
            "uk region",
            "uk south",
            "uk west",
            "united kingdom",
            "uk only",
        ]
    )


def get_uk_regions() -> list[str]:
    """Get UK Azure regions for data residency.

    Returns:
        List of UK regions: ["UK South", "UK West"].
    """
    return ["UK South", "UK West"]


def generate_gdpr_checklist() -> list[str]:
    """Generate GDPR compliance checklist.

    Returns:
        List of GDPR checklist items.
    """
    return [
        "☐ GDPR compliance: Data residency in UK regions (UK South or UK West)",
        "☐ Data Protection Impact Assessment (DPIA) completed",
        "☐ Encryption in transit (TLS 1.2+) enabled",
        "☐ Encryption at rest enabled for all data stores",
        "☐ Column-level encryption for PII implemented",
        "☐ Audit trail: All data access logged and retained",
        "☐ Data retention: Policies defined and enforced",
        "☐ Right to deletion: Process defined for data removal",
        "☐ Data subject requests: Process defined and tested",
    ]


def generate_nhs_dspt_checklist() -> list[str]:
    """Generate NHS Data Security and Protection Toolkit checklist.

    Returns:
        List of NHS DSPT checklist items.
    """
    return [
        "☐ NHS DSPT compliance: Data Security and Protection Toolkit standards",
        "☐ Encryption in transit: TLS 1.2+ required",
        "☐ Encryption at rest: AES-256 or equivalent",
        "☐ Access control: Role-based (RBAC) for all users",
        "☐ Audit logging: All access attempts logged",
        "☐ Patient data: Confidentiality maintained",
        "☐ Data minimization: Only necessary data collected",
        "☐ Multi-factor authentication (MFA) required for privileged access",
        "☐ Incident response: Plan defined for data breaches",
    ]


def generate_cabinet_office_checklist() -> list[str]:
    """Generate UK Cabinet Office Security Guidance checklist.

    Returns:
        List of Cabinet Office checklist items.
    """
    return [
        "☐ Cabinet Office Security: UK security guidance compliant",
        "☐ Encryption: TLS 1.2+ for in-transit, AES-256+ for at-rest",
        "☐ Network security: Firewall rules and access controls",
        "☐ Authentication: Multi-factor authentication for privileged users",
        "☐ Logging and monitoring: All activities logged and monitored",
        "☐ Incident response: Plan defined and tested",
        "☐ Data classification: Sensitivity levels assigned",
        "☐ Vendor security: Third-party vendors assessed",
    ]


def generate_compliance_checklist(
    is_uk_government: bool,
    has_gdpr: bool,
    is_healthcare: bool,
) -> list[str]:
    """Generate consolidated compliance checklist.

    Args:
        is_uk_government: Whether UK government RFP.
        has_gdpr: Whether GDPR applies.
        is_healthcare: Whether healthcare/NHS applies.

    Returns:
        List of applicable compliance items.
    """
    checklist = []

    # GDPR always included if mentioned
    if has_gdpr:
        checklist.extend(generate_gdpr_checklist())
        logger.debug("Added GDPR checklist")

    # NHS DSPT for healthcare
    if is_healthcare:
        checklist.extend(generate_nhs_dspt_checklist())
        logger.debug("Added NHS DSPT checklist")

    # Cabinet Office for UK government
    if is_uk_government:
        checklist.extend(generate_cabinet_office_checklist())
        logger.debug("Added Cabinet Office checklist")

    # Deduplicate
    checklist = list(dict.fromkeys(checklist))

    if not checklist:
        # Default minimal checklist
        checklist = [
            "☐ Data encryption in transit (TLS 1.2+)",
            "☐ Data encryption at rest",
            "☐ Access control and audit logging",
            "☐ Incident response plan",
        ]

    return checklist
