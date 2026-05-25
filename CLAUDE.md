# Claude Code Guidance for bid-acceleration-engine

## Project Overview

A local-first AI pipeline for recommending **Azure data architectures** for government and enterprise data migration RFPs.

**NOT a general bid response tool.** This is specifically for **data architecture**: recommending how to ingest, transform, store, and consume data on Azure.

**Context:** Built for an **Azure-only consulting company**. This tool helps Azure Solutions Architects rapidly generate data architecture recommendations for UK government RFPs (Local Council, NHS, Transport, Education, Water Authority).

**Current Progress:** Phases 1-4 complete and validated. Building Phase 5.

**Architecture:** 7-agent pipeline, all phases local-first (no external APIs), all solutions Azure-only

## Azure Consulting Company Context

This tool is purpose-built for an Azure consulting firm. Key principles:

- **Azure-only:** All solutions must use Azure services. No AWS, GCP, or hybrid recommendations.
- **Consulting-ready:** Generated solutions are detailed enough to include directly in bid proposals.
- **Credibility:** Quality bar is high—recommendations reflect on consulting firm reputation.
- **UK Government:** Solutions address UK compliance (GDPR, NHS standards, Cabinet Office security guidance).
- **Well-Architected:** All Phase 3+ solutions reference Azure Well-Architected Framework.
- **Patterns-driven:** Leverage Microsoft's reference architectures and best practices.

**Target User:** Azure Solutions Architects responding to government RFPs

## The 7-Phase Data Architecture Pipeline

Each phase builds on the previous one. Output from one phase is input to the next.

| Phase | Agent | Status | Input | Output |
|-------|-------|--------|-------|--------|
| 1 | `bid_intake_agent` | ✓ DONE | RFP `.txt` file | `BidDocument` (metadata + raw text) |
| 2 | `requirement_extraction_agent` | ✓ DONE | `BidDocument` | `ExtractedRequirement[]` (data/integration needs) |
| 3 | `data_ingestion_agent` | ✓ DONE | Requirements | `IngestionArchitecture` (Event Hubs, Data Factory, SHIR, compliance) |
| 4 | `transformation_agent` | ✓ DONE | Ingestion arch + Requirements | `TransformationArchitecture` (ETL, Databricks, quality, lineage) |
| 5 | `analytics_agent` | BUILDING | Transformation arch | `AnalyticsArchitecture` (Synapse SQL, Power BI, APIs, security) |
| 6 | `review_agent` | TODO | All architectures | `ReviewResult` (validated, gaps flagged, compliance confirmed) |
| 7 | `delivery_plan_agent` | TODO | Validated architecture | `DeliveryPlan` (phased timeline, milestones, team structure) |

**Data Flow:**
```
RFP → Phase 1 → BidDocument
         ↓
      Phase 2 → Requirements
         ↓
      Phase 3 → Ingestion Architecture
         ↓
      Phase 4 → Transformation Architecture
         ↓
      Phase 5 → Analytics Architecture
         ↓
      Phase 6 → Validated Full Architecture
         ↓
      Phase 7 → Phased Delivery Plan
```

**Key Constraint:** Each phase is a pure transformation. No external APIs, no network calls, all processing local-only.

## Tech Stack

- **Python 3.12+** with `uv` (package manager + virtual environment)
- **Ruff** for linting and formatting
- **pytest** for testing
- **Pydantic v2** for data validation (strong typing, JSON serialization)
- **src-based layout**: `src/bid_acceleration_engine/`

## Project Structure

```
bid-acceleration-engine/
├── src/bid_acceleration_engine/
│   ├── agents/                    # Agent modules
│   │   └── bid_intake_agent/      # Phase 1: parses raw bids
│   ├── schemas/                   # Pydantic models (data contracts)
│   ├── utils/                     # Shared helpers (logging, file I/O)
│   └── prompts/                   # Prompt templates (future use)
├── tests/                         # Test suite mirroring src/
├── pyproject.toml                 # uv + Ruff + pytest config
└── .python-version                # Python version pin
```

## Development Workflow

### Running Commands

All commands use `uv run` to run within the project environment:

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/bid_acceleration_engine

# Run linter
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/
```

### Creating New Code

1. **Always use src-based layout**: Code goes in `src/bid_acceleration_engine/`, tests go in `tests/`
2. **Import style**: `from bid_acceleration_engine.agents.bid_intake_agent import ...` (not relative imports)
3. **Use Pydantic for all data structures**: Never use bare dicts for inter-agent communication
4. **Keep agents pure**: Agents are transformations: input → work → typed output
5. **No external APIs in Phase 1**: All processing is local-only

### Linting & Formatting

Ruff is configured with:
- **Line length:** 120 characters
- **Target version:** Python 3.12
- **Rules enabled:** E (errors), F (pyflakes), I (isort), UP (upgrades)

Run before committing:
```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
uv run pytest
```

### Small Commits

Commit frequently with focused, atomic changes:
- One feature, one schema, one utility = one commit
- Test additions go in the same commit as the code they test
- Commit messages: imperative mood, < 50 characters

**Examples:**
- `feat: add AgentResult schema`
- `test: add date_parser unit tests`
- `chore: update .gitignore`

## Design Principles

### 1. Strong Typing with Pydantic v2

All data flowing between agents is strongly typed using Pydantic models:

```python
from pydantic import BaseModel, ConfigDict

class BidDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    title: str
    raw_text: str
    # ... more fields
```

**Why:** Catches schema drift early, enables IDE autocompletion, serializes to/from JSON automatically.

### 2. Shared Schemas as the Dependency Root

- All Pydantic models live in `schemas/`
- `schemas/` imports nothing from `agents/`, `utils/`, or `prompts/`
- Other modules import from `schemas/` freely
- This prevents circular dependencies and decouples agents

### 3. Agents Are Pure Transformations

Each agent:
- Receives typed input (e.g., `Path`, `BidDocument`)
- Performs work
- Emits typed output wrapped in `AgentResult[T]`

```python
class BidIntakeAgent(BaseAgent):
    def run(self, source_path: Path) -> AgentResult[BidDocument]:
        # read → parse → construct → return
```

### 4. Utilities Are Stateless

Functions in `utils/` have no side effects and no imports from `agents/`:

- `logging.get_logger(name: str) -> logging.Logger`
- `file_io.read_text_file(path: Path) -> str`
- `date_parser.parse_date_string(raw: str) -> date | None`

### 5. Local-First, No External APIs (All Phases)

- No network calls to external services
- No Claude API calls (no programmatic API usage)
- No OpenAI API or other external ML/AI APIs
- All processing in-memory on local machine
- Claude Code can be used at runtime for intelligent processing (locally, not via API)
- Claude Pro subscription used for consulting and intelligent processing, never API calls

## Testing Strategy

- **Unit tests** for pure functions (parsers, utilities)
- **Integration tests** for agents (using `tmp_path` fixture)
- **Fixtures** in `conftest.py` for sample bid files
- **Test coverage:** `uv run pytest --cov=src/bid_acceleration_engine`

## Future Extensibility

The architecture supports adding new agents without modifying existing code:

1. **New agent:** Create `src/bid_acceleration_engine/agents/your_agent/`
2. **New data model:** Add to `src/bid_acceleration_engine/schemas/your_model.py`
3. **Shared utility:** Add to `src/bid_acceleration_engine/utils/`
4. **Pipeline integration:** Update `pipeline.py` to chain the new agent

All agents use the same `BaseAgent` interface and same schema patterns.

## Debugging

- **Run pytest in verbose mode:** `uv run pytest -v`
- **Filter tests:** `uv run pytest tests/agents/test_bid_intake_agent.py -v`
- **Check imports:** `uv run python -c "import bid_acceleration_engine; print(bid_acceleration_engine.__version__)"`
- **Inspect Pydantic:** Use `model.model_dump(mode='json')` to see JSON output

## Common Tasks

### Add a new dependency
```bash
uv add package_name                    # runtime
uv add --dev package_name              # dev only
```

### Create a new test file
```bash
# Create tests/agents/test_my_agent.py
# Import fixtures from conftest.py
# Use uv run pytest tests/agents/test_my_agent.py
```

### Run a specific test
```bash
uv run pytest tests/agents/test_bid_intake_agent.py::test_happy_path -v
```

## Notes for Claude

### General Principles
- **Data architecture focus:** This tool is for recommending Azure data solutions, not general bid responses. Each phase answers a specific question: How do we ingest? How do we transform? How do we serve?
- **Local-first principle:** All 7 agents must work entirely offline, no external APIs under any circumstances
- **Keep implementation intentionally focused:** Each agent does one thing well, no over-engineering
- **Validate Pydantic generics early:** `AgentResult[T]` must work before building on top
- **Mock nothing in tests:** Use real temp files and pytest fixtures
- **One commit = one complete feature:** Don't leave tests without code or code without tests
- **Prefer explicit over implicit:** Type hints, docstrings, and clear variable names
- **Avoid over-engineering:** No abstract base classes beyond what's documented, no premature refactoring
- **Use Claude Pro subscription only for development guidance:** Never call APIs from running code
- **Phase sequence matters:** Don't skip phases or reorder them. Phases 4-7 depend on Phases 1-3.

### Azure-Specific Principles (Phase 3+)
- **Azure-only solutions:** All Phase 3 solution outlines must recommend Azure services only. No comparative analysis with other clouds.
- **Consulting credibility:** Assume generated solutions will be included in actual bid proposals. Quality and accuracy are critical.
- **Well-Architected Framework:** Reference Microsoft's five pillars: Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency.
- **UK Government compliance:** Solutions should address GDPR, NHS Data Security and Protection Toolkit (DSPT), Cabinet Office security guidelines.
- **Reference architectures:** Leverage Microsoft's published reference architectures on GitHub (Azure Architecture Center).
- **Service specificity:** Recommend specific Azure services (App Service, SQL Database, Cosmos DB) with SKU/tier guidance where appropriate.
- **Managed services preference:** Recommend managed Azure services over IaaS where it aligns with consulting best practices.
