# Technology Stack

**Analysis Date:** 2026-05-08

## Languages

**Primary:**
- Python 3.11+ — весь codebase (агенты, оркестратор, инструменты, тесты)

## Runtime

**Environment:**
- CPython 3.11+

**Package Manager:**
- pip + setuptools 68+
- Lockfile: отсутствует (только `pyproject.toml`)

## Frameworks

**Core:**
- Нет web-фреймворка — CLI-приложение, запускается через `main.py`

**Валидация данных:**
- `pydantic` 2.0+ — Shared State (`orchestrator/state.py`): `ProjectState`, `TaskSpec`, `ArchDecision`, `TechSpec`, `CodeArtifact`, `TestReport`, `DeployConfig`

**CLI-вывод:**
- `rich` 13.0+ — форматированный вывод в терминал (`orchestrator/pipeline.py`): `Console`, `Panel`

**Конфигурация:**
- `python-dotenv` 1.0+ — загрузка `.env` файла в `main.py`

**Testing:**
- `pytest` 8.0+ — запуск тестов
- `pytest-asyncio` 0.23+ — поддержка async тестов (asyncio_mode = "auto")

## Key Dependencies

**Critical:**
- `openai` 1.0+ — HTTP-клиент для DeepSeek API (используется через `OpenAI(base_url="https://api.deepseek.com")` в `agents/base.py`)
- `pydantic` 2.0+ — типизация и валидация всего pipeline state

**Infrastructure:**
- `setuptools` 68+ — сборка пакета, editable install (`pip install -e .`)

## Configuration

**Environment:**
- Загрузка через `python-dotenv` в `main.py` (`load_dotenv()`)
- `.env.example` описывает требуемые переменные
- Ключевые переменные:
  - `DEEPSEEK_API_KEY` — API ключ DeepSeek (обязателен для реальных вызовов)
  - `HEAVY_MODEL` — `true`/`false`, включает `deepseek-reasoner` для PO и Architect агентов (по умолчанию `false`)
  - `PROJECTS_DIR` — папка сохранения артефактов (по умолчанию `./projects`)

**Build:**
- `pyproject.toml` — единственный файл конфигурации проекта
- `[tool.setuptools.packages.find]` включает: `agents*`, `orchestrator*`, `tools*`
- `[tool.pytest.ini_options]`: `asyncio_mode = "auto"`

## Platform Requirements

**Development:**
- Python 3.11+
- `pip install -e .` для установки в editable mode
- `.env` файл с `DEEPSEEK_API_KEY`
- Режим `--dry-run` доступен без API-ключа

**Production:**
- Нет специальных требований к платформе: чистый Python CLI
- Результаты сохраняются в `projects/<slug>/` (6 Markdown-файлов на задачу)

---

*Stack analysis: 2026-05-08*
