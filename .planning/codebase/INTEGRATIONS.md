# External Integrations

**Analysis Date:** 2026-05-08

## APIs & External Services

**LLM Provider:**
- DeepSeek API — генерация текста всеми агентами pipeline
  - SDK/Client: `openai` 1.0+ (OpenAI-compatible клиент с переопределённым `base_url`)
  - Base URL: `https://api.deepseek.com`
  - Auth: env var `DEEPSEEK_API_KEY`
  - Клиент инициализируется как синглтон в `agents/base.py` (`_get_client()`)
  - Используемые модели:
    - `deepseek-chat` — основная (по умолчанию для всех агентов)
    - `deepseek-reasoner` — тяжёлая модель, активируется при `HEAVY_MODEL=true` для агентов с `use_heavy_model = True` (PO, Architect)
  - Параметры вызова: `max_tokens=8192`, messages в формате `[system, user]`
  - Формат ответа: `response.choices[0].message.content` (OpenAI chat completions format)

**Примечание:** В тестах `test_agents.py` встречаются ссылки на `mock_client.messages.create` (Anthropic-стиль) — это артефакт тестов, реальный код использует `client.chat.completions.create` (OpenAI-стиль).

## Data Storage

**Databases:**
- Не используются — состояние хранится только в памяти как `ProjectState` (Pydantic модель)

**File Storage:**
- Локальная файловая система
  - Артефакты сохраняются в `projects/<slug>/` через `orchestrator/pipeline.py` → `save_results()`
  - 6 файлов на задачу: `01_task_spec.md` … `06_deploy_config.md`
  - Путь настраивается через `PROJECTS_DIR` или флаг `--output`

**Caching:**
- Отсутствует (нет Redis, memcached и т.п.)

## Authentication & Identity

**Auth Provider:**
- Только API-ключ DeepSeek (`DEEPSEEK_API_KEY`)
- Пользовательской аутентификации нет — CLI-инструмент без multi-user контекста

## Monitoring & Observability

**Error Tracking:**
- Отсутствует (нет Sentry, DataDog и т.п.)

**Logs:**
- `rich.console.Console` для форматированного вывода в терминал (`orchestrator/pipeline.py`)
- Нет структурированного логирования в файл

## CI/CD & Deployment

**Hosting:**
- Нет — локальный CLI-инструмент

**CI Pipeline:**
- Не обнаружен (нет `.github/workflows/`, нет `Makefile` с CI-таргетами)

## Environment Configuration

**Required env vars:**
- `DEEPSEEK_API_KEY` — обязателен для реальных вызовов API
- `HEAVY_MODEL` — опционально, `true`/`false` (по умолчанию `false`)
- `PROJECTS_DIR` — опционально, путь для сохранения результатов (по умолчанию `./projects`)

**Secrets location:**
- `.env` файл в корне проекта (в `.gitignore`)
- `.env.example` — шаблон без секретов, зафиксирован в репозитории

## Webhooks & Callbacks

**Incoming:**
- Нет (не web-сервис)

**Outgoing:**
- Нет (только синхронные HTTP-вызовы к DeepSeek API)

## Инструменты (tools/) — потенциальные интеграции

Модули в `tools/` содержат определения инструментов (TOOL_DEFINITIONS) для возможного использования через tool use API, но текущие агенты (`BaseAgent.run()`) их не вызывают:

- `tools/file_ops.py` — `read_file`, `write_file`, `list_files` — работа с локальной ФС
- `tools/code_exec.py` — `run_python` — выполнение Python кода через `subprocess`
- `tools/git_ops.py` — `git_status`, `git_commit` — работа с Git через `subprocess`

Эти инструменты подготовлены для будущей интеграции с tool use функциональностью DeepSeek/OpenAI API, но пока не подключены к агентам.

---

*Integration audit: 2026-05-08*
