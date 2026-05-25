"""Data quality framework design."""

from bid_acceleration_engine.agents.transformation_agent import detector
from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.schemas.transformation import DataQualityConfiguration, DataQualityRule
from bid_acceleration_engine.utils.logging import get_logger

logger = get_logger(__name__)


def design_data_quality_configuration(
    requirements: list[ExtractedRequirement],
) -> DataQualityConfiguration:
    """Design data quality rules and configuration.

    Args:
        requirements: List of extracted requirements.

    Returns:
        DataQualityConfiguration with appropriate rules.
    """
    rules = []

    # Detect quality signals
    has_pii = detector.detect_pii_requirements(requirements)
    dedup_required = detector.detect_deduplication_needs(requirements)
    reconciliation_required = detector.detect_reconciliation_needs(requirements)
    has_quality_needs = detector.detect_data_quality_needs(requirements)

    logger.info(
        f"Quality signals: PII={has_pii}, dedup={dedup_required}, "
        f"reconciliation={reconciliation_required}, quality_needs={has_quality_needs}"
    )

    # Rule 1: Always add schema validation (mandatory for all transforms)
    rules.append(
        DataQualityRule(
            tier="validation",
            description="Schema validation: enforce field types, reject nulls on mandatory columns",
            implementation="Data Factory Data Flows or Databricks dataframe schema enforcement; "
            "Azure Synapse pipeline validation steps",
        )
    )

    # Rule 2: Deduplication (if detected)
    if dedup_required or has_quality_needs:
        rules.append(
            DataQualityRule(
                tier="deduplication",
                description="Deduplication on primary key (system source + record ID)",
                implementation="Data Factory Distinct transform or Databricks dropDuplicates() on key columns; "
                "Synapse SQL RANK() OVER window function",
            )
        )

    # Rule 3: Reconciliation (if detected)
    if reconciliation_required or has_quality_needs:
        rules.append(
            DataQualityRule(
                tier="reconciliation",
                description="Reconciliation: input record count = output count ±5%",
                implementation="Azure Monitor alerts on row-count mismatches; "
                "Purview data quality checks on source vs. destination counts",
            )
        )

    # Rule 4: PII Masking (if detected)
    if has_pii:
        rules.append(
            DataQualityRule(
                tier="pii_masking",
                description="PII masking: hash/pseudonymise personal identifiers for analytics dataset",
                implementation="Data Factory Derived Column with SHA256() hash; "
                "Databricks SQL CAST to BINARY, then hash; "
                "Synapse Dynamic Data Masking or column-level encryption",
            )
        )

    logger.info(f"Generated {len(rules)} data quality rules")

    return DataQualityConfiguration(
        rules=rules,
        has_pii=has_pii,
        reconciliation_required=reconciliation_required,
        deduplication_required=dedup_required,
    )
