#!/usr/bin/env python3
"""Azure Data Architecture Pipeline — walkthrough of Phases 1–4 (of 7).

Pipeline:
  Phase 1  Bid Intake              ✅ (this script)
  Phase 2  Requirement Extraction  ✅ (this script)
  Phase 3  Data Ingestion Arch     ✅ (this script)
  Phase 4  Transformation Arch     ✅ (this script)
  Phase 5  Analytics Arch          ⏳ todo
  Phase 6  Review & Validation     ⏳ todo
  Phase 7  Delivery Plan           ⏳ todo
"""

import json
import sys

# Ensure UTF-8 output on all platforms (including Windows cp1252 terminals)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from tempfile import TemporaryDirectory

from bid_acceleration_engine.agents.bid_intake_agent.agent import BidIntakeAgent
from bid_acceleration_engine.agents.data_ingestion_agent.agent import DataIngestionAgent
from bid_acceleration_engine.agents.requirement_extraction_agent.agent import (
    RequirementExtractionAgent,
)
from bid_acceleration_engine.agents.transformation_agent.agent import TransformationAgent
from bid_acceleration_engine.schemas.results import AgentStatus


def walkthrough(bid_file_path: str) -> None:
    """Walk through Phases 1-4 with a real bid document.

    Args:
        bid_file_path: Path to a bid document (.txt file).
    """
    bid_path = Path(bid_file_path)

    if not bid_path.exists():
        print(f"❌ File not found: {bid_path}")
        return

    print(f"\n{'=' * 80}")
    print("AZURE DATA ARCHITECTURE PIPELINE — WALKTHROUGH (Phases 1-4 of 7)")
    print(f"{'=' * 80}")
    print("  Purpose: Recommend Azure data architecture from a UK government RFP")
    print("  Phases shown: Intake | Extraction | Ingestion | Transformation")
    print(f"{'=' * 80}\n")

    print(f"📄 Input bid file: {bid_path.name}")
    print(f"   Size: {bid_path.stat().st_size:,} bytes\n")

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # ======================================================================
        # PHASE 1: Parse the bid document
        # ======================================================================
        print("=" * 80)
        print("PHASE 1: BID INTAKE — Parse & Extract Metadata")
        print("=" * 80 + "\n")

        bid_intake = BidIntakeAgent("bid_intake_agent")
        output_json = tmp_path / "parsed_bid.json"

        print("⏳ Parsing bid document...")
        result1 = bid_intake.run(bid_path, output_json)

        if result1.status != AgentStatus.SUCCESS:
            print(f"❌ Phase 1 failed: {result1.error_message}")
            return

        bid_doc = result1.output
        print(f"✅ Phase 1 complete in {result1.duration_seconds:.2f}s\n")

        print("📋 Parsed BidDocument:")
        print(f"   Title:      {bid_doc.metadata.title}")
        print(f"   Issuer:     {bid_doc.metadata.issuer}")
        print(f"   Due Date:   {bid_doc.metadata.due_date}")
        print(f"   Word Count: {bid_doc.metadata.word_count:,}")
        print(f"   Sections:   {len(bid_doc.sections)}")
        if bid_doc.sections:
            headings = [s.heading for s in bid_doc.sections if s.heading]
            print(f"   Headings:   {', '.join(headings[:5])}{'...' if len(headings) > 5 else ''}")

        # ======================================================================
        # PHASE 2: Extract and classify requirements
        # ======================================================================
        print(f"\n{'=' * 80}")
        print("PHASE 2: REQUIREMENT EXTRACTION — Classify & Prioritise")
        print("=" * 80 + "\n")

        req_agent = RequirementExtractionAgent("requirement_extraction_agent")

        print("⏳ Extracting requirements...")
        result2 = req_agent.run(bid_doc)

        if result2.status != AgentStatus.SUCCESS:
            print(f"❌ Phase 2 failed: {result2.error_message}")
            return

        requirements = result2.output
        print(f"✅ Phase 2 complete in {result2.duration_seconds:.2f}s\n")

        print(f"📊 Extracted {len(requirements)} requirements\n")

        # By category
        by_category: dict[str, int] = {}
        for req in requirements:
            cat = req.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        print("   By Category:")
        for cat, count in sorted(by_category.items()):
            bar = "█" * count
            print(f"     {cat:<12} {bar} ({count})")

        # By priority
        by_priority: dict[str, int] = {}
        for req in requirements:
            pri = req.priority.value
            by_priority[pri] = by_priority.get(pri, 0) + 1

        print("\n   By Priority:")
        for pri in ["High", "Medium", "Low"]:
            count = by_priority.get(pri, 0)
            bar = "█" * count
            print(f"     {pri:<12} {bar} ({count})")

        # Mandatory vs Optional
        mandatory_count = sum(1 for r in requirements if r.mandatory)
        optional_count = len(requirements) - mandatory_count
        print(f"\n   Mandatory: {mandatory_count}   Optional: {optional_count}")

        # Sample requirements
        print(f"\n{'=' * 80}")
        print("SAMPLE REQUIREMENTS (first 3)")
        print("=" * 80)
        for i, req in enumerate(requirements[:3], 1):
            text = req.source_text[:90] + ("..." if len(req.source_text) > 90 else "")
            req_type = "Mandatory" if req.mandatory else "Optional"
            print(
                f"\n  #{i}  [{req.category.value}] [{req.priority.value}] [{req_type}]"
            )
            print(f"       {text}")

        # ======================================================================
        # PHASE 3: Data Ingestion Architecture
        # ======================================================================
        print(f"\n{'=' * 80}")
        print("PHASE 3: DATA INGESTION ARCHITECTURE — Azure Tool Selection & Configuration")
        print("  (All recommendations are Azure-only, aligned to Well-Architected Framework)")
        print("=" * 80 + "\n")

        ingestion_agent = DataIngestionAgent("data_ingestion_agent")

        print("⏳ Analysing requirements for data ingestion architecture...")
        result3 = ingestion_agent.run(requirements)

        if result3.status != AgentStatus.SUCCESS:
            print(f"❌ Phase 3 failed: {result3.error_message}")
            return

        arch = result3.output
        print(f"✅ Phase 3 complete in {result3.duration_seconds:.2f}s\n")

        # Tool selection
        print("🔧 Tool Selection:")
        print(f"   Recommended Tool:   {arch.tool.value.replace('_', ' ').title()}")
        print(f"   Streaming Required: {'Yes' if arch.is_streaming else 'No'}")
        if arch.complexity_score is not None:
            print(f"   Complexity Score:   {arch.complexity_score}")
        print(f"\n   Decision: {arch.tool_decision}")

        if arch.complexity_factors:
            print("\n   Complexity Factors:")
            for factor in arch.complexity_factors:
                print(f"     • {factor}")

        # Architecture pattern
        if arch.architecture_pattern:
            print("\n🏗️  Architecture Pattern:")
            print(f"   {arch.architecture_pattern}")

        # Key services
        if arch.key_services:
            print("\n☁️  Key Azure Services:")
            for svc in arch.key_services:
                print(f"   • {svc}")

        # Detected signals
        if arch.on_premise_sources:
            print("\n🖥️  On-Premise Sources Detected:")
            for src in arch.on_premise_sources:
                print(f"   • {src}")

        if arch.detected_volume:
            print(f"\n📦 Data Volume:    {arch.detected_volume}")
        if arch.detected_freshness:
            print(f"⏱️  Freshness:      {arch.detected_freshness}")

        # SHIR configuration
        if arch.shir_config:
            shir = arch.shir_config
            print(f"\n{'=' * 80}")
            print("SHIR CONFIGURATION (Self-Hosted Integration Runtime)")
            print("=" * 80)
            print(f"   Placement:          {shir.placement}")
            ha_text = (
                f"Yes — {shir.ha_nodes} nodes"
                if shir.ha_required
                else "No — single node"
            )
            print(f"   High Availability:  {ha_text}")
            print(f"   Network Security:   {shir.network_security_layer}")
            print(f"   Authentication:     {shir.authentication_method}")
            print(f"   Encryption Transit: {shir.encryption_in_transit}")
            print(f"   Encryption At Rest: {'Yes' if shir.encryption_at_rest else 'No'}")
            print(f"   UK Data Residency:  {'Yes' if shir.uk_region_required else 'No'}")
            if shir.azure_regions:
                print(f"   Azure Regions:      {', '.join(shir.azure_regions)}")
            print(f"   Concurrent Conns:   {shir.concurrent_connections}")
            if shir.estimated_daily_volume_gb:
                print(f"   Est. Daily Volume:  {shir.estimated_daily_volume_gb:.1f} GB")

            if shir.firewall_rules:
                print("\n   🔒 Firewall Rules:")
                for rule in shir.firewall_rules:
                    print(f"      • {rule}")

            if shir.security_recommendations:
                print("\n   🛡️  Security Recommendations:")
                for rec in shir.security_recommendations:
                    print(f"      • {rec}")

            if shir.compliance_checklist:
                print("\n   ✅ Compliance Checklist:")
                for item in shir.compliance_checklist:
                    print(f"      ☐ {item}")

        # Considerations and assumptions
        if arch.considerations:
            print("\n💡 Considerations:")
            for c in arch.considerations:
                print(f"   • {c}")

        if arch.assumptions:
            print("\n⚠️  Assumptions:")
            for a in arch.assumptions:
                print(f"   • {a}")

        # ======================================================================
        # PHASE 4: Transformation Architecture
        # ======================================================================
        print(f"\n{'=' * 80}")
        print("PHASE 4: TRANSFORMATION ARCHITECTURE — ETL Design, Data Quality & Governance")
        print("  (All recommendations are Azure-only, aligned to Well-Architected Framework)")
        print("=" * 80 + "\n")

        transformation_agent = TransformationAgent("transformation_agent")

        print("⏳ Analysing requirements for transformation architecture...")
        result4 = transformation_agent.run(arch, requirements)

        if result4.status != AgentStatus.SUCCESS:
            print(f"❌ Phase 4 failed: {result4.error_message}")
            return

        transform = result4.output
        print(f"✅ Phase 4 complete in {result4.duration_seconds:.2f}s\n")

        # Tool selection
        print("🔧 Tool Selection:")
        print(f"   Recommended Tool:   {transform.tool.value.replace('_', ' ').title()}")
        print(f"   Streaming:          {'Yes' if transform.is_streaming else 'No'}")
        print(f"   Complexity Score:   {transform.complexity_score}")
        print(f"\n   Decision: {transform.tool_decision}")

        if transform.complexity_factors:
            print("\n   Complexity Factors:")
            for factor in transform.complexity_factors:
                print(f"     • {factor}")

        # Processing & Architecture
        if transform.processing_pattern:
            print("\n⏱️  Processing Pattern:")
            print(f"   {transform.processing_pattern}")

        if transform.architecture_pattern:
            print("\n🏗️  Architecture Pattern:")
            print(f"   {transform.architecture_pattern}")

        # Key services
        if transform.key_services:
            print("\n☁️  Key Azure Services:")
            for svc in transform.key_services:
                print(f"   • {svc}")

        # Data Quality
        if transform.data_quality:
            print("\n📊 Data Quality Configuration:")
            print(f"   Has PII:                {transform.data_quality.has_pii}")
            print(f"   Deduplication Required: {transform.data_quality.deduplication_required}")
            print(f"   Reconciliation Required: {transform.data_quality.reconciliation_required}")
            if transform.data_quality.rules:
                print("\n   Quality Rules:")
                for rule in transform.data_quality.rules:
                    print(f"     [{rule.tier}] {rule.description}")

        # Governance
        if transform.governance:
            print("\n🔒 Governance & Compliance:")
            print(f"   Lineage Enabled:    {transform.governance.lineage_enabled}")
            if transform.governance.lineage_enabled:
                print(f"   Lineage Tool:       {transform.governance.lineage_tool}")
            print(f"   Audit Logging:      {transform.governance.audit_logging}")
            print(f"   PII Masking:        {transform.governance.pii_masking_required}")
            print(f"   UK Data Residency:  {transform.governance.uk_data_residency}")
            if transform.governance.compliance_frameworks:
                print(f"   Compliance Frameworks: {', '.join(transform.governance.compliance_frameworks)}")
            if transform.governance.retention_policy:
                print(f"   Retention Policy:   {transform.governance.retention_policy}")

        # SLA Targets
        if transform.sla_targets:
            print("\n📈 SLA Targets:")
            for key, value in transform.sla_targets.items():
                print(f"   {key}: {value}")

        # Considerations and assumptions
        if transform.considerations:
            print("\n💡 Considerations:")
            for c in transform.considerations:
                print(f"   • {c}")

        if transform.assumptions:
            print("\n⚠️  Assumptions:")
            for a in transform.assumptions:
                print(f"   • {a}")

        # ======================================================================
        # Export results
        # ======================================================================
        print(f"\n{'=' * 80}")
        print("EXPORTING RESULTS")
        print("=" * 80 + "\n")

        bid_stem = bid_path.stem
        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        phase1_export = results_dir / f"{bid_stem}_{timestamp}_phase1_output.json"
        with open(phase1_export, "w") as f:
            json.dump(result1.model_dump(mode="json"), f, indent=2, default=str)
        print(f"✅ Phase 1 output: {phase1_export}")

        phase2_export = results_dir / f"{bid_stem}_{timestamp}_phase2_output.json"
        with open(phase2_export, "w") as f:
            json.dump(result2.model_dump(mode="json"), f, indent=2, default=str)
        print(f"✅ Phase 2 output: {phase2_export}")

        phase3_export = results_dir / f"{bid_stem}_{timestamp}_phase3_output.json"
        with open(phase3_export, "w") as f:
            json.dump(result3.model_dump(mode="json"), f, indent=2, default=str)
        print(f"✅ Phase 3 output: {phase3_export}")

        phase4_export = results_dir / f"{bid_stem}_{timestamp}_phase4_output.json"
        with open(phase4_export, "w") as f:
            json.dump(result4.model_dump(mode="json"), f, indent=2, default=str)
        print(f"✅ Phase 4 output: {phase4_export}")

        print(f"\n📁 All outputs saved to: {results_dir.absolute()}")

        print(f"\n{'=' * 80}")
        print("PIPELINE PROGRESS SUMMARY")
        print("=" * 80)
        print("  Phase 1  Bid Intake Agent             [DONE] — BidDocument produced")
        print("  Phase 2  Requirement Extraction Agent  [DONE] — ExtractedRequirement[] produced")
        print("  Phase 3  Data Ingestion Agent          [DONE] — DataIngestionArchitecture produced")
        print("  Phase 4  Transformation Agent          [DONE] — TransformationArchitecture produced")
        print("  Phase 5  Analytics Agent               [TODO] — Synapse SQL, Power BI, API layer")
        print("  Phase 6  Review Agent                  [TODO] — Validated architecture, gaps flagged")
        print("  Phase 7  Delivery Plan Agent           [TODO] — Phased timeline, milestones, team structure")

        print(f"\n{'=' * 80}")
        print("WALKTHROUGH COMPLETE (Phases 1-4 of 7)")
        print(f"{'=' * 80}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Azure Data Architecture Pipeline — Phases 1-4 of 7")
        print("Usage: python walkthrough_phase1_to_phase4.py <path_to_bid_file>")
        print("\nExample:")
        print(
            "  uv run python walkthrough_phase1_to_phase4.py "
            "tests/fixtures/sample_bids/uk_local_council_data_analytics.txt"
        )
        print("\nAvailable UK government RFP fixtures:")
        fixtures = Path("tests/fixtures/sample_bids").glob("uk_*.txt")
        for f in sorted(fixtures):
            print(f"  tests/fixtures/sample_bids/{f.name}")
        sys.exit(1)

    walkthrough(sys.argv[1])
