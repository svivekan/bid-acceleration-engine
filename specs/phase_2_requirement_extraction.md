# Phase 2: Requirement Extraction Agent

## Overview
Extract and classify technical requirements from parsed bid documents. Identify mandatory vs. optional requirements, categorize by type, and assign priority and complexity estimates. Uses Claude Code for intelligent classification (local processing only, no Claude API calls).

## Input
- `BidDocument` (from Phase 1 bid_intake_agent)
  - `raw_text`: Full RFP text
  - `sections`: List of BidSection objects
  - `metadata`: Title, issuer, due_date, etc.

## Output
- `ExtractedRequirement[]` containing:
  - `id`: UUID (unique requirement identifier)
  - `source_text`: Original text from RFP (raw requirement text)
  - `category`: One of [Technical, Security, Compliance, Performance]
  - `mandatory`: Boolean (true if in MANDATORY section)
  - `priority`: Enum [High, Medium, Low]
  - `estimated_complexity`: Enum [Simple, Moderate, Complex]
  - `section_heading`: Where requirement was found (e.g., "MANDATORY REQUIREMENTS")
  - `source_location`: Line number or section reference

Wrapped in `AgentResult[ExtractedRequirement[]]` following Phase 1 pattern.

## Acceptance Criteria

### 1. Search for MANDATORY/OPTIONAL Keywords
- [ ] Parse document for "MANDATORY REQUIREMENTS" section heading
- [ ] Parse document for "OPTIONAL FEATURES" / "ENHANCEMENTS" / "CAPABILITIES" section heading
- [ ] Mark requirements `mandatory=true` if found in MANDATORY section
- [ ] Mark requirements `mandatory=false` if found in OPTIONAL section
- [ ] Handle case-insensitive matching

### 2. Extract Numbered Requirements
- [ ] Identify numbered list items (1., 2., 3., etc.)
- [ ] Extract each numbered item as a separate requirement
- [ ] Preserve original text including line breaks
- [ ] Handle multi-line requirements (continue until next number)

### 3. Categorize into Four Types

Use Claude Code to classify each requirement into one of:

**Technical** - Systems, infrastructure, platforms
- Examples: database, cloud, API, architecture, framework, service, integration, deployment

**Security** - Protection and access control
- Examples: encryption, authentication, authorization, access control, firewall, audit

**Compliance** - Legal and regulatory
- Examples: GDPR, HIPAA, SOC2, audit, standards, regulations, legal requirements

**Performance** - Speed, capacity, reliability
- Examples: latency, throughput, uptime, availability, concurrent users, response time, scalability

- [ ] Use Claude Code to intelligently categorize each requirement
- [ ] Default to **Technical** if classification is ambiguous
- [ ] Store category in `category` field

### 4. Assign Priority (High/Medium/Low)
Rules (apply in order):

**High Priority:**
- In MANDATORY REQUIREMENTS section
- Keywords: critical, must, shall, required, essential, core
- Numeric thresholds: uptime > 99%, throughput > 10,000/sec, users > 100,000

**Medium Priority:**
- In MANDATORY section without above keywords
- Keywords: should, important, significant
- Mid-range thresholds: uptime 95-99%, throughput 1,000-10,000/sec, users 10,000-100,000

**Low Priority:**
- In OPTIONAL section
- Keywords: could, may, nice-to-have, optional
- Low thresholds: uptime < 95%, throughput < 1,000/sec, users < 10,000

- [ ] Default to **Medium** if no clear priority indicators
- [ ] Store in `priority` field

### 5. Estimate Complexity (Simple/Moderate/Complex)

Use Claude Code to intelligently assess complexity based on:

**Simple** (straightforward to implement)
- Single responsibility requirement
- Well-defined scope
- No cross-system dependencies
- Examples: "Support 100 concurrent users", "Response time < 2 seconds"

**Moderate** (requires careful design)
- 2-3 related components
- Cross-system dependencies
- Requires testing
- Examples: "Real-time data sync across 3 systems", "HIPAA-compliant audit logging"

**Complex** (major architectural decision)
- 4+ related components
- Significant cross-system impact
- Requires research/prototyping
- Examples: "Distributed stream processing with 99.99% uptime", "Machine learning-based anomaly detection with sub-second latency"

- [ ] Use Claude Code to assess requirement complexity
- [ ] Analyze: scope, dependencies, cross-system impact, technical maturity needed
- [ ] Return one of: Simple, Moderate, Complex
- [ ] Store in `estimated_complexity` field

### 7. Handle Edge Cases
- [ ] Multi-line requirements: preserve line breaks, join into single requirement
- [ ] Numbered items with sub-items (1. main, a. sub): treat as one requirement
- [ ] Duplicate requirements: detect and deduplicate
- [ ] Ambiguous requirements: flag with warning in AgentResult

### 8. JSON Serialization
- [ ] All ExtractedRequirement objects must be Pydantic models
- [ ] Must serialize to/from JSON without data loss
- [ ] Support round-trip: JSON → Python → JSON

## Test Cases

### Happy Path
- [ ] Extract requirements from local_council fixture (6 requirements minimum)
- [ ] Extract requirements from nhs_trust fixture (7 requirements minimum)
- [ ] Extract requirements from transport fixture (6 requirements minimum)
- [ ] Extract requirements from university fixture (6 requirements minimum)
- [ ] Extract requirements from water_authority fixture (7 requirements minimum)

### Accuracy Benchmarks
- [ ] 80%+ correct category assignment across all UK RFP fixtures
- [ ] 90%+ correct mandatory/optional classification
- [ ] All extracted requirements match numbered items in original text

### Edge Cases
- [ ] Requirement with multiple lines
- [ ] Numbered items with sub-bullets
- [ ] Requirements with technical acronyms (GDPR, HIPAA, SLA)
- [ ] Requirements with numeric values (uptime thresholds, user counts)
- [ ] Empty optional features section
- [ ] No explicit mandatory requirements section (all requirements treated as optional)

### Error Handling
- [ ] Missing MANDATORY/OPTIONAL section: return empty result or inferred requirements
- [ ] Malformed requirement text: skip with warning in AgentResult
- [ ] No requirements found: return empty array with SUCCESS status

## Implementation Notes

### Architecture
```
agents/requirement_extraction_agent/
├── agent.py              # RequirementExtractionAgent class
├── parsers.py            # Extract numbered requirements from text
├── classifier.py         # Use Claude Code for intelligent classification
└── __init__.py
```

### Dependencies
- `pydantic` for ExtractedRequirement schema
- Existing: `bid_acceleration_engine.schemas.bid`
- Claude Code for classification (invoked locally, no API calls)

### Implementation Details
- Use Claude Code to intelligently classify requirements
- Claude Code processes locally (no external APIs)
- Extract: category, priority, complexity
- All processing happens in-memory on local machine
- Fallback to simple heuristics if Claude Code unavailable

## Success Criteria

Phase 2 is complete when:
1. ✅ All 8 acceptance criteria pass
2. ✅ All test cases pass
3. ✅ 80%+ accuracy on 5 UK RFP fixtures
4. ✅ No regressions in Phase 1 tests (171 tests still passing)
5. ✅ Code follows project style (Ruff, type hints, docstrings)
6. ✅ Commits are small and atomic (one feature per commit)
