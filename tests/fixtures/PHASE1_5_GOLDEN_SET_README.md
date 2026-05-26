# Phase 1.5 Golden Set — Baseline for Enhancement Testing

## What Is This?

The golden set (`phase1_5_golden_set.json`) is **hand-validated metadata** extracted from real RFP fixtures. It represents the ground truth that Phase 1.5 should achieve.

**Purpose:** To establish a testable baseline showing:
- What Phase 1 currently does correctly
- Where Phase 1 fails or misses improvements
- What Phase 1.5 should fix

## Files in This Directory

- `phase1_5_golden_set.json` — Complete metadata for all 7 RFP fixtures (validated by manual review)
- `PHASE1_5_GOLDEN_SET_README.md` — This file

## Structure of phase1_5_golden_set.json

```json
{
  "fixtures": {
    "fixture_name": {
      "file": "path/to/fixture.txt",
      "phase1_issues": { /* what Phase 1 gets wrong */ },
      "golden_truth": { /* correct metadata */ }
    }
  },
  "summary": {
    "key_improvements_needed": { /* 5 areas Phase 1.5 should address */ }
  }
}
```

## What Gets Validated

### Metadata Fields
- **title** — RFP title (not document-type header)
- **issuer** — Contracting authority name
- **due_date** — Submission deadline (not questions-due or other dates)
- **estimated_contract_value** — Contract value (for context)
- **contract_duration** — Project duration
- **key_sections** — Major document sections

### Additional Validation
- **title_source** — Where the title came from (`first_line`, `solicitation_title_field`, `inferred`)
- **title_confidence** — Confidence score (0.0–1.0) for Phase 1.5 to use
- **due_date_type** — Type of deadline (`submission_deadline`, `questions_due`, etc.)
- **section_detection_challenge** — Known issues with section extraction

## The 5 Key Gaps Phase 1.5 Should Address

### 1. **Title Extraction** — Document-Type Headers
**Issue:** All 5 UK RFPs have a document-type header as the first line (e.g., "LOCAL AUTHORITY PROCUREMENT NOTICE"), not the actual title.

**Phase 1 Behavior:** Extracts first non-empty line → gets wrong title

**Phase 1.5 Fix:** Look for "Solicitation Title:" field (or equivalent) to find the real title

**Example:**
```
uk_local_council_data_analytics.txt:
  Line 1: "LOCAL AUTHORITY PROCUREMENT NOTICE" ← Phase 1 extracts this (wrong)
  Line 3: "Solicitation Title: Integrated Council Data Analytics Platform" ← Correct title
```

**Fixtures Affected:** ALL 5 UK RFPs + simple_rfp (but simple_rfp actually gets it right)

---

### 2. **Date Disambiguation** — Multiple Dates
**Issue:** RFPs contain multiple dates (Posted, Questions Due, Closing). Phase 1 needs to pick submission deadline.

**Phase 1 Behavior:** Uses regex patterns; may miss or misinterpret dates

**Phase 1.5 Fix:** Understand date hierarchy (Closing/submission deadline > Questions Due > Posted)

**Example:**
```
complex_rfp.txt:
  Line 6: "Posted: 03-06-2026"        ← Posted date (not submission)
  Line 7: "Closing: 15 April, 2026"   ← SUBMISSION DEADLINE
  Line 8: "Questions Due: April 1st"  ← Earlier cutoff (not submission)
```

**Fixtures Affected:** complex_rfp.txt

---

### 3. **Section Heading Detection** — Title-Case Headings
**Issue:** UK RFPs sometimes use title-case headings instead of ALL CAPS. Phase 1 only recognizes ALL CAPS or numbered headings.

**Phase 1 Behavior:** Misses title-case headings like "Evaluation Factors"

**Phase 1.5 Fix:** Recognize semantic sections even with non-standard formatting

**Example:**
```
uk_transport_network_data_system.txt:
  Line 69: "Evaluation Factors" ← Title-case heading, Phase 1 won't detect
  Phase 1.5 should recognize this as a section header
```

**Fixtures Affected:** uk_transport_network_data_system.txt

---

### 4. **Requirement Categorization** — Mandatory vs Optional
**Issue:** Phase 1 extracts sections but doesn't categorize by importance (Mandatory, Optional, Nice-to-Have)

**Phase 1 Behavior:** No categorization; just extracts section bodies

**Phase 1.5 Fix:** Tag sections by type (MANDATORY_REQUIREMENTS, OPTIONAL_ENHANCEMENTS, EVALUATION_CRITERIA, etc.)

**Example:**
```
All UK RFPs have:
  "MANDATORY REQUIREMENTS" section (8 items)
  "OPTIONAL ENHANCEMENTS" section (4-6 items)
  "EVALUATION CRITERIA" section (scoring breakdown)

Phase 1.5 should tag each section's type so Phase 2 can process them differently.
```

**Fixtures Affected:** ALL fixtures

---

### 5. **Issuer Validation** — Compound Names
**Issue:** Some issuer names have compound structure (e.g., "Northern Universities Consortium (8 institutions)"). Need to validate the full entity name.

**Phase 1 Behavior:** Extracts the text but no validation; may truncate or misinterpret

**Phase 1.5 Fix:** Understand that parenthetical details are part of the entity name, not separate metadata

**Example:**
```
uk_university_research_data_repository.txt:
  "Contracting Authority: Northern Universities Consortium (8 institutions)"
  
Phase 1 extracts: "Northern Universities Consortium (8 institutions)" ✓ Correct
Phase 1.5 should: Validate that "(8 institutions)" is part of the name, not extra info
```

**Fixtures Affected:** uk_university_research_data_repository.txt (and potentially others)

---

## How to Use This Golden Set

### For Testing Phase 1.5:

1. **Read the golden_truth values** for each fixture
2. **Compare Phase 1 output** against golden_truth
3. **Run Phase 1.5 enhancement** on Phase 1 output
4. **Verify Phase 1.5 output** matches or closely approximates golden_truth
5. **Assign confidence scores** (Phase 1.5 should indicate how confident it is)

### Example Test Structure:

```python
def test_phase1_5_corrects_title():
    # Get Phase 1 output
    phase1_output = phase1_agent.run(fixture)
    assert phase1_output.title == "LOCAL AUTHORITY PROCUREMENT NOTICE"  # Wrong
    
    # Enhance with Phase 1.5
    phase1_5_output = phase1_5_agent.run(phase1_output)
    assert phase1_5_output.title == "Integrated Council Data Analytics Platform"  # Correct
    assert phase1_5_output.title_confidence > 0.9  # High confidence
```

---

## Key Statistics

| Metric | Value |
|--------|-------|
| **Total Fixtures** | 6 RFPs + 1 additional |
| **UK Government RFPs** | 5 (Local Council, NHS, Transport, University, Water) |
| **US Government RFPs** | 2 (simple_rfp, complex_rfp) |
| **Fields Validated** | title, issuer, due_date, sections, key_sections |
| **Critical Issues** | 5 (Title, Date, Sections, Categorization, Issuer) |
| **Phase 1 Pass Rate** | ~85% (gets titles wrong, misses sections, no categorization) |
| **Phase 1.5 Target** | >95% accuracy on golden_truth |

---

## What Phase 1.5 Should NOT Do

❌ Make API calls to external services
❌ Require user input for disambiguation
❌ Overwrite Phase 1 output without confidence scores
❌ Assume US date formats (be UK-aware)

---

## What Phase 1.5 CAN Do

✅ Use intelligent pattern matching (no APIs)
✅ Add confidence scores to all fields
✅ Flag ambiguous cases for review
✅ Correct obvious errors (wrong title extraction)
✅ Categorize sections by semantic type
✅ Validate and enhance Phase 1 metadata

---

## Next Steps

1. **Build Phase 1.5 agent** (implementation of EnhancedBidIntakeAgent)
2. **Run tests against golden set** (see test_phase1_5_spec.py)
3. **Measure accuracy:** # fixtures matching golden_truth / total
4. **If >90% match:** Phase 1.5 is ready for use
5. **If <90% match:** Refine logic and re-test

---

## Questions?

Refer to `test_phase1_5_spec.py` for concrete examples of what's expected.
