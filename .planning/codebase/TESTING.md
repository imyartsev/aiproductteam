# Testing Patterns

**Analysis Date:** 2026-05-08

## Test Framework

**Runner:**
- `pytest` >= 8.0
- Config: `pyproject.toml` (`[tool.pytest.ini_options]`)
- `asyncio_mode = "auto"` configured (pytest-asyncio >= 0.23 installed)

**Assertion Library:**
- Built-in `assert` statements (no third-party assertion library)

**Run Commands:**
```bash
pytest tests/              # Run all tests
pytest tests/ -v           # Verbose output
pytest tests/ -k "agents"  # Run specific test file by name
# Coverage: not configured — no pytest-cov or coverage.ini found
```

## Test File Organization

**Location:** Separate `tests/` directory at project root — NOT co-located with source

**Naming:**
- Test files: `test_<module>.py` — `test_agents.py`, `test_pipeline.py`
- Test functions: `test_<what_is_tested>` — `test_dry_run_pipeline_returns_state`, `test_po_agent_populates_task_spec`
- Helper functions: prefixed with underscore: `_make_mock_response`

**Structure:**
```
tests/
├── __init__.py
├── test_agents.py      # Unit tests for BaseAgent and POAgent
└── test_pipeline.py    # Integration tests for pipeline + save_results
```

## Test Structure

**Suite Organization:**
- No `describe`-style grouping — flat list of test functions per file
- No `class`-based test organization (no `class TestFoo`)
- Module-level docstring describes the test file's purpose

```python
"""Тесты агентов с мок-ответами Claude API."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Path setup for imports — manual sys.path manipulation
sys.path.insert(0, str(Path(__file__).parent.parent))

# Env var preset before imports
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from agents.base import BaseAgent
from orchestrator.state import ProjectState, TaskSpec
```

**Patterns:**
- No `setUp`/`tearDown` — no shared test state
- No pytest fixtures (no `@pytest.fixture` in any test file)
- `tmp_path` built-in pytest fixture used in one test for filesystem isolation
- Env vars set with `os.environ.setdefault()` at module level before imports

## Mocking

**Framework:** `unittest.mock` — `MagicMock` and `patch` decorator

**Primary mock target:** `agents.base._get_client` — patches the module-level singleton factory

**Pattern used throughout:**
```python
@patch("agents.base._get_client")
def test_base_agent_run(mock_get_client):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_mock_response("Hello from agent")
    mock_get_client.return_value = mock_client

    class TestAgent(BaseAgent):
        role = "po"

    agent = TestAgent()
    result = agent.run("test prompt")
    assert result == "Hello from agent"
    mock_client.messages.create.assert_called_once()
```

**Mock response factory:** Reusable helper builds a mock Anthropic-style response object:
```python
def _make_mock_response(text: str):
    block = MagicMock()
    block.type = "text"
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response
```

**Note:** The mock response structure matches the Anthropic SDK (`response.content[0].text`), but the actual `BaseAgent.run()` uses the OpenAI SDK (`response.choices[0].message.content`). This is a mismatch — see CONCERNS.md.

**What to Mock:**
- External API calls: always mock `agents.base._get_client`
- Avoid real network calls in any test

**What NOT to Mock:**
- `orchestrator.pipeline.run_pipeline` with `dry_run=True` — the pipeline has a built-in test mode, use it directly

## Fixtures and Factories

**Test Data:**
- Inline construction — `ProjectState(raw_task="Build a todo app")` directly in each test
- No separate fixtures file or `conftest.py`

**`tmp_path` usage:**
```python
def test_save_results_creates_files(tmp_path):
    state = run_pipeline("Test task", dry_run=True)
    project_dir = save_results(state, output_dir=str(tmp_path))
    files = list(project_dir.iterdir())
    assert len(files) == 6
```

**Location:** No shared fixtures — all test data is local to each test function.

## Coverage

**Requirements:** None enforced — no `pytest-cov`, no coverage configuration, no minimum threshold

**View Coverage:**
```bash
# Not configured. To add:
pip install pytest-cov
pytest tests/ --cov=agents --cov=orchestrator --cov-report=term-missing
```

## Test Types

**Unit Tests** (`tests/test_agents.py`):
- Scope: individual agent `run()` and `process()` methods
- API calls fully mocked via `@patch`
- Inline `TestAgent` subclass created inside test for isolated `BaseAgent` testing

**Integration Tests** (`tests/test_pipeline.py`):
- Scope: full pipeline execution and file output
- Uses `dry_run=True` mode — no mocking needed, pipeline substitutes stub output
- Tests both `run_pipeline()` and `save_results()` together

**E2E Tests:** Not present — no tests that call the real DeepSeek API

## Common Patterns

**Dry-run integration testing:**
```python
def test_dry_run_all_artifacts_populated():
    state = run_pipeline("Hello World", dry_run=True)
    assert state.task_spec.content != ""
    assert state.arch_decision.content != ""
    # ... assert all 6 artifact fields populated
```

**Verifying API call arguments:**
```python
call_kwargs = mock_client.messages.create.call_args.kwargs
system = call_kwargs["system"]
assert system[0]["cache_control"] == {"type": "ephemeral"}
```

**Inline agent subclass for unit testing BaseAgent:**
```python
class TestAgent(BaseAgent):
    role = "po"

agent = TestAgent()
result = agent.run("test prompt")
```

**sys.path manipulation** — both test files insert project root before any local imports:
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```
This indicates `conftest.py` or `pythonpath` configuration in `pyproject.toml` is missing.

---

*Testing analysis: 2026-05-08*
