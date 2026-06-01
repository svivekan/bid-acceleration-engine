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
Raw RFP (.txt / .pdf / .docx)
     │
     ▼  Phase 1 — Bid Intake Agent                  ✅ COMPLETE
     │  Parse title, issuer, due date, sections (supports PDF, DOCX, TXT)
     │
     ▼  Phase 1.5 — Enhanced Bid Intake Agent        ✅ COMPLETE
     │  Title correction, section classification, requirement counting
     │
     ▼  Phase 2 — Requirement Extraction Agent       ✅ COMPLETE
     │  Extract every requirement; classify by category, priority, complexity
     │
     ▼  Phase 3 — Data Ingestion Agent               ✅ COMPLETE
     │  Recommend Azure ingestion tools, SHIR config, security, compliance
     │
     ▼  Phase 4 — Transformation Agent               ✅ COMPLETE
     │  ETL design, data quality rules, governance framework, SLA targets
     │
     ▼  Phase 5 — Analytics Agent                    🔨 BUILDING
     │  Synapse SQL, Power BI semantic layer, API exposure, row-level security
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
| Phase 1 — Bid Intake | ✅ Complete | 127 written · 127 passing |
| Phase 1.5 — Enhanced Bid Intake | ✅ Complete | 26 written · 26 passing |
| Phase 2 — Requirement Extraction | ✅ Complete | 25 written · 25 passing |
| Phase 3 — Data Ingestion Architecture | ✅ Complete | 18 written · 18 passing |
| Phase 4 — Transformation Architecture | ✅ Complete | 13 written · 13 passing |
| Schemas & Utilities | ✅ Complete | 50 written · 50 passing |
| **Total** | | **259 tests · 259 passing (100%)** |

> **PDF/DOCX Support Validated:** Phase 1 now supports .txt, .pdf, and .docx formats.
> Phase 1.5 enhances title accuracy and section classification on all formats.
> All test suites passing; pipeline ready for Phase 5 development.

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

### Phase 4 Output — `TransformationArchitecture`
```
Tool:              Fabric Pipeline (or Data Factory / Databricks / Stream Analytics)
Processing:        Batch ETL (schedule determined per RFP signals)
Architecture:      Ingestion → Fabric Pipeline → Lakehouse → Power BI
Data Quality:      Schema validation, mandatory field enforcement, reconciliation rules
Quality Rules:     PII detection & masking | Deduplication signals | Reconciliation tolerance
Governance:        Microsoft Purview lineage, Azure Monitor audit logging
Compliance:        GDPR, NHS DSPT (if detected), UK data residency (if required)
SLA targets:       Data freshness: as defined | RTO: 1 hour | RPO: 30 minutes | Availability: 99.9%
Key services:      Fabric Pipeline, Data Lakehouse, Power BI, Microsoft Purview, Azure Monitor
```

---

## Live Demo — Run This During the Call

The walkthrough shows how the system parses RFPs (PDF, DOCX, or TXT), extracts requirements, detects architectural signals, and recommends specific Azure services based on decision logic. Phases 1-4 are production-ready.

### Scenario 1: Local Council Digital Platform
```bash
uv run python walkthrough_phase1_to_phase4.py tests/fixtures/sample_bids/uk_local_council_data_analytics.txt
```

**Decision logic explained:**
- **Data sources:** 8 systems (Council Tax, Social Care, Housing, etc.) → moderate complexity
- **Freshness:** "Daily data refresh cycles" → batch ingestion (not streaming)
- **On-premise signals:** Oracle EBS, case management systems → requires Self-Hosted IR
- **Governance:** GDPR compliance, audit trails, DPIA required → enterprise-grade tools
- **Recommendation:** **Fabric Pipeline** (score: 1 = enterprise governance +1, <3 sources)
  - Why NOT Data Factory? Only 8 systems and daily batch (Fabric is sufficient & cost-effective)
  - Why NOT Event Hubs? No real-time signals, no event streaming keywords
  - SHIR config: 3-node HA cluster, ExpressRoute for secure on-prem connectivity, TLS 1.2+

### Scenario 2: NHS Trust Real-Time Clinical Integration
```bash
uv run python walkthrough_phase1_to_phase4.py tests/fixtures/sample_bids/uk_nhs_trust_population_health.txt
```

**Decision logic explained:**
- **Data sources:** 12 hospital systems (Epic EHR, labs, imaging) → high complexity
- **Freshness signals:** "Real-time patient data feeds" (4 feeds/day from Epic) → time-sensitive
- **Healthcare compliance:** NHS DSPT standards, clinical audit trails, PII protection
- **Recommendation:** **Data Factory** (score: 3+ = 12 sources +2, >10 dependencies +2, governance +1)
  - Why NOT Fabric? 12+ systems with complex orchestration needs (Fabric insufficient)
  - Why NOT Event Hubs? 4 feeds/day is scheduled batch, not continuous event streaming
  - SHIR config: 3-node HA, Managed Identity for NHS Azure subscription security

### Scenario 3: Transport Authority Real-Time Telematics
```bash
uv run python walkthrough_phase1_to_phase4.py tests/fixtures/sample_bids/uk_transport_network_data_system.txt
```

### PDF/DOCX Demo
To test with PDF or Word documents:
```bash
uv run python walkthrough_phase1_to_phase4.py tests/fixtures/sample_bids/your_bid_document.pdf
uv run python walkthrough_phase1_to_phase4.py tests/fixtures/sample_bids/your_bid_document.docx
```

**Decision logic explained:**
- **Data sources:** 450+ buses (GPS feeds) + 1000+ events/second traffic data → streaming signals
- **Freshness signals:** "Real-time location data", "continuous processing", "1000+ events per second" → streaming
- **Recommendation:** **Event Hubs + Stream Analytics** (streaming detected)
  - Why streaming? Keywords trigger: "real-time", "continuous", "events per second"
  - Data Lakehouse as sink for real-time dashboards
  - No SHIR needed (cloud-native APIs, not on-prem sources)
  - Stream Analytics jobs for real-time aggregation & capacity management

### Step 2 — Show the test suite
```bash
uv run pytest tests/ --tb=no -q
```
Expected: `259 passed in ~2s` — all phases tested, all scenarios validated.

Three real-world UK government scenarios (Council, NHS, Transport) plus Phase 4 transformation architecture validation.

### Step 3 — Open a fixture file to show a real RFP input
```
tests/fixtures/sample_bids/uk_local_council_data_analytics.txt
```

Shows the raw requirements the system is analyzing (MANDATORY REQUIREMENTS, OPTIONAL ENHANCEMENTS).

### Step 4 — Open the JSON output in results/ to show what the pipeline produces
```bash
cat results/uk_local_council_data_analytics_*_phase3_output.json | jq .
```

Shows the complete architectural recommendation:
- Tool selection & justification
- SHIR configuration (placement, HA nodes, network security, authentication)
- Security recommendations (encryption, firewall rules, credential rotation)
- Compliance checklist (GDPR, NHS DSPT, data residency)
- Architecture pattern diagram
- Assumptions & constraints

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

## What Comes Next — Phases 5–7

| Phase | Status | What it produces |
|---|---|---|
| **Phase 5** — Analytics Agent | 🔨 Building | Power BI semantic layer, Synapse SQL pools, API exposure, row-level security design |
| **Phase 6** — Review Agent | ⏳ Todo | Cross-phase validation, gaps flagged, compliance confirmation, requirements traceability |
| **Phase 7** — Delivery Plan Agent | ⏳ Todo | Phased delivery timeline, effort estimates, team structure, critical path milestones |

**When complete:** An Azure Solutions Architect drops in an RFP (PDF, DOCX, or TXT) and
receives a complete, justified Azure data architecture recommendation — covering ingestion,
transformation, analytics, and delivery — ready for expert review and direct inclusion in bid proposals.

**Current state:** Phases 1-4 production-ready and validated with real UK government RFPs.

---

## Repository Structure

```
bid-acceleration-engine/
├── src/bid_acceleration_engine/
│   ├── agents/                Phase 1–4 implementations (one folder per phase)
│   ├── schemas/               Pydantic data contracts (the "API" between agents)
│   └── utils/                 Shared helpers (document parsing, logging, validation)
├── specs/                     Written acceptance criteria per phase
├── tests/                     259 tests across Phases 1–4
├── results/                   JSON output from pipeline runs
├── walkthrough_phase1_to_phase4.py   ← Main demo (Phases 1–4)
└── MANAGER_BRIEFING.md        This file
```

**Status:** Phases 1–4 complete and production-ready. Phase 5 in development.

**Target user:** Azure Solutions Architects responding to UK government data platform RFPs.

**Input formats:** .txt, .pdf, .docx (Phase 1 automatically detects and parses all three)
