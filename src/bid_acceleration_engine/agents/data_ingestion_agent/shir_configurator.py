"""SHIR configuration: placement, HA, network security, auth method, performance."""

import re

from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


def determine_placement(
    has_on_premise: bool,
    requirements: list[ExtractedRequirement],
) -> str:
    """Determine SHIR placement (on-prem, DMZ, or Azure VM).

    Args:
        has_on_premise: Whether on-premise sources detected.
        requirements: List of extracted requirements.

    Returns:
        Placement: "on-prem", "dmz", or "azure-vm".
    """
    if not has_on_premise:
        return "azure-vm"  # No on-prem, use Azure VM

    # Check for DMZ security policy
    for req in requirements:
        if "dmz" in req.source_text.lower():
            logger.debug("DMZ security policy detected, placing SHIR in DMZ")
            return "dmz"

    # Default: on-premise
    logger.debug("SHIR placement: on-premise")
    return "on-prem"


def determine_ha_requirement(
    requirements: list[ExtractedRequirement],
) -> tuple[bool, int]:
    """Determine HA requirement and node count.

    HA is required if:
    - 99.9% uptime mentioned, OR
    - Enterprise governance required

    Args:
        requirements: List of extracted requirements.

    Returns:
        Tuple of (ha_required, ha_nodes).
    """
    # Check for uptime requirements
    for req in requirements:
        text_lower = req.source_text.lower()
        # Match "99.9% uptime" or similar
        match = re.search(r"(\d+\.\d+)%\s*uptime", text_lower)
        if match:
            uptime = float(match.group(1))
            if uptime >= 99.9:
                logger.debug(f"HA required for {uptime}% uptime SLA")
                return True, 3  # Multi-node cluster

    # Check for enterprise governance
    governance_keywords = [
        "enterprise",
        "critical",
        "mission-critical",
        "high availability",
        "disaster recovery",
    ]
    for req in requirements:
        text_lower = req.source_text.lower()
        for keyword in governance_keywords:
            if keyword in text_lower:
                logger.debug(f"HA required for enterprise governance ('{keyword}')")
                return True, 3

    logger.debug("Single-node SHIR sufficient")
    return False, 1


def determine_network_security(
    requirements: list[ExtractedRequirement],
) -> str:
    """Determine network security layer (SHIR-only, VPN, or ExpressRoute).

    Args:
        requirements: List of extracted requirements.

    Returns:
        Network security layer: "shir-only", "shir-plus-vpn", or "shir-plus-expressroute".
    """
    # Check for enterprise/high-security signals
    enterprise_keywords = ["enterprise", "high-security", "multi-site", "critical"]
    is_enterprise = any(
        keyword in " ".join([r.source_text.lower() for r in requirements]) for keyword in enterprise_keywords
    )

    if is_enterprise:
        logger.debug("ExpressRoute recommended for enterprise-grade security")
        return "shir-plus-expressroute"

    # Check for existing VPN infrastructure
    for req in requirements:
        if "vpn" in req.source_text.lower() or "site-to-site" in req.source_text.lower():
            logger.debug("VPN detected, using SHIR + VPN")
            return "shir-plus-vpn"

    logger.debug("SHIR-only (HTTPS outbound)")
    return "shir-only"


def determine_authentication_method(
    requirements: list[ExtractedRequirement],
) -> tuple[str, bool]:
    """Determine authentication method and managed identity possibility.

    Args:
        requirements: List of extracted requirements.

    Returns:
        Tuple of (auth_method, managed_identity_possible).
    """
    text = " ".join([r.source_text.lower() for r in requirements])

    # Check for Windows domain
    if "windows domain" in text or "active directory" in text or "kerberos" in text:
        logger.debug("Windows authentication for domain environment")
        return "windows-auth", False

    # Check for modern Azure indicators
    if "managed identity" in text or "azure managed identity" in text:
        logger.debug("Managed identity recommended for modern Azure environment")
        return "managed-identity", True

    # Default: SQL auth with credentials in Key Vault
    logger.debug("SQL authentication with Key Vault credentials")
    return "sql-auth", True


def determine_concurrent_connections(
    source_count: int,
    freshness: str | None,
) -> int:
    """Estimate concurrent connections needed.

    Args:
        source_count: Number of data sources.
        freshness: Freshness requirement (e.g., "daily", "hourly").

    Returns:
        Estimated concurrent connections.
    """
    # Base connections: 2-5 for simple, more for complex
    base = 5 if source_count >= 5 else 2

    if source_count >= 10:
        base = 10

    # Increase for frequent refreshes
    if freshness == "hourly":
        base *= 5
    elif freshness == "real-time":
        base *= 10

    logger.debug(f"Estimated concurrent connections: {base}")
    return base


def estimate_daily_volume_gb(volume_str: str | None) -> int | None:
    """Estimate daily volume in GB.

    Args:
        volume_str: Volume string like "2TB".

    Returns:
        Daily volume in GB, or None if not applicable.
    """
    if not volume_str:
        return None

    match = re.search(r"(\d+(?:\.\d+)?)\s*(gb|tb|pb)", volume_str.lower())
    if not match:
        return None

    value = float(match.group(1))
    unit = match.group(2).lower()

    if unit == "pb":
        return int(value * 1_000_000 / 30)  # Monthly to daily
    elif unit == "tb":
        return int(value * 1_000 / 30)
    else:  # gb
        return int(value / 30)
