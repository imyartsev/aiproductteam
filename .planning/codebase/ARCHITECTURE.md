<!-- refreshed: 2026-05-08 -->
# Architecture

**Analysis Date:** 2026-05-08

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                        main.py (CLI)                         │
│                  argparse entry point                        │
└─────────────────────────┬───────────────────────────────────┘
                           │ run_pipeline(task, dry_run)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              orchestrator/pipeline.py                        │
│   Sequential STEPS loop: 6 agents × process(state)          │
└──────┬──────┬──────┬──────┬──────┬──────────────────────────┘
       │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼
   POAgent ArchitectAgent AnalystAgent DevAgent QAAgent DevOpsAgent
   `agents/po.py`  `agents/architect.py`  ...`agents/devops.py`
       │      │      │      │      │      │
       └──────┴──────┴──────┴──────┴──────┘
                           │ BaseAgent.run() → DeepSeek API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              orchestrator/state.py (ProjectState)            │
│  raw_task → task_spec → arch_decision → tech_spec            │
│          → code_artifact → test_report → deploy_config       │
└─────────────────────────┬───────────────────────────────────┘
                           │ save_results()
                           ▼
┌─────────────────────────────────────────────────────────────┐
│    projects/<slug>/  (Markdown-файлы артефактов)             │
│  01_task_spec.md  02_arch_decision.md  03_tech_spec.md       │
│  04_code.md  05_test_report.md  06_deploy_config.md          │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| CLI Entry Point | Парсинг аргументов, вызов pipeline | `main.py` |
| Pipeline Orchestrator | Последовательный запуск агентов, dry-run, сохранение | `orchestrator/pipeline.py` |
| ProjectState | Pydantic-модель общего состояния, передаётся через весь pipeline | `orchestrator/state.py` |
| BaseAgent | Загрузка system prompt, вызов DeepSeek API через openai SDK | `agents/base.py` |
| POAgent | Преобразует raw_task в user stories и критерии приёмки | `agents/po.py` |
| ArchitectAgent | Читает task_spec, формирует архитектурные решения (стек, ADR) | `agents/architect.py` |
| AnalystAgent | Читает task_spec + arch_decision, создаёт tech_spec с API-контрактами | `agents/analyst.py` |
| DevAgent | Читает tech_spec, генерирует код | `agents/dev.py` |
| QAAgent | Читает tech_spec + code_artifact, создаёт test_report | `agents/qa.py` |
| DevOpsAgent | Читает arch_decision + code_artifact + test_report, создаёт deploy_config | `agents/devops.py` |
| File Tools | read/write/list файлов, TOOL_DEFINITIONS для API | `tools/file_ops.py` |
| Code Tools | Запуск Python-кода в subprocess | `tools/code_exec.py` |
| Git Tools | git status / commit | `tools/git_ops.py` |

## Pattern Overview

**Overall:** Sequential Pipeline with Shared Mutable State

**Key Characteristics:**
- Каждый агент получает единственный объект `ProjectState` и возвращает его обратно с заполненным артефактом
- Агенты работают строго последовательно — каждый следующий читает артефакты предыдущих
- Состояние передаётся по ссылке через мутацию Pydantic-объекта, а не через очередь сообщений
- Dry-run режим обходит все API-вызовы, заполняя артефакты заглушками `[dry-run] <name> output`
- Инструменты (`tools/`) реализованы, но агентами в текущей реализации не вызываются — присутствуют как заготовки

## Layers

**Presentation Layer (CLI):**
- Purpose: Принять задачу от пользователя, вывести прогресс через `rich`
- Location: `main.py`, `orchestrator/pipeline.py` (console.print)
- Contains: argparse, Rich Console, форматирование вывода
- Depends on: Orchestrator layer
- Used by: Пользователь напрямую

**Orchestration Layer:**
- Purpose: Управление последовательностью агентов, dry-run, сохранение результатов
- Location: `orchestrator/pipeline.py`
- Contains: Список STEPS, функции `run_pipeline` и `save_results`
- Depends on: Agents layer, State layer
- Used by: Presentation layer

**State Layer:**
- Purpose: Единственный источник истины для всего pipeline
- Location: `orchestrator/state.py`
- Contains: Pydantic BaseModel — `ProjectState` и 6 Artifact-подклассов
- Depends on: pydantic
- Used by: Orchestration layer, Agents layer

**Agents Layer:**
- Purpose: Реализация каждой роли продуктовой команды
- Location: `agents/`
- Contains: `BaseAgent` + 6 конкретных агентов
- Depends on: State layer, DeepSeek API (через openai SDK), `prompts/`
- Used by: Orchestration layer

**Prompts Layer:**
- Purpose: System prompts для каждого агента, хранятся отдельно от кода
- Location: `prompts/` (po.md, architect.md, analyst.md, dev.md, qa.md, devops.md)
- Contains: Markdown-файлы с инструкциями для ролей
- Depends on: Nothing
- Used by: `agents/base.py:_load_prompt()`

**Tools Layer:**
- Purpose: Инструменты для агентов (file I/O, code exec, git) — TOOL_DEFINITIONS для API
- Location: `tools/`
- Contains: Python-функции и JSON-схемы tool use
- Depends on: stdlib (subprocess, pathlib)
- Used by: Agents layer (потенциально, сейчас не интегрированы)

## Data Flow

### Primary Request Path

1. Пользователь вызывает `main.py "задача"` — argparse в `main.py:17-38`
2. `run_pipeline(task)` создаёт `ProjectState(raw_task=task)` — `orchestrator/pipeline.py:24-25`
3. Цикл по `STEPS`: для каждого агента вызывается `agent.process(state)` — `orchestrator/pipeline.py:29-47`
4. `agent.process()` формирует строковый `prompt` из нужных полей `state` — например `agents/analyst.py:10-14`
5. `BaseAgent.run(prompt)` отправляет запрос DeepSeek API — `agents/base.py:40-51`
6. Ответ записывается в соответствующий артефакт `state` — например `state.tech_spec = TechSpec(content=result)`
7. После завершения цикла `save_results(state)` пишет 6 Markdown-файлов в `projects/<slug>/` — `orchestrator/pipeline.py:52-71`

### Dry-Run Path

1. При `--dry-run` pipeline заходит в ветку `if dry_run` — `orchestrator/pipeline.py:32-38`
2. Каждый артефакт заполняется строкой `[dry-run] <AgentName> output` без API-вызовов
3. Сохранение в файлы происходит как обычно

### Context Accumulation (Цепочка зависимостей агентов)

```
raw_task
  └─→ POAgent → task_spec
                  └─→ ArchitectAgent → arch_decision
                        └─→ AnalystAgent (task_spec + arch_decision) → tech_spec
                                └─→ DevAgent → code_artifact
                                      └─→ QAAgent (tech_spec + code_artifact) → test_report
                                            └─→ DevOpsAgent (arch_decision + code + test_report) → deploy_config
```

**State Management:**
- Единственный объект `ProjectState` мутируется по месту в каждом `agent.process(state)`
- Нет параллельности — строго последовательный доступ
- Нет персистентного хранилища между запусками — только файловый вывод в `projects/`

## Key Abstractions

**Artifact:**
- Purpose: Базовый класс для всех артефактов pipeline — обёртка над строкой `content`
- Examples: `orchestrator/state.py:6-7`, все 6 подклассов в `orchestrator/state.py:10-31`
- Pattern: Pydantic BaseModel с единственным полем `content: str = ""`

**BaseAgent:**
- Purpose: Загружает system prompt из `prompts/<role>.md`, создаёт DeepSeek-клиент, вызывает API
- Examples: `agents/base.py:29-51`
- Pattern: Template Method — подклассы переопределяют `role` и `use_reasoner`, метод `process()` реализуется в каждом подклассе

**STEPS registry:**
- Purpose: Декларативный список порядка выполнения pipeline
- Examples: `orchestrator/pipeline.py:14-21`
- Pattern: List of tuples `(name, AgentClass, artifact_field)` — единственное место, где задаётся порядок

## Entry Points

**CLI:**
- Location: `main.py`
- Triggers: `python main.py "задача"` или `python main.py --dry-run "задача"`
- Responsibilities: Парсинг аргументов, вызов `run_pipeline` и `save_results`

**Programmatic:**
- Location: `orchestrator/pipeline.py:run_pipeline`
- Triggers: Прямой импорт и вызов из кода или тестов
- Responsibilities: Выполнение полного pipeline, возврат `ProjectState`

## Architectural Constraints

- **Threading:** Single-threaded, синхронные вызовы API — параллельного выполнения агентов нет
- **Global state:** Модуль-уровневый singleton `_client: OpenAI | None` в `agents/base.py:11` — один экземпляр клиента на весь процесс
- **Circular imports:** Не обнаружено — зависимости направлены строго вниз: `main.py → orchestrator → agents → state`
- **Context window:** Каждый агент получает полное содержимое предыдущих артефактов в промпте — при больших задачах возможен выход за лимит токенов
- **Tools not wired:** `tools/` реализованы с TOOL_DEFINITIONS, но ни один агент их не использует в `process()` — это заготовки для будущего tool use

## Anti-Patterns

### Dry-run логика в orchestrator

**What happens:** `run_pipeline` содержит `if dry_run` ветку прямо в основном цикле агентов (`orchestrator/pipeline.py:32-38`), и каждый агент внутри цикла заменяется заглушкой
**Why it's wrong:** Логика dry-run завязана на внутреннюю структуру артефактов — `getattr(state, artifact_field).__class__(content=...)` — хрупко при изменении Artifact
**Do this instead:** Создать `DryRunAgent` или обёртку вне основного цикла, либо дать `BaseAgent.run()` флаг `dry_run`

### use_heavy_model vs use_reasoner

**What happens:** В `agents/po.py:9` и `agents/architect.py:9` установлен атрибут `use_heavy_model = True`, но в `agents/base.py:33` проверяется `self.use_reasoner` — несовпадение имён
**Why it's wrong:** Флаг `HEAVY_MODEL=true` в `.env` никогда не активирует reasoner-модель для PO и Architect, хотя задумано именно это
**Do this instead:** Переименовать атрибуты в подклассах на `use_reasoner = True` (как в `BaseAgent`)

## Error Handling

**Strategy:** Нет явной обработки исключений — ошибки API пробрасываются наверх как необработанные исключения

**Patterns:**
- Нет try/except в `BaseAgent.run()` — OpenAI API ошибки (rate limit, network) упадут с traceback
- Нет retry-логики
- Нет валидации ответа агента (пустой `content` не проверяется)

## Cross-Cutting Concerns

**Logging:** `rich.Console` с `console.print` в `orchestrator/pipeline.py` — только визуальный вывод, без структурированных логов
**Validation:** Pydantic v2 валидирует структуру `ProjectState`, но не содержимое строковых артефактов
**Authentication:** API-ключ через `DEEPSEEK_API_KEY` env var, загружается через `python-dotenv` в `main.py`

---

*Architecture analysis: 2026-05-08*
