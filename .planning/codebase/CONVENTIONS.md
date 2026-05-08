# Coding Conventions

**Analysis Date:** 2026-05-08

## Naming Patterns

**Files:**
- Modules named after their role in snake_case: `base.py`, `po.py`, `file_ops.py`, `git_ops.py`
- Agent files match role string used in `BaseAgent.role`: `po.py` → `role = "po"`
- Test files prefixed with `test_`: `test_agents.py`, `test_pipeline.py`
- Private helpers prefixed with underscore: `_get_client`, `_load_prompt`, `_git`, `_make_mock_response`

**Classes:**
- PascalCase throughout: `BaseAgent`, `POAgent`, `ProjectState`, `TaskSpec`, `ArchDecision`
- Agent classes suffixed with `Agent`: `POAgent`, `ArchitectAgent`, `DevAgent`
- Pydantic artifact models named after the artifact, no suffix: `TaskSpec`, `CodeArtifact`, `TestReport`

**Functions:**
- snake_case for all functions and methods: `run_pipeline`, `save_results`, `read_file`, `write_file`
- `process()` is the standard method signature for all agent subclasses
- `run()` is the API-call method in `BaseAgent`

**Variables:**
- snake_case: `mock_client`, `project_dir`, `artifact_field`, `dry_run`
- Module-level singletons with underscore prefix: `_client` in `agents/base.py`
- Constants in UPPER_SNAKE_CASE: `CHAT_MODEL`, `REASONER_MODEL`, `STEPS`

## Code Style

**Formatting:**
- No formatter configured (no `.prettierrc`, `black`, or `ruff` in `pyproject.toml`)
- Indentation: 4 spaces consistently
- String quotes: double quotes for user-facing strings, single where mixed

**Linting:**
- No linter configured (no `flake8`, `pylint`, `ruff`, `mypy` config found)
- Type hints present throughout but not enforced by tooling

## Import Organization

**Order observed:**
1. `from __future__ import annotations` — always first line in all modules
2. Standard library (`os`, `pathlib`, `subprocess`, `sys`, `argparse`)
3. Third-party (`openai`, `pydantic`, `rich`, `dotenv`)
4. Local imports — relative within package (`from .base import BaseAgent`), absolute for cross-package (`from orchestrator.state import ProjectState`)

**Path Aliases:**
- None configured — plain absolute imports used for cross-package references

**Relative imports:**
- Used within `agents/` package: `from .base import BaseAgent`, `from .po import POAgent`
- Agents import from orchestrator with absolute path: `from orchestrator.state import ...`

## Type Annotations

**Pattern:** Full type hints on all function signatures. Return types always annotated.

```python
def _get_client() -> OpenAI: ...
def _load_prompt(name: str) -> str: ...
def run(self, user_message: str) -> str: ...
def run_pipeline(task: str, dry_run: bool = False) -> ProjectState: ...
def save_results(state: ProjectState, output_dir: str | None = None) -> Path: ...
```

**Union syntax:** Python 3.10+ `X | Y` syntax used (enabled by `from __future__ import annotations`):
- `str | None` instead of `Optional[str]`
- `OpenAI | None` for nullable module-level singleton

## Error Handling

**Pattern:** No explicit error handling observed in the codebase. Exceptions propagate naturally:
- `os.environ["DEEPSEEK_API_KEY"]` raises `KeyError` if missing — no try/except wrapper
- File reads in `_load_prompt` raise `FileNotFoundError` unhandled
- API calls in `BaseAgent.run()` propagate OpenAI SDK exceptions directly

**Implication:** All error handling is left to the caller or allowed to crash with a traceback.

## Logging

**Framework:** `rich.console.Console` used in `orchestrator/pipeline.py` only

**Patterns:**
- Rich markup for colored output: `[bold cyan]`, `[bold yellow]`, `[green]`, `[dim]`
- Progress messages printed directly to console during pipeline execution
- No logging module (`import logging`) used anywhere
- No structured logging

```python
# orchestrator/pipeline.py
console = Console(highlight=False, legacy_windows=False)
console.print(Panel(f"[bold cyan]Задача:[/] {task}", title="AI Product Team"))
console.print(f"\n[bold yellow]>> {name}[/] обрабатывает задачу...")
console.print(f"[green]  OK[/] {preview}...")
```

## Comments

**Style:** Docstrings for classes and public methods; inline comments for non-obvious logic

**Docstring pattern:**
- Module-level: one-line description in triple quotes at top of test files
- Class docstrings: one-line Russian description explaining artifact purpose
- Method docstrings: one-line Russian description for public methods

```python
class BaseAgent:
    """Базовый класс агента. Загружает системный промпт и вызывает DeepSeek API."""

def run(self, user_message: str) -> str:
    """Отправляет сообщение агенту и возвращает текстовый ответ."""
```

**Inline comments:** Used sparingly for intent clarification:
```python
# Используем первые 40 символов задачи как имя папки  (pipeline.py:55)
# Определения инструментов для Claude tool use API   (file_ops.py:23)
```

**Language:** Russian for all comments and docstrings.

## Module Design

**Exports:** `agents/__init__.py` uses explicit `__all__` list with all six agent classes

**Barrel pattern:** `agents/__init__.py` re-exports all agents so callers use `from agents import POAgent`

**TOOL_DEFINITIONS pattern:** Each `tools/` module exposes a `TOOL_DEFINITIONS` list alongside its functions — JSON schema definitions for Claude tool use API. Example: `tools/file_ops.py`, `tools/code_exec.py`, `tools/git_ops.py`

## Pydantic Conventions

**Inheritance hierarchy:**
```python
BaseModel → Artifact(content: str = "") → TaskSpec / ArchDecision / TechSpec / ...
BaseModel → ProjectState (aggregates all artifacts via Field(default_factory=...))
```

**Field defaults:** All optional fields use `Field(default_factory=ArtifactSubclass)` — never `None`

**No validators:** No `@field_validator` or `@model_validator` decorators present — content is always a raw string

## Class Attribute Conventions (BaseAgent subclasses)

All agent subclasses declare exactly two class-level attributes before any methods:
```python
class POAgent(BaseAgent):
    role = "po"           # matches prompts/<role>.md filename
    use_heavy_model = True  # or absent/False
```

Note: `base.py` uses `use_reasoner` but subclasses declare `use_heavy_model` — these are inconsistent (see CONCERNS.md).

---

*Convention analysis: 2026-05-08*
