# Claude Code Guidance for bid-acceleration-engine

## Project Overview

A local-first AI pipeline for accelerating government and enterprise bid responses. The system chains discrete agents, each responsible for a stage of bid analysis and response generation.

**Current Phase:** Phase 2 - Requirement Extraction Agent

**Architecture:** 6-agent pipeline, all phases local-first (no external APIs)

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

- **Local-first principle:** All 6 agents must work entirely offline, no external APIs under any circumstances
- **Keep implementation intentionally focused:** Each agent does one thing well, no over-engineering
- **Validate Pydantic generics early:** `AgentResult[T]` must work before building on top
- **Mock nothing in tests:** Use real temp files and pytest fixtures
- **One commit = one complete feature:** Don't leave tests without code or code without tests
- **Prefer explicit over implicit:** Type hints, docstrings, and clear variable names
- **Avoid over-engineering:** No abstract base classes beyond what's documented, no premature refactoring
- **Use Claude Pro subscription only for development guidance:** Never call APIs from running code
