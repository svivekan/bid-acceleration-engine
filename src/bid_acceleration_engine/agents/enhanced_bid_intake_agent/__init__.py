"""Phase 1.5: Enhanced Bid Intake Agent.

Enhances Phase 1 BidDocument output with:
- Corrected title extraction (looks for "Solicitation Title:" field)
- Date disambiguation (picks submission deadline over other dates)
- Section detection improvements (catches title-case headings)
- Section categorization (tags MANDATORY/OPTIONAL, counts items)
- Issuer confidence scoring (detects compound names)
"""

from bid_acceleration_engine.agents.enhanced_bid_intake_agent.agent import EnhancedBidIntakeAgent

__all__ = ["EnhancedBidIntakeAgent"]
