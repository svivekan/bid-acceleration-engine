# Bid Acceleration Engine — Manager Briefing

> **Purpose of this document:** Talking-point guide for an informal screen share.
> Keep this open during the conversation — it contains stats, demo commands, and the roadmap.

---

## What This Is (and Is Not)

> **This is not a general bid writing tool.**
> It is specifically a **data architecture recommendation engine** — built for Azure Solutions
> Architects responding to UK government RFPs that involve data migration, ingestion,
> transformation, or analytics on Azure.

---

## The Problem We Are Solving

When an Azure Solutions Architect receives a UK government RFP (Council, NHS, Transport,
Water Authority, etc.) involving a data platform, they face several days of mechanical work
before any real thinking begins:

- Reading and re-reading the RFP to extract every data and integration requirement
- Classifying which are mandatory, which are compliance-driven, which carry architectural risk
- Mapping requirements to Azure services — with justification for each choice
- Producing a data architecture covering ingestion, transformation, analytics, and delivery

This project **automates that mechanical extraction and mapping** so architects can spend
their time on insight, differentiation, and defensible recommendations — not classification.

---

## What Has Been Built

A **7-agent pipeline**, built in Python, running fully locally (no external API calls).
Drop in an RFP text file; get back a structured, justified Azure data architecture.

### Pipeline Overview

```
Raw RFP (.txt)
     │
     ▼  Phase 1 — Bid Intake Agent                  ✅ COMPLETE
     │  Parse title, issuer, due date, sections
     │
     ▼  Phase 2 — Requirement Extraction Agent       ✅ COMPLETE
     │  Extract every requirement; classify by category, priority, complexity
     │
     ▼  Phase 3 — Data Ingestion Agent               ✅ COMPLETE
     │  Recommend Azure ingestion tools, SHIR config, security, compliance
     │
     ▼  Phase 4 — Transformation Agent               🔨 BUILDING NOW
     │  ETL design, Databricks/Synapse, data quality, lineage
     │
     ▼  Phase 5 — Analytics Agent                    ⏳ TODO
     │  Synapse SQL, Power BI, API layer, row-level security
     │
     ▼  Phase 6 — Review Agent                       ⏳ TODO
     │  Validated architecture, gaps flagged, compliance confirmed
     │
     ▼  Phase 7 — Delivery Plan Agent                ⏳ TODO
        Phased timeline, milestones, team structure
```

---

## Progress at a Glance

| Phase | Status | Tests |
|---|---|---|
| Phase 1 — Bid Intake | ✅ Complete | 127 written · 122 passing |
| Phase 2 — Requirement Extraction | ✅ Complete | 25 written · 24 passing |
| Phase 3 — Data Ingestion Architecture | ✅ Complete | 18 written · 18 passing |
| Schemas & Utilities | ✅ Complete | 44 written · 44 passing |
| **Total** | | **214 tests · 208 passing (97%)** |

> The 6 failing tests are known, documented issues (1 test has a setup bug in its fixture;
> 5 tests check for a contract value field not yet present in the sample RFP fixtures).
> Neither failure reflects a defect in the pipeline logic.

---

## What Each Phase Produces

### Phase 1 Output — `BidDocument`
```
BidDocument
  ├── title:     "Data Analytics Platform — Metropolitan Borough Council"
  ├── issuer:    "Metropolitan Borough Council"
  ├── due_date:  2026-03-15
  ├── word_count: 3,241
  └── sections:  [ BACKGROUND, MANDATORY REQUIREMENTS, OPTIONAL FEATURES, ... ]
```

### Phase 2 Output — `ExtractedRequirement[]`
```
Requirement #1
  Text:     "The system must support real-time data ingestion from IoT sensors..."
  Category:  Technical
  Priority:  High
  Complexity: Complex
  Mandatory: True
  Section:   MANDATORY REQUIREMENTS
```

### Phase 3 Output — `DataIngestionArchitecture`
```
Tool:              Azure Data Factory  (or Fabric Pipeline / Event Hubs)
Architecture:      On-Prem Source → Self-Hosted IR → Data Factory → Synapse
On-prem sources:   SQL Server, Oracle
SHIR config:       HA (3 nodes), ExpressRoute, Managed Identity, TLS 1.2+
Compliance:        GDPR checklist, UK data residency (UK South / UK West)
Key services:      Azure Data Factory, SHIR, Key Vault, Monitor, Synapse Analytics
```

---

## Live Demo — Run This During the Call

### Step 1 — Run the full pipeline (Phases 1, 2 & 3)
```bash
uv run python walkthrough_phase1_to_phase3.py tests/fixtures/sample_bids/uk_local_council_data_analytics.txt
```

Try other RFP fixtures for different results:
```bash
# NHS Trust
uv run python walkthrough_phase1_to_phase3.py tests/fixtures/sample_bids/uk_nhs_trust_population_health.txt

# Transport
uv run python walkthrough_phase1_to_phase3.py tests/fixtures/sample_bids/uk_transport_network_data_system.txt
```

### Step 2 — Show the test suite
```bash
uv run pytest tests/ --tb=no -q
```
Expected: `208 passed, 6 failed in ~1s`

### Step 3 — Open a fixture file to show a real RFP input
```
tests/fixtures/sample_bids/uk_local_council_data_analytics.txt
```

### Step 4 — Open the JSON output in results/ to show what the pipeline produces
The walkthrough saves Phase 1, 2, and 3 JSON outputs to `results/`.

---

## Key Design Decisions Worth Highlighting

| Decision | Why |
|---|---|
| **Azure data architecture focus** | Purpose-built for data platform bids — not a generic bid writer |
| **Local-first, no API calls** | No latency, no cost, no RFP data leaving the machine |
| **Pydantic v2 throughout** | Every inter-agent handoff is fully typed and validated |
| **Stateless agents** | Pure input → output; easy to test, easy to compose |
| **Azure-only recommendations** | Aligned to our practice; no AWS/GCP drift |
| **Well-Architected Framework** | Phase 3+ solutions reference Microsoft's five pillars: Reliability, Security, Cost Optimisation, Operational Excellence, Performance Efficiency |
| **UK compliance built in** | GDPR, NHS DSPT, Cabinet Office — detected and addressed automatically |
| **Spec-driven development** | Each phase has a written spec; tests validate against it |

---

## What Comes Next — Phases 4–7

| Phase | Status | What it produces |
|---|---|---|
| **Phase 4** — Transformation Agent | 🔨 Building now | ETL/ELT design, Databricks or Synapse Pipelines, data quality rules, lineage |
| **Phase 5** — Analytics Agent | ⏳ Todo | Synapse Analytics SQL pools, Power BI semantic layer, API exposure, row-level security |
| **Phase 6** — Review Agent | ⏳ Todo | Cross-phase validation: gaps flagged, compliance confirmed, requirements traced |
| **Phase 7** — Delivery Plan Agent | ⏳ Todo | Phased delivery timeline, effort estimates, team structure, milestones |

When all seven phases are complete, an Azure Solutions Architect drops in an RFP and
receives a complete, justified Azure data architecture recommendation — covering ingestion
through to analytics and delivery — ready for expert review and inclusion in the bid.

---

## Repository

```
bid-acceleration-engine/
├── src/bid_acceleration_engine/
│   ├── agents/        Phase implementations (one folder per phase)
│   ├── schemas/       Pydantic data contracts (the "API" between agents)
│   └── utils/         Shared helpers
├── specs/             Written acceptance criteria per phase
├── tests/             214 tests across all phases
└── walkthrough_phase1_to_phase3.py   ← run this for the demo
```

**Target user:** Azure Solutions Architects responding to UK government data platform RFPs.
