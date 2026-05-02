"""Requirement classifier: categorize, prioritize, and estimate complexity."""

import re

from bid_acceleration_engine.schemas.requirements import (
    EstimatedComplexity,
    RequirementCategory,
    RequirementPriority,
)
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


# Keyword patterns for classification
TECHNICAL_KEYWORDS = [
    "database",
    "cloud",
    "api",
    "architecture",
    "framework",
    "service",
    "integration",
    "deployment",
    "system",
    "infrastructure",
    "platform",
    "software",
    "application",
    "server",
    "network",
    "microservice",
    "container",
    "kubernetes",
    "docker",
    "distributed",
]

SECURITY_KEYWORDS = [
    "encryption",
    "authentication",
    "authorization",
    "access control",
    "firewall",
    "audit",
    "security",
    "ssl",
    "tls",
    "certificate",
    "token",
    "password",
    "otp",
    "mfa",
    "threat",
    "vulnerability",
    "penetration",
]

COMPLIANCE_KEYWORDS = [
    "gdpr",
    "hipaa",
    "soc2",
    "audit",
    "standard",
    "regulation",
    "legal",
    "compliance",
    "privacy",
    "data protection",
    "iso",
    "certification",
    "requirement",
    "governance",
    "policy",
]

PERFORMANCE_KEYWORDS = [
    "latency",
    "throughput",
    "uptime",
    "availability",
    "concurrent",
    "response time",
    "scalability",
    "performance",
    "sla",
    "qos",
    "load",
    "capacity",
    "millisecond",
    "second",
    "percent",
    "%",
    "users",
    "requests",
]

HIGH_PRIORITY_KEYWORDS = ["critical", "must", "shall", "required", "essential", "core", "mandatory"]
MEDIUM_PRIORITY_KEYWORDS = ["should", "important", "significant"]
LOW_PRIORITY_KEYWORDS = ["could", "may", "nice-to-have", "optional"]


def classify_category(requirement_text: str) -> RequirementCategory:
    """Classify requirement into one of four categories.

    Uses keyword matching with intelligent heuristics.
    Defaults to Technical if ambiguous.

    Args:
        requirement_text: The requirement text.

    Returns:
        RequirementCategory (Technical, Security, Compliance, or Performance).
    """
    text_lower = requirement_text.lower()

    # Count keyword matches for each category
    security_score = sum(1 for kw in SECURITY_KEYWORDS if kw in text_lower)
    compliance_score = sum(1 for kw in COMPLIANCE_KEYWORDS if kw in text_lower)
    performance_score = sum(1 for kw in PERFORMANCE_KEYWORDS if kw in text_lower)
    technical_score = sum(1 for kw in TECHNICAL_KEYWORDS if kw in text_lower)

    # Special handling: if it mentions specific thresholds, likely performance
    if re.search(r"(\d+%|\d+\s*(?:ms|seconds?|users|requests|concurrent))", text_lower):
        performance_score += 2

    # Determine category by highest score
    scores = {
        RequirementCategory.TECHNICAL: technical_score,
        RequirementCategory.SECURITY: security_score,
        RequirementCategory.COMPLIANCE: compliance_score,
        RequirementCategory.PERFORMANCE: performance_score,
    }

    max_score = max(scores.values())
    if max_score == 0:
        # No keywords matched, default to Technical
        return RequirementCategory.TECHNICAL

    # Return category with highest score
    for category, score in scores.items():
        if score == max_score:
            return category

    return RequirementCategory.TECHNICAL


def assign_priority(
    requirement_text: str,
    mandatory: bool,
) -> RequirementPriority:
    """Assign priority to a requirement.

    Rules (applied in order):
    1. HIGH: Mandatory (default), or high-priority keywords, or uptime > 99%,
       throughput > 10k/sec, users > 100k
    2. MEDIUM: 95-99% uptime, 1k-10k throughput, 10k-100k users, or medium
       keywords
    3. LOW: Optional (default), or uptime < 95%, throughput < 1k, users < 10k,
       or low keywords

    Args:
        requirement_text: The requirement text.
        mandatory: Whether the requirement is in the mandatory section.

    Returns:
        RequirementPriority (High, Medium, or Low).
    """
    text_lower = requirement_text.lower()

    # Check for explicit priority keywords
    has_high_keyword = any(kw in text_lower for kw in HIGH_PRIORITY_KEYWORDS)
    has_medium_keyword = any(kw in text_lower for kw in MEDIUM_PRIORITY_KEYWORDS)
    has_low_keyword = any(kw in text_lower for kw in LOW_PRIORITY_KEYWORDS)

    # Check for numeric thresholds
    uptime_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*uptime", text_lower)
    throughput_match = re.search(r"(\d+(?:[,\s]*\d+)*)\s*(?:per|/)\s*(?:second|sec)", text_lower)
    users_match = re.search(r"(\d+(?:[,\s]*\d+)*)\s*(?:concurrent\s+)?users", text_lower)

    uptime_pct = float(uptime_match.group(1)) if uptime_match else None
    throughput_val = int(re.sub(r"[,\s]", "", throughput_match.group(1))) if throughput_match else None
    users_val = int(re.sub(r"[,\s]", "", users_match.group(1))) if users_match else None

    # HIGH priority
    if mandatory:
        # In mandatory section: default to HIGH unless it has explicit low/medium keywords
        if not has_low_keyword:
            return RequirementPriority.HIGH

    if has_high_keyword:
        return RequirementPriority.HIGH
    if uptime_pct and uptime_pct > 99:
        return RequirementPriority.HIGH
    if throughput_val and throughput_val > 10000:
        return RequirementPriority.HIGH
    if users_val and users_val > 100000:
        return RequirementPriority.HIGH

    # LOW priority
    if has_low_keyword:
        return RequirementPriority.LOW
    if uptime_pct and uptime_pct < 95:
        return RequirementPriority.LOW
    if throughput_val and throughput_val < 1000:
        return RequirementPriority.LOW
    if users_val and users_val < 10000:
        return RequirementPriority.LOW

    if not mandatory:
        # Optional section defaults to low
        return RequirementPriority.LOW

    # MEDIUM priority (fallback)
    if uptime_pct and 95 <= uptime_pct <= 99:
        return RequirementPriority.MEDIUM
    if throughput_val and 1000 <= throughput_val <= 10000:
        return RequirementPriority.MEDIUM
    if users_val and 10000 <= users_val <= 100000:
        return RequirementPriority.MEDIUM
    if has_medium_keyword:
        return RequirementPriority.MEDIUM

    # Default: mandatory → HIGH, optional → LOW
    return RequirementPriority.HIGH if mandatory else RequirementPriority.LOW


def estimate_complexity(requirement_text: str) -> EstimatedComplexity:
    """Estimate implementation complexity of a requirement.

    Simple: single responsibility, well-defined, no cross-system dependencies
    Moderate: 2-3 components, cross-system, requires testing
    Complex: 4+ components, significant impact, research/prototyping needed

    Args:
        requirement_text: The requirement text.

    Returns:
        EstimatedComplexity (Simple, Moderate, or Complex).
    """
    text_lower = requirement_text.lower()

    # Complexity indicators
    simple_indicators = [
        "support",
        "provide",
        "include",
        "display",
        "show",
        "response time",
    ]
    moderate_indicators = [
        "integrate",
        "sync",
        "real-time",
        "audit",
        "logging",
        "compliance",
        "cross",
        "multiple",
    ]
    complex_indicators = [
        "distributed",
        "machine learning",
        "anomaly",
        "stream processing",
        "architectural",
        "design",
        "research",
        "prototype",
    ]

    simple_score = sum(1 for ind in simple_indicators if ind in text_lower)
    moderate_score = sum(1 for ind in moderate_indicators if ind in text_lower)
    complex_score = sum(1 for ind in complex_indicators if ind in text_lower)

    # Count mentioned components/systems
    system_keywords = [
        "system",
        "service",
        "component",
        "module",
        "database",
        "api",
    ]
    component_mentions = sum(text_lower.count(kw) for kw in system_keywords)

    if complex_score > 0 or component_mentions >= 4:
        return EstimatedComplexity.COMPLEX

    if moderate_score > 0 or component_mentions >= 2:
        return EstimatedComplexity.MODERATE

    if component_mentions == 1 or simple_score > 0:
        return EstimatedComplexity.SIMPLE

    # Default to moderate
    return EstimatedComplexity.MODERATE
