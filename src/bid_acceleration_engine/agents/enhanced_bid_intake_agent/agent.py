"""Enhanced Bid Intake Agent (Phase 1.5) — orchestrates bid document enhancement."""

from datetime import datetime

from bid_acceleration_engine.agents.base import BaseAgent
from bid_acceleration_engine.agents.enhanced_bid_intake_agent.categorizer import (
    categorize_sections,
)
from bid_acceleration_engine.agents.enhanced_bid_intake_agent.date_disambiguator import (
    extract_submission_deadline,
)
from bid_acceleration_engine.agents.enhanced_bid_intake_agent.section_enhancer import (
    enhance_sections,
)
from bid_acceleration_engine.agents.enhanced_bid_intake_agent.title_extractor import (
    extract_enhanced_title,
)
from bid_acceleration_engine.schemas.bid import BidDocument
from bid_acceleration_engine.schemas.enhanced_bid import EnhancedBidDocument, EnhancedBidMetadata
from bid_acceleration_engine.schemas.results import AgentResult


class EnhancedBidIntakeAgent(BaseAgent):
    """Phase 1.5: Enhance Phase 1 BidDocument with corrections and confidence scores.

    Takes a BidDocument (from Phase 1 BidIntakeAgent) and applies four improvements:
    1. Title extraction: looks for "Solicitation Title:" field
    2. Date disambiguation: picks submission deadline over other dates
    3. Section detection: detects title-case headings
    4. Categorization: tags MANDATORY/OPTIONAL sections, counts items

    Returns EnhancedBidDocument with confidence scores for all corrected fields.
    EnhancedBidDocument is a BidDocument subclass, so Phase 2+ accepts it transparently.
    """

    def run(self, bid_doc: BidDocument) -> AgentResult[EnhancedBidDocument]:
        """Enhance a BidDocument with Phase 1.5 improvements.

        Args:
            bid_doc: BidDocument from Phase 1

        Returns:
            AgentResult[EnhancedBidDocument] with all corrections and confidence scores
        """
        try:
            start = datetime.now()

            raw_text = bid_doc.raw_text
            corrections = []

            # Step 1: Enhanced title extraction
            new_title, title_source, title_confidence = extract_enhanced_title(raw_text, bid_doc.metadata.title)
            if new_title != bid_doc.metadata.title:
                corrections.append(
                    f"title: '{bid_doc.metadata.title}' → '{new_title}' "
                    f"(source: {title_source}, confidence: {title_confidence:.2f})"
                )

            # Step 2: Date disambiguation
            new_due_date, due_date_type, due_date_confidence = extract_submission_deadline(raw_text)
            if new_due_date and bid_doc.metadata.due_date and new_due_date != bid_doc.metadata.due_date:
                corrections.append(
                    f"due_date: {bid_doc.metadata.due_date} → {new_due_date} "
                    f"(type: {due_date_type}, confidence: {due_date_confidence:.2f})"
                )
                final_due_date = new_due_date
                final_due_date_type = due_date_type
                final_due_date_confidence = due_date_confidence
            elif new_due_date and not bid_doc.metadata.due_date:
                corrections.append(
                    f"due_date: None → {new_due_date} (type: {due_date_type}, confidence: {due_date_confidence:.2f})"
                )
                final_due_date = new_due_date
                final_due_date_type = due_date_type
                final_due_date_confidence = due_date_confidence
            else:
                # Phase 1 found the date; treat it as submission deadline
                final_due_date = bid_doc.metadata.due_date
                final_due_date_type = "submission_deadline" if bid_doc.metadata.due_date else None
                final_due_date_confidence = 1.0 if bid_doc.metadata.due_date else 0.0

            # Step 3: Section enhancement (detect title-case headings)
            enhanced_sections = enhance_sections(raw_text, bid_doc.sections)
            if len(enhanced_sections) > len(bid_doc.sections):
                corrections.append(
                    f"sections: added {len(enhanced_sections) - len(bid_doc.sections)} title-case heading(s)"
                )

            # Step 4: Section categorization and item counting
            categorized_sections, mandatory_count, optional_count = categorize_sections(enhanced_sections)

            # Issuer confidence: check for compound names (parentheticals, dashes)
            issuer_confidence = 1.0
            if bid_doc.metadata.issuer:
                if "(" in bid_doc.metadata.issuer or " - " in bid_doc.metadata.issuer:
                    issuer_confidence = 0.95
                    corrections.append(
                        f"issuer_confidence: reduced to 0.95 (compound name detected: '{bid_doc.metadata.issuer}')"
                    )

            # Build EnhancedBidMetadata
            enhanced_metadata = EnhancedBidMetadata(
                title=new_title,
                issuer=bid_doc.metadata.issuer,
                due_date=final_due_date,
                word_count=bid_doc.metadata.word_count,
                source_file=bid_doc.metadata.source_file,
                ingested_at=bid_doc.metadata.ingested_at,
                title_source=title_source,
                title_confidence=title_confidence,
                due_date_type=final_due_date_type,
                due_date_confidence=final_due_date_confidence,
                issuer_confidence=issuer_confidence,
                mandatory_count=mandatory_count,
                optional_count=optional_count,
            )

            # Build EnhancedBidDocument
            enhanced_doc = EnhancedBidDocument(
                id=bid_doc.id,
                metadata=enhanced_metadata,
                raw_text=bid_doc.raw_text,
                sections=categorized_sections,
                corrections_applied=corrections,
            )

            duration = (datetime.now() - start).total_seconds()
            return self._wrap_result(enhanced_doc, duration_seconds=duration)

        except Exception as e:
            return self._wrap_result(None, duration_seconds=0, error=str(e))
