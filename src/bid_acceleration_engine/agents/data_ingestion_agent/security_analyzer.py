"""Security analyzer: encryption, auth method, security recommendations."""

from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


def determine_encryption(
    requirements: list[ExtractedRequirement],
) -> tuple[str, bool, bool]:
    """Determine encryption approach (transit, at-rest, PII).

    Args:
        requirements: List of extracted requirements.

    Returns:
        Tuple of (encryption_in_transit, encryption_at_rest, column_level_encryption).
    """
    text = " ".join([r.source_text.lower() for r in requirements])

    encryption_in_transit = "tls-1-2-plus"  # Always

    # At-rest encryption for GDPR, PII, healthcare, government
    needs_at_rest = any(keyword in text for keyword in ["gdpr", "pii", "healthcare", "government", "sensitive"])

    # Column-level encryption for PII, GDPR, and healthcare
    needs_column_encryption = any(
        keyword in text
        for keyword in [
            "gdpr",
            "pii",
            "personal data",
            "sensitive data",
            "healthcare",
            "nhs",
            "patient data",
            "dspt",
        ]
    )

    if needs_at_rest:
        logger.debug("Encryption at-rest required")
    if needs_column_encryption:
        logger.debug("Column-level encryption for PII required")

    return encryption_in_transit, needs_at_rest, needs_column_encryption


def generate_security_recommendations(
    auth_method: str,
    network_security_layer: str,
    encryption_at_rest: bool,
    column_level_encryption: bool,
    requirements: list[ExtractedRequirement],
) -> list[str]:
    """Generate security recommendations based on configuration.

    Args:
        auth_method: Authentication method (windows-auth, sql-auth, managed-identity).
        network_security_layer: Network layer (shir-only, shir-plus-vpn, shir-plus-expressroute).
        encryption_at_rest: Whether at-rest encryption needed.
        column_level_encryption: Whether column-level encryption needed.
        requirements: List of extracted requirements.

    Returns:
        List of security recommendations.
    """
    recommendations = []
    text = " ".join([r.source_text.lower() for r in requirements])

    # Network security recommendations
    if network_security_layer == "shir-plus-expressroute":
        recommendations.append("Use ExpressRoute for dedicated private connection (enterprise-grade)")

    if "vpn" in text and network_security_layer == "shir-only":
        recommendations.append("Consider adding site-to-site VPN for additional network encryption")

    # Authentication recommendations
    if auth_method == "sql-auth":
        recommendations.append("Rotate SQL Server credentials quarterly (store in Azure Key Vault)")
        recommendations.append("Use Azure Key Vault for secure credential storage")

    if auth_method == "managed-identity":
        recommendations.append("Use Managed Identity instead of SQL credentials (modern best practice)")

    if auth_method == "sql-auth" and ("modern" in text or "managed identity" in text):
        recommendations.append("Use Managed Identity instead of SQL credentials (modern best practice)")

    # Encryption recommendations
    if column_level_encryption:
        recommendations.append("Implement column-level encryption for PII (GDPR requirement)")

    if encryption_at_rest:
        recommendations.append("Enable encryption at rest for all data landing zones")

    # Healthcare-specific recommendations
    if "healthcare" in text or "nhs" in text:
        recommendations.append("Implement NHS DSPT encryption standards")
        recommendations.append("Enable data residency within NHS-approved regions")

    # GDPR-specific recommendations
    if "gdpr" in text:
        recommendations.append("Enable audit logging for all data access (GDPR Article 32)")
        recommendations.append("Implement data retention policies aligned with GDPR")

    # General best practices
    recommendations.append("Enable monitoring and alerting for SHIR connection failures")
    recommendations.append("Implement data lineage tracking for audit compliance")

    logger.debug(f"Generated {len(recommendations)} security recommendations")
    return recommendations


def determine_firewall_rules(on_premise_sources: list[str]) -> list[str]:
    """Determine firewall rules needed for on-premise sources.

    Args:
        on_premise_sources: List of on-premise source types.

    Returns:
        List of firewall rules.
    """
    rules = []

    source_text = " ".join(on_premise_sources).lower()

    # SQL Server: port 1433
    if "sql server" in source_text:
        rules.append("Allow SHIR IP to SQL Server port 1433 (TCP)")

    # Oracle: port 1521
    if "oracle" in source_text:
        rules.append("Allow SHIR IP to Oracle port 1521 (TCP)")

    # PostgreSQL: port 5432
    if "postgresql" in source_text:
        rules.append("Allow SHIR IP to PostgreSQL port 5432 (TCP)")

    # MySQL: port 3306
    if "mysql" in source_text:
        rules.append("Allow SHIR IP to MySQL port 3306 (TCP)")

    # SFTP/File shares
    if "sftp" in source_text or "file share" in source_text:
        rules.append("Allow SHIR IP to SFTP/SMB ports (22, 445)")

    # Generic rule
    if not rules:
        rules.append("Allow SHIR IP to all required on-premise data source ports")

    # Restrict sources
    rules.append("Restrict access to SHIR IP only (principle of least privilege)")

    logger.debug(f"Determined {len(rules)} firewall rules")
    return rules
