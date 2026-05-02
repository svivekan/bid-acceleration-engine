#!/usr/bin/env python3
"""Real-life walkthrough: Phase 1 (parse) → Phase 2 (extract requirements)."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from bid_acceleration_engine.agents.bid_intake_agent.agent import BidIntakeAgent
from bid_acceleration_engine.agents.requirement_extraction_agent.agent import (
    RequirementExtractionAgent,
)
from bid_acceleration_engine.schemas.results import AgentStatus


def walkthrough(bid_file_path: str) -> None:
    """Walk through Phase 1 and Phase 2 with a real bid document.

    Args:
        bid_file_path: Path to a bid document (.txt file).
    """
    bid_path = Path(bid_file_path)

    if not bid_path.exists():
        print(f"❌ File not found: {bid_path}")
        return

    print(f"\n{'='*80}")
    print(f"PHASE 1 → PHASE 2 WALKTHROUGH")
    print(f"{'='*80}\n")

    print(f"📄 Input bid file: {bid_path.name}")
    print(f"   Size: {bid_path.stat().st_size:,} bytes\n")

    # Create results directory
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # ======================================================================
        # PHASE 1: Parse the bid document
        # ======================================================================
        print("=" * 80)
        print("PHASE 1: BID INTAKE (Parse & Extract Metadata)")
        print("=" * 80 + "\n")

        bid_intake = BidIntakeAgent("bid_intake_agent")
        output_json = tmp_path / "parsed_bid.json"

        print(f"⏳ Parsing bid document...")
        result1 = bid_intake.run(bid_path, output_json)

        if result1.status != AgentStatus.SUCCESS:
            print(f"❌ Phase 1 failed: {result1.error_message}")
            return

        bid_doc = result1.output

        print(f"✅ Phase 1 completed in {result1.duration_seconds:.2f}s\n")

        print(f"Parsed BidDocument:")
        print(f"  Title: {bid_doc.metadata.title}")
        print(f"  Issuer: {bid_doc.metadata.issuer}")
        print(f"  Due Date: {bid_doc.metadata.due_date}")
        print(f"  Word Count: {bid_doc.metadata.word_count:,}")
        print(f"  Sections: {len(bid_doc.sections)}")
        print(f"  Raw Text Length: {len(bid_doc.raw_text):,} characters\n")

        # ======================================================================
        # PHASE 2: Extract and classify requirements
        # ======================================================================
        print("=" * 80)
        print("PHASE 2: REQUIREMENT EXTRACTION (Classify & Prioritize)")
        print("=" * 80 + "\n")

        req_agent = RequirementExtractionAgent("requirement_extraction_agent")

        print(f"⏳ Extracting requirements...")
        result2 = req_agent.run(bid_doc)

        if result2.status != AgentStatus.SUCCESS:
            print(f"❌ Phase 2 failed: {result2.error_message}")
            return

        requirements = result2.output

        print(f"✅ Phase 2 completed in {result2.duration_seconds:.2f}s\n")

        print(f"Extracted {len(requirements)} requirements:\n")

        # Count by category
        by_category = {}
        for req in requirements:
            cat = req.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        print("📊 By Category:")
        for cat, count in sorted(by_category.items()):
            print(f"   {cat}: {count}")

        # Count by priority
        by_priority = {}
        for req in requirements:
            pri = req.priority.value
            by_priority[pri] = by_priority.get(pri, 0) + 1

        print("\n📊 By Priority:")
        for pri in ["High", "Medium", "Low"]:
            count = by_priority.get(pri, 0)
            print(f"   {pri}: {count}")

        # Count by complexity
        by_complexity = {}
        for req in requirements:
            cpx = req.estimated_complexity.value
            by_complexity[cpx] = by_complexity.get(cpx, 0) + 1

        print("\n📊 By Complexity:")
        for cpx in ["Simple", "Moderate", "Complex"]:
            count = by_complexity.get(cpx, 0)
            print(f"   {cpx}: {count}")

        # Mandatory vs Optional
        mandatory_count = sum(1 for r in requirements if r.mandatory)
        optional_count = len(requirements) - mandatory_count

        print(f"\n📊 Mandatory vs Optional:")
        print(f"   Mandatory: {mandatory_count}")
        print(f"   Optional: {optional_count}")

        # ======================================================================
        # Show sample requirements
        # ======================================================================
        print("\n" + "=" * 80)
        print("SAMPLE REQUIREMENTS (First 5)")
        print("=" * 80 + "\n")

        for i, req in enumerate(requirements[:5], 1):
            print(f"Requirement #{i}")
            print(f"  Text: {req.source_text[:80]}{'...' if len(req.source_text) > 80 else ''}")
            print(f"  Category: {req.category.value}")
            print(f"  Priority: {req.priority.value}")
            print(f"  Complexity: {req.estimated_complexity.value}")
            print(f"  Mandatory: {req.mandatory}")
            print(f"  Section: {req.section_heading}")
            print()

        # ======================================================================
        # Export results to persistent directory
        # ======================================================================
        print("=" * 80)
        print("EXPORTING RESULTS")
        print("=" * 80 + "\n")

        # Use bid filename as prefix for results
        bid_stem = bid_path.stem
        timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export Phase 1 output
        phase1_export = results_dir / f"{bid_stem}_{timestamp}_phase1_output.json"
        with open(phase1_export, "w") as f:
            json.dump(result1.model_dump(mode="json"), f, indent=2, default=str)
        print(f"✅ Phase 1 output: {phase1_export}")

        # Export Phase 2 output
        phase2_export = results_dir / f"{bid_stem}_{timestamp}_phase2_output.json"
        with open(phase2_export, "w") as f:
            json.dump(result2.model_dump(mode="json"), f, indent=2, default=str)
        print(f"✅ Phase 2 output: {phase2_export}")

        # Show file paths
        print(f"\n📁 Results saved to: {results_dir.absolute()}")

        print("\n" + "=" * 80)
        print("✅ WALKTHROUGH COMPLETE")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python walkthrough_phase1_phase2.py <path_to_bid_file>")
        print("\nExample:")
        print(
            "  python walkthrough_phase1_phase2.py "
            "tests/fixtures/sample_bids/uk_local_council_data_analytics.txt"
        )
        sys.exit(1)

    walkthrough(sys.argv[1])
