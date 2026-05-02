"""Requirement extraction agent: extract and classify requirements from bid documents."""

import time
from uuid import uuid4

from bid_acceleration_engine.agents.base import BaseAgent
from bid_acceleration_engine.agents.requirement_extraction_agent import classifier, parsers
from bid_acceleration_engine.schemas.bid import BidDocument
from bid_acceleration_engine.schemas.requirements import ExtractedRequirement
from bid_acceleration_engine.schemas.results import AgentResult


class RequirementExtractionAgent(BaseAgent):
    """Agent for extracting and classifying requirements from parsed bid documents.

    This Phase 2 agent:
    - Identifies MANDATORY/OPTIONAL sections (case-insensitive)
    - Extracts numbered requirements (1., 2., 3., etc.)
    - Classifies into 4 categories: Technical, Security, Compliance, Performance
    - Assigns priority: High, Medium, Low
    - Estimates complexity: Simple, Moderate, Complex
    - All processing is local (no external APIs)
    """

    def run(
        self,
        bid_document: BidDocument,
    ) -> AgentResult[list[ExtractedRequirement]]:
        """Extract and classify requirements from a bid document.

        Args:
            bid_document: The parsed BidDocument from Phase 1.

        Returns:
            AgentResult containing list of ExtractedRequirement objects.
        """
        start_time = time.time()

        try:
            # Step 1: Extract numbered requirements from mandatory/optional sections
            parsed_reqs = parsers.extract_requirements_from_document(bid_document.raw_text)

            # Step 2: Classify each requirement
            extracted_requirements = []
            for parsed_req in parsed_reqs:
                # Classify category
                category = classifier.classify_category(parsed_req.text)

                # Assign priority
                priority = classifier.assign_priority(parsed_req.text, parsed_req.mandatory)

                # Estimate complexity
                complexity = classifier.estimate_complexity(parsed_req.text)

                # Create ExtractedRequirement
                req = ExtractedRequirement(
                    id=uuid4(),
                    source_text=parsed_req.text,
                    category=category,
                    priority=priority,
                    estimated_complexity=complexity,
                    mandatory=parsed_req.mandatory,
                    section_heading=parsed_req.section_heading,
                    source_location=parsed_req.source_location,
                )

                extracted_requirements.append(req)

            # Wrap result
            duration = time.time() - start_time
            self.logger.info(f"Extracted and classified {len(extracted_requirements)} requirements")
            return self._wrap_result(
                output=extracted_requirements,
                duration_seconds=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            self.logger.exception(f"Error extracting requirements: {e}")
            return self._wrap_result(
                output=None,
                duration_seconds=duration,
                error=f"Error extracting requirements: {str(e)}",
            )
