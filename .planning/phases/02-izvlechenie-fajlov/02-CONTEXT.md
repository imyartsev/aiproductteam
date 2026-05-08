# Phase 2: Извлечение файлов - Context

**Gathered:** 2026-05-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Добавить в pipeline автоматическое извлечение реальных файлов проекта из markdown-вывода агентов Dev, QA и DevOps. Агенты уже выводят код с маркерами `# path: <путь>` — нужен парсер, который найдёт эти блоки и создаст файлы на диске в `projects/<slug>/`.

Затрагивает: `orchestrator/pipeline.py`, `orchestrator/extractor.py` (новый), `prompts/devops.md` (обновление маркеров).

</domain>

<decisions>
## Implementation Decisions

### Формат маркеров

- **D-01:** Единый маркер `# path: <путь>` используется для всех агентов (Dev, QA, DevOps) — без разделения по типу файла. Парсер один на всех.
- **D-02:** `prompts/dev.md` и `prompts/qa.md` уже содержат нужные маркеры — менять не надо.
- **D-03:** `prompts/devops.md` нужно обновить — добавить `# path:` маркеры для 5 файлов: `Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`, `.env.example`, `README.md`.
- **D-04:** Prose-разделы DevOps-агента (health check, инструкция по деплою) идут в `README.md` с маркером `# path: README.md`.

### Markdown-файлы

- **D-05:** Файлы `04_code.md`, `05_test_report.md`, `06_deploy_config.md` **остаются** рядом с реальными файлами — это сырой вывод LLM, полезен для дебага. Никаких переименований.

### Архитектура парсера

- **D-06:** Логика извлечения — в новом файле `orchestrator/extractor.py` (отдельный модуль с одной ответственностью).
- **D-07:** `save_results()` в `orchestrator/pipeline.py` вызывает функцию из extractor после сохранения markdown-файлов.
- **D-08:** Dry-run не извлекает файлы (заглушки `"[dry-run] ... output"` не содержат маркеров) — это корректное поведение, не баг.

### Claude's Discretion

- Сигнатура функции экстрактора: `extract_files(content: str, base_dir: Path) -> list[Path]`
- Парсинг: regex по code-блокам ` ``` ` с `# path:` в первой строке блока
- Unit-тесты для `extractor.py` — написать в `tests/`
- Вложенные пути (например `.github/workflows/ci.yml`) создаём через `pathlib.mkdir(parents=True, exist_ok=True)`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Pipeline и точки интеграции
- `orchestrator/pipeline.py` — `save_results()` (строки 52-72): сюда добавляем вызов extractor; `run_pipeline()` (строки 24-49): структура цикла агентов
- `orchestrator/state.py` — `ProjectState` и все артефакты: `code_artifact`, `test_report`, `deploy_config` — их `.content` парсит extractor

### Промпты с маркерами (образец и обновление)
- `prompts/dev.md` — **уже содержит** `# path:` маркеры → образец для понимания формата
- `prompts/qa.md` — **уже содержит** `# path: tests/test_<module>.py` → не менять
- `prompts/devops.md` — **нужно обновить**: добавить `# path:` для Dockerfile, docker-compose.yml, .github/workflows/ci.yml, .env.example, README.md

### Требования
- `.planning/REQUIREMENTS.md` — CODE-01, CODE-02, CODE-03, DEPLOY-01, DEPLOY-02: критерии приёмки этапа

### Архитектура
- `.planning/codebase/ARCHITECTURE.md` — описание pipeline, data flow, паттерн `save_results()`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `orchestrator/pipeline.py:save_results()` — уже делает `project_dir.mkdir(parents=True, exist_ok=True)` и `write_text(content, encoding="utf-8")` → те же операции нужны для извлечённых файлов
- `pathlib.Path` — уже используется в `pipeline.py` для всех файловых операций, переиспользовать

### Established Patterns
- Маркер формат `# path: <путь>` уже определён в dev.md и qa.md — нельзя менять, парсер должен соответствовать
- Сохранение через `(project_dir / filename).write_text(content, encoding="utf-8")` — паттерн из `save_results()`, использовать везде

### Integration Points
- `save_results(state, output_dir)` в `pipeline.py:52` — единственная точка входа. После строки 69 (сохранение markdown) вызвать `extract_files()` для `code_artifact.content`, `test_report.content`, `deploy_config.content`
- Новый файл `orchestrator/extractor.py` должен импортироваться в `pipeline.py`

</code_context>

<specifics>
## Specific Ideas

- DevOps README.md: агент пишет health check endpoint, ключевые метрики и инструкцию по деплою — всё в одном README.md с маркером `# path: README.md`
- Парсер должен обрабатывать code-блоки любого языка (```python, ```yaml, ```dockerfile, ``` — без указания языка) — маркер `# path:` в первой строке блока

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 2-Извлечение файлов*
*Context gathered: 2026-05-08*
