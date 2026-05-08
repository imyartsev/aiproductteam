# Phase 3: Демо-прогон - Context

**Gathered:** 2026-05-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Запустить полный pipeline с задачей "Создай FastAPI сервис для управления задачами" и верифицировать запускаемость результата через Docker. Включает: доработку промптов Dev и QA для надёжной генерации, написание скрипта проверки `verify.py`, и успешный прогон pipeline конец-в-конец.

Затрагивает: `prompts/dev.md`, `prompts/qa.md`, новый файл `verify.py` в корне проекта.

</domain>

<decisions>
## Implementation Decisions

### Промпты агентов

- **D-01:** Промпт Dev-агента (`prompts/dev.md`) улучшить. Обязательные дополнения: (1) всегда генерировать `# path: requirements.txt` с полным списком зависимостей, (2) всегда генерировать `# path: README.md` с инструкцией запуска через Docker (`docker build` + `docker run`). Стек (FastAPI + ORM + БД) выбирает Architect-агент в `arch_decision` — Dev читает `arch_decision` и строго следует выбранному стеку.
- **D-02:** Промпт QA-агента (`prompts/qa.md`) улучшить. Тесты должны использовать `pytest` + FastAPI `TestClient` (не httpx с живым сервером, не requests). TestClient не требует запущенного сервера и работает внутри Docker-контейнера без дополнительных настроек.

### Скрипт проверки

- **D-03:** Создать `verify.py` в корне проекта (рядом с `main.py`). Интерфейс: `python verify.py projects/<slug>`. Принимает путь к папке сгенерированного проекта.
- **D-04:** Скрипт выполняет четыре шага последовательно:
  1. `docker build -t <slug> <project_dir>` — собрать образ
  2. `docker run -d -p 8000:8000 <slug>` — запустить сервер в фоне, подождать старта
  3. `GET http://localhost:8000/health` через `requests` — проверить что сервер отвечает
  4. `docker run <slug> pytest` — запустить тесты внутри Docker, проверить exit code 0
  Выводит `PASS` или `FAIL` с подробным выводом каждого шага.

### Стратегия при неудаче

- **D-05:** Если `verify.py` завершается с ошибкой — демо считается провалившимся, этап не завершён. Следующий шаг: дорабатывать промпты агентов до успешного прогона. Ручные правки сгенерированного кода не допускаются — это нарушает критерий "без ручных правок".

### Claude's Discretion

- Таймаут ожидания старта Docker-контейнера (рекомендуется 10–15 сек с retry-loop)
- Имя Docker-образа (можно использовать slug папки проекта)
- Реализация verify.py (subprocess + time.sleep vs docker SDK)
- Порт uvicorn (8000 по умолчанию — стандарт FastAPI)
- Очистка Docker-ресурсов после проверки (docker stop + docker rm)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Промпты агентов (основные файлы изменений)
- `prompts/dev.md` — промпт Dev-агента, требует доработки (D-01): добавить requirements.txt и README.md
- `prompts/qa.md` — промпт QA-агента, требует доработки (D-02): уточнить TestClient и pytest

### DevOps-артефакты (уже генерируются)
- `prompts/devops.md` — уже содержит `# path: Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml` — не трогать

### Pipeline и интеграция
- `orchestrator/pipeline.py` — точки вызова агентов и `save_results()`; extractor уже интегрирован (Phase 2)
- `orchestrator/state.py` — ProjectState; `code_artifact`, `test_report`, `deploy_config` — артефакты для проверки
- `orchestrator/extractor.py` — парсер `# path:` маркеров (реализован в Phase 2)

### Требования и критерии
- `.planning/REQUIREMENTS.md` — DEMO-01, DEMO-02, DEMO-03, DEMO-04: критерии приёмки этапа
- `.planning/ROADMAP.md` — Phase 3 Success Criteria (9 пунктов)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `orchestrator/extractor.py:extract_files()` — уже парсит `# path:` маркеры и создаёт файлы через `pathlib`. После Phase 2 pipeline автоматически раскладывает реальные файлы Dev, QA, DevOps.
- `orchestrator/pipeline.py:save_results()` — уже вызывает `extract_files()` для `code_artifact`, `test_report`, `deploy_config`. Реальные файлы уже появляются в `projects/<slug>/`.

### Established Patterns
- `# path: <файл>` маркер — единственный формат, по которому extractor находит файлы. Dev и QA уже используют его. DevOps уже генерирует Dockerfile и docker-compose.yml через этот маркер.
- `projects/<slug>/` — стандартная папка вывода pipeline. Верифицируем содержимое именно этой папки.

### Integration Points
- `verify.py` независим от pipeline — отдельный скрипт, не меняет существующий код
- Изменения только в `prompts/dev.md` и `prompts/qa.md` — не трогаем Python-код агентов

</code_context>

<specifics>
## Specific Ideas

- Скрипт проверки должен выводить итог для каждого шага: `[OK] docker build` / `[FAIL] docker build: <error>` — чтобы сразу было видно где сломалось
- Тест `/health` — достаточно что сервер отвечает 200, содержимое тела не важно. Если FastAPI не генерирует `/health` — агенты должны его добавить (зафиксировать в промпте Dev)
- Тест pytest внутри Docker подразумевает что Dockerfile включает тестовые зависимости (pytest, httpx/starlette) — DevOps-агент это уже делает через `requirements.txt`

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-demo-progon*
*Context gathered: 2026-05-08*
