"""Bid intake agent: parses raw bid documents and extracts metadata."""

import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from bid_acceleration_engine.agents.base import BaseAgent
from bid_acceleration_engine.agents.bid_intake_agent import parsers
from bid_acceleration_engine.schemas.bid import BidDocument, BidMetadata
from bid_acceleration_engine.schemas.results import AgentResult
from bid_acceleration_engine.utils.file_io import read_text_file, write_json


class BidIntakeAgent(BaseAgent):
    """Agent for parsing raw bid documents and extracting metadata.

    This is a Phase 1 MVP agent that performs pure text parsing without LLM calls.
    It extracts:
    - Title (first non-empty line)
    - Issuer/contracting authority
    - Due date
    - Word count
    - Document sections
    """

    def run(
        self,
        source_path: Path,
        output_path: Path,
    ) -> AgentResult[BidDocument]:
        """Parse a bid document and write results to JSON.

        Args:
            source_path: Path to the source .txt bid document.
            output_path: Path where to write the JSON output.

        Returns:
            AgentResult containing the parsed BidDocument or error details.
        """
        start_time = time.time()

        try:
            # Read the bid document
            raw_text = read_text_file(source_path)

            # Extract metadata
            title = parsers.extract_title(raw_text)
            issuer = parsers.extract_issuer(raw_text)
            due_date = parsers.extract_due_date(raw_text)
            word_count = parsers.count_words(raw_text)
            sections = parsers.extract_sections(raw_text)

            # Construct BidMetadata
            metadata = BidMetadata(
                title=title,
                issuer=issuer,
                due_date=due_date,
                word_count=word_count,
                source_file=source_path,
                ingested_at=datetime.now(),
            )

            # Construct BidDocument
            doc = BidDocument(
                id=uuid4(),
                metadata=metadata,
                raw_text=raw_text,
                sections=sections,
            )

            # Write JSON output
            write_json(doc, output_path, overwrite=False)

            # Wrap result
            duration = time.time() - start_time
            return self._wrap_result(
                output=doc,
                duration_seconds=duration,
            )

        except FileNotFoundError:
            duration = time.time() - start_time
            self.logger.error(f"File not found: {source_path}")
            return self._wrap_result(
                output=None,
                duration_seconds=duration,
                error=f"File not found: {source_path}",
            )
        except Exception as e:
            duration = time.time() - start_time
            self.logger.exception(f"Error processing bid document: {e}")
            return self._wrap_result(
                output=None,
                duration_seconds=duration,
                error=f"Error processing bid document: {str(e)}",
            )
