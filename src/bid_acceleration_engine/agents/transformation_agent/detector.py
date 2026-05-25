"""Signal detection for transformation requirements."""

from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


def detect_pii_requirements(requirements: list[ExtractedRequirement]) -> bool:
    """Detect if requirements mention personally identifiable information handling.

    Args:
        requirements: List of extracted requirements.

    Returns:
        True if PII-related keywords found, False otherwise.
    """
    pii_keywords = [
        "pii",
        "personal data",
        "gdpr",
        "pseudonym",
        "anonymis",
        "redact",
        "sensitive",
        "personally identifiable",
        "encrypt personal",
    ]

    for req in requirements:
        text_lower = req.source_text.lower()
        for keyword in pii_keywords:
            if keyword in text_lower:
                logger.debug(f"Detected PII keyword '{keyword}' in: {req.source_text[:80]}")
                return True
    return False


def detect_data_quality_needs(requirements: list[ExtractedRequirement]) -> bool:
    """Detect if requirements mention data quality, validation, or cleansing.

    Args:
        requirements: List of extracted requirements.

    Returns:
        True if data quality keywords found, False otherwise.
    """
    quality_keywords = [
        "reconcil",
        "dedup",
        "duplicat",
        "validat",
        "quality",
        "cleanse",
        "accuracy",
        "data integrity",
        "schema enforcement",
    ]

    for req in requirements:
        text_lower = req.source_text.lower()
        for keyword in quality_keywords:
            if keyword in text_lower:
                logger.debug(f"Detected data quality keyword '{keyword}' in: {req.source_text[:80]}")
                return True
    return False


def detect_governance_requirements(requirements: list[ExtractedRequirement]) -> bool:
    """Detect if requirements mention governance, lineage, audit, or traceability.

    Args:
        requirements: List of extracted requirements.

    Returns:
        True if governance keywords found, False otherwise.
    """
    governance_keywords = [
        "lineage",
        "audit trail",
        "catalog",
        "purview",
        "provenance",
        "traceability",
        "data governance",
        "audit log",
    ]

    for req in requirements:
        text_lower = req.source_text.lower()
        for keyword in governance_keywords:
            if keyword in text_lower:
                logger.debug(f"Detected governance keyword '{keyword}' in: {req.source_text[:80]}")
                return True
    return False


def detect_ml_complexity(requirements: list[ExtractedRequirement]) -> bool:
    """Detect if requirements indicate ML/analytics complexity.

    Args:
        requirements: List of extracted requirements.

    Returns:
        True if ML-related keywords found, False otherwise.
    """
    ml_keywords = [
        "machine learning",
        "predict",
        "forecast",
        "model",
        "analytics",
        "scoring",
        "anomaly detection",
        "data science",
    ]

    for req in requirements:
        text_lower = req.source_text.lower()
        for keyword in ml_keywords:
            if keyword in text_lower:
                logger.debug(f"Detected ML keyword '{keyword}' in: {req.source_text[:80]}")
                return True
    return False


def detect_compliance_frameworks(requirements: list[ExtractedRequirement]) -> list[str]:
    """Detect which compliance frameworks are mentioned.

    Args:
        requirements: List of extracted requirements.

    Returns:
        List of detected compliance frameworks (e.g., ["GDPR", "NHS DSPT"]).
    """
    frameworks = set()

    framework_map = {
        "GDPR": ["gdpr", "data protection regulation"],
        "NHS DSPT": ["nhs dspt", "nhs", "dspt", "data security protection toolkit", "nhs standards"],
        "ICO": ["ico", "information commissioner"],
        "Cabinet Office": ["cabinet office", "gs cloud"],
    }

    for req in requirements:
        text_lower = req.source_text.lower()
        for framework, keywords in framework_map.items():
            for keyword in keywords:
                if keyword in text_lower:
                    frameworks.add(framework)
                    logger.debug(f"Detected compliance framework '{framework}' in: {req.source_text[:80]}")

    return sorted(list(frameworks))


def detect_reconciliation_needs(requirements: list[ExtractedRequirement]) -> bool:
    """Detect if requirements mention reconciliation or balance checking.

    Args:
        requirements: List of extracted requirements.

    Returns:
        True if reconciliation keywords found, False otherwise.
    """
    reconciliation_keywords = [
        "reconcil",
        "balance",
        "count check",
        "match record",
        "data reconciliation",
    ]

    for req in requirements:
        text_lower = req.source_text.lower()
        for keyword in reconciliation_keywords:
            if keyword in text_lower:
                logger.debug(f"Detected reconciliation keyword '{keyword}' in: {req.source_text[:80]}")
                return True
    return False


def detect_deduplication_needs(requirements: list[ExtractedRequirement]) -> bool:
    """Detect if requirements mention deduplication or duplicate handling.

    Args:
        requirements: List of extracted requirements.

    Returns:
        True if deduplication keywords found, False otherwise.
    """
    dedup_keywords = [
        "dedup",
        "duplicate",
        "unique record",
        "remove duplicate",
        "deduplicate",
    ]

    for req in requirements:
        text_lower = req.source_text.lower()
        for keyword in dedup_keywords:
            if keyword in text_lower:
                logger.debug(f"Detected deduplication keyword '{keyword}' in: {req.source_text[:80]}")
                return True
    return False
