# Codebase Structure

**Analysis Date:** 2026-05-08

## Directory Layout

```
ai-product-team/
├── main.py                   # CLI-точка входа (argparse + вызов pipeline)
├── pyproject.toml            # Метаданные пакета, зависимости, pytest-конфиг
├── CLAUDE.md                 # Инструкции проекта для Claude
├── README.md                 # Документация проекта
├── .env.example              # Шаблон переменных окружения
│
├── agents/                   # Реализация агентов продуктовой команды
│   ├── __init__.py           # Реэкспорт всех AgentClass
│   ├── base.py               # BaseAgent: DeepSeek API клиент, загрузка промптов
│   ├── po.py                 # POAgent: raw_task → task_spec
│   ├── architect.py          # ArchitectAgent: task_spec → arch_decision
│   ├── analyst.py            # AnalystAgent: task_spec + arch_decision → tech_spec
│   ├── dev.py                # DevAgent: tech_spec → code_artifact
│   ├── qa.py                 # QAAgent: tech_spec + code_artifact → test_report
│   └── devops.py             # DevOpsAgent: arch + code + test → deploy_config
│
├── orchestrator/             # Управление pipeline и общее состояние
│   ├── __init__.py
│   ├── pipeline.py           # run_pipeline(), save_results(), STEPS registry
│   └── state.py              # Pydantic-модели: ProjectState + 6 Artifact-подклассов
│
├── prompts/                  # System prompts агентов (Markdown)
│   ├── po.md
│   ├── architect.md
│   ├── analyst.md
│   ├── dev.md
│   ├── qa.md
│   └── devops.md
│
├── tools/                    # Инструменты для агентов (заготовки, не интегрированы)
│   ├── __init__.py
│   ├── file_ops.py           # read_file / write_file / list_files + TOOL_DEFINITIONS
│   ├── code_exec.py          # run_python() в subprocess + TOOL_DEFINITIONS
│   └── git_ops.py            # git_status / git_commit + TOOL_DEFINITIONS
│
├── tests/                    # Тесты (pytest)
│   ├── __init__.py
│   ├── test_pipeline.py      # Интеграционные тесты pipeline в dry-run режиме
│   └── test_agents.py        # Тесты агентов
│
├── projects/                 # Вывод: результаты работы pipeline (gitignored)
│   ├── .gitkeep
│   └── <slug>/               # Папка задачи (первые 40 символов задачи)
│       ├── 01_task_spec.md
│       ├── 02_arch_decision.md
│       ├── 03_tech_spec.md
│       ├── 04_code.md
│       ├── 05_test_report.md
│       └── 06_deploy_config.md
│
└── памятки/                  # Техническая документация проекта (gitignored)
    └── .gitkeep
```

## Directory Purposes

**`agents/`:**
- Purpose: По одному файлу на каждую роль продуктовой команды
- Contains: `BaseAgent` и 6 конкретных агентов с методом `process(state) -> state`
- Key files: `agents/base.py` — DeepSeek клиент, `agents/__init__.py` — реэкспорт

**`orchestrator/`:**
- Purpose: Ядро системы — порядок выполнения и модели данных
- Contains: `pipeline.py` с функциями `run_pipeline`/`save_results` и `state.py` с Pydantic-моделями
- Key files: `orchestrator/state.py` — единственный источник схемы данных

**`prompts/`:**
- Purpose: System prompts хранятся отдельно от кода агентов — легко редактировать без правки Python
- Contains: Один `.md`-файл на каждого агента, имя файла совпадает с `agent.role`
- Key files: Загружаются динамически через `agents/base.py:_load_prompt(name)`

**`tools/`:**
- Purpose: Инструменты для потенциальной интеграции tool use в агентов
- Contains: Python-функции + JSON-схемы `TOOL_DEFINITIONS` для DeepSeek/OpenAI tool use API
- Key files: Не интегрированы в текущую реализацию агентов

**`tests/`:**
- Purpose: Автоматические тесты на pytest
- Contains: Тесты pipeline в dry-run режиме, тесты агентов
- Key files: `tests/test_pipeline.py` — самые важные интеграционные тесты

**`projects/`:**
- Purpose: Файловый вывод pipeline — каждая задача в отдельной папке
- Contains: Markdown-файлы артефактов с нумерованными именами
- Generated: Yes (содержимое генерируется агентами)
- Committed: No (в `.gitignore`)

**`памятки/`:**
- Purpose: Ручная техническая документация разработчиков
- Generated: No
- Committed: No (в `.gitignore`)

## Key File Locations

**Entry Points:**
- `main.py`: CLI — `python main.py "задача"` или `python main.py --dry-run "задача"`
- `orchestrator/pipeline.py:run_pipeline`: Programmatic entry point

**Configuration:**
- `pyproject.toml`: Зависимости проекта, Python >=3.11, pytest asyncio_mode=auto
- `.env.example`: Шаблон с `DEEPSEEK_API_KEY`, `HEAVY_MODEL`, `PROJECTS_DIR`
- `CLAUDE.md`: Инструкции по разработке для Claude

**Core Logic:**
- `orchestrator/pipeline.py`: STEPS registry и управление выполнением
- `orchestrator/state.py`: Все модели данных
- `agents/base.py`: Общая логика агентов и DeepSeek клиент

**Testing:**
- `tests/test_pipeline.py`: Интеграционные тесты dry-run

## Naming Conventions

**Files:**
- Агенты: `<role>.py` в нижнем регистре (совпадает с `agent.role` и именем prompt-файла)
- Промпты: `<role>.md` — строгое соответствие `role`-атрибуту в Python-классе
- Артефакты вывода: `NN_<name>.md` с двузначным префиксом для сортировки

**Directories:**
- Папка задачи в `projects/`: slug из первых 40 символов задачи, спецсимволы → `_`

**Classes:**
- Агенты: `<Role>Agent` (PascalCase, суффикс Agent)
- Артефакты: имя роли без суффикса (TaskSpec, ArchDecision, TechSpec и т.д.)

**Functions:**
- snake_case во всём коде
- Приватные функции в `agents/base.py`: `_get_client()`, `_load_prompt()` (с `_`)

## Where to Add New Code

**Новый агент:**
1. Создать `agents/<role>.py`, унаследовать от `BaseAgent`, реализовать `process(state) -> state`
2. Добавить Pydantic Artifact-модель в `orchestrator/state.py` и поле в `ProjectState`
3. Написать system prompt в `prompts/<role>.md`
4. Добавить tuple `("<Name>", <RoleAgent>, "<artifact_field>")` в `STEPS` в `orchestrator/pipeline.py:14`
5. Добавить импорт в `agents/__init__.py`

**Новый инструмент:**
- Реализация: `tools/<name>.py` с функциями и `TOOL_DEFINITIONS`
- Интеграция: передать `TOOL_DEFINITIONS` в `BaseAgent` и добавить вызов `client.chat.completions.create(tools=...)`

**Новая конфигурация:**
- Env vars: Добавить в `.env.example` с комментарием, читать через `os.environ.get()` в `agents/base.py`

**Утилиты:**
- Общие хелперы: `tools/` (если связаны с внешними операциями) или новый модуль на уровне корня

## Special Directories

**`projects/`:**
- Purpose: Файловый артефакт каждого запуска pipeline
- Generated: Yes — создаётся `save_results()` при каждом запуске
- Committed: No (`.gitignore` исключает содержимое, кроме `.gitkeep`)

**`памятки/`:**
- Purpose: Техническая документация разработчиков
- Generated: No
- Committed: No

**`ai_product_team.egg-info/`:**
- Purpose: Метаданные setuptools при `pip install -e .`
- Generated: Yes
- Committed: No

---

*Structure analysis: 2026-05-08*
