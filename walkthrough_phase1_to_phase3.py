#!/usr/bin/env python3
"""Azure Data Architecture Pipeline — walkthrough of Phases 1–3 (of 7).

Pipeline:
  Phase 1  Bid Intake              ✅ (this script)
  Phase 2  Requirement Extraction  ✅ (this script)
  Phase 3  Data Ingestion Arch     ✅ (this script)
  Phase 4  Transformation Arch     🔨 building
  Phase 5  Analytics Arch          ⏳ todo
  Phase 6  Review & Validation     ⏳ todo
  Phase 7  Delivery Plan           ⏳ todo
"""

import sys
import json

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
from bid_acceleration_engine.schemas.results import AgentStatus


def walkthrough(bid_file_path: str) -> None:
    """Walk through Phase 1, Phase 2, and Phase 3 with a real bid document.

    Args:
        bid_file_path: Path to a bid document (.txt file).
    """
    bid_path = Path(bid_file_path)

    if not bid_path.exists():
        print(f"❌ File not found: {bid_path}")
        return

    print(f"\n{'=' * 80}")
    print("AZURE DATA ARCHITECTURE PIPELINE — WALKTHROUGH (Phases 1-3 of 7)")
    print(f"{'=' * 80}")
    print("  Purpose: Recommend Azure data architecture from a UK government RFP")
    print("  Phases shown: Intake | Requirement Extraction | Data Ingestion Architecture")
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
            print(f"\n  #{i}  [{req.category.value}] [{req.priority.value}] [{'Mandatory' if req.mandatory else 'Optional'}]")
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
            print(f"\n🏗️  Architecture Pattern:")
            print(f"   {arch.architecture_pattern}")

        # Key services
        if arch.key_services:
            print(f"\n☁️  Key Azure Services:")
            for svc in arch.key_services:
                print(f"   • {svc}")

        # Detected signals
        if arch.on_premise_sources:
            print(f"\n🖥️  On-Premise Sources Detected:")
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
            print(f"   High Availability:  {'Yes — ' + str(shir.ha_nodes) + ' nodes' if shir.ha_required else 'No — single node'}")
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
                print(f"\n   🔒 Firewall Rules:")
                for rule in shir.firewall_rules:
                    print(f"      • {rule}")

            if shir.security_recommendations:
                print(f"\n   🛡️  Security Recommendations:")
                for rec in shir.security_recommendations:
                    print(f"      • {rec}")

            if shir.compliance_checklist:
                print(f"\n   ✅ Compliance Checklist:")
                for item in shir.compliance_checklist:
                    print(f"      ☐ {item}")

        # Considerations and assumptions
        if arch.considerations:
            print(f"\n💡 Considerations:")
            for c in arch.considerations:
                print(f"   • {c}")

        if arch.assumptions:
            print(f"\n⚠️  Assumptions:")
            for a in arch.assumptions:
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

        print(f"\n📁 All outputs saved to: {results_dir.absolute()}")

        print(f"\n{'=' * 80}")
        print("PIPELINE PROGRESS SUMMARY")
        print("=" * 80)
        print("  Phase 1  Bid Intake Agent             [DONE] — BidDocument produced")
        print("  Phase 2  Requirement Extraction Agent  [DONE] — ExtractedRequirement[] produced")
        print("  Phase 3  Data Ingestion Agent          [DONE] — DataIngestionArchitecture produced")
        print("  Phase 4  Transformation Agent          [BUILDING] — ETL, Databricks, data quality, lineage")
        print("  Phase 5  Analytics Agent               [TODO] — Synapse SQL, Power BI, API layer")
        print("  Phase 6  Review Agent                  [TODO] — Validated architecture, gaps flagged")
        print("  Phase 7  Delivery Plan Agent           [TODO] — Phased timeline, milestones, team structure")

        print(f"\n{'=' * 80}")
        print("WALKTHROUGH COMPLETE (Phases 1-3 of 7)")
        print(f"{'=' * 80}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Azure Data Architecture Pipeline — Phases 1-3 of 7")
        print("Usage: python walkthrough_phase1_to_phase3.py <path_to_bid_file>")
        print("\nExample:")
        print(
            "  uv run python walkthrough_phase1_to_phase3.py "
            "tests/fixtures/sample_bids/uk_local_council_data_analytics.txt"
        )
        print("\nAvailable UK government RFP fixtures:")
        fixtures = Path("tests/fixtures/sample_bids").glob("uk_*.txt")
        for f in sorted(fixtures):
            print(f"  tests/fixtures/sample_bids/{f.name}")
        sys.exit(1)

    walkthrough(sys.argv[1])
