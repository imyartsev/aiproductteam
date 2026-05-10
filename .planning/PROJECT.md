# AI Product Team

## What This Is

Автономная команда ИИ-агентов, которая принимает описание задачи и прогоняет её через полный цикл разработки: PO → Architect → Analyst → Dev → QA → DevOps. На выходе — реальные файлы проекта (Python-код, тесты, Dockerfile, CI-конфиги), которые можно запустить без ручных правок.

## Core Value

Дать задачу текстом — получить рабочий, запускаемый код: от пользовательских историй до Dockerfile.

## Requirements

### Validated

- ✓ Последовательный pipeline из 6 агентов (PO → Architect → Analyst → Dev → QA → DevOps) — v1.0
- ✓ Интеграция с DeepSeek API через OpenAI SDK — v1.0
- ✓ Shared state (ProjectState) передаётся через весь pipeline — v1.0
- ✓ CLI-интерфейс: `python main.py "задача"` — v1.0
- ✓ Dry-run режим для тестирования без API-вызовов — v1.0
- ✓ Markdown-артефакты сохраняются в `projects/<slug>/` — v1.0
- ✓ Исправлен баг: `use_heavy_model` → `use_reasoner` в PO и Architect — v1.0
- ✓ Парсер `# path:` маркеров — Dev/QA/DevOps создают реальные файлы на диске — v1.0
- ✓ Pipeline успешно выполняется с задачей "Создай FastAPI сервис для управления задачами" — v1.0
- ✓ Сгенерированный FastAPI сервис запускается и тесты проходят (38/38, Docker) — v1.0

### Active

*(нет активных требований — v1.0 milestone закрыт)*

### Out of Scope

- Параллельное выполнение агентов — усложнение без необходимости для текущей цели
- Интеграция `tools/` (file_ops, code_exec, git_ops) — заготовки, не нужны для demo
- Retry-логика и расширенная обработка ошибок API — за рамками demo
- Поддержка других языков кроме Python — нет такого требования
- Path traversal validation для `# path:` маркеров — принято как REL-04 в backlog

## Context

**Shipped v1.0:** 2026-05-08. Pipeline полностью работает — от текстовой задачи до запускаемого FastAPI проекта.

Стек: Python 3.13, DeepSeek API (OpenAI-совместимый через `base_url=https://api.deepseek.com`), Pydantic.

Запуск: `PYTHONIOENCODING=utf-8 python main.py "задача"`.
Верификация: `python verify.py projects/<slug>` (требует запущенный Docker).

Итог верификации v1.0: 38 тестов PASS, FastAPI сервис поднимается в Docker, `/health` → 200.

**Примечание (2026-05-10):** После завершения v1.0 концепция проекта была переосмыслена. GSD-фреймворк решает задачу автоматизации разработки более полно и детально. v2 не планируется.

## Constraints

- **Стек:** Python, DeepSeek API (OpenAI-совместимый), Pydantic — менять не нужно
- **Вывод:** `projects/<slug>/` — реальная структура проекта, а не только markdown
- **Запускаемость:** Сгенерированный FastAPI ToDo сервис должен стартовать без ручных правок
- **Docker образ:** `python:3.10-slim` — единственный проверенный базовый образ

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| DeepSeek вместо Claude для агентов | Дешевле и быстрее для серийных запросов pipeline | ✓ Работает, API-совместимость полная |
| Markdown с `# path:` маркерами как формат вывода Dev | Позволяет агенту писать свободно, потом парсим | ✓ Работает надёжно через regex + re.DOTALL |
| Один `ProjectState` на весь pipeline | Простота — каждый агент видит всё что было до него | ✓ Достаточно для sequential pipeline |
| `use_reasoner` вместо `use_heavy_model` | Совпадение с полем в BaseAgent | ✓ Баг устранён, HEAVY_MODEL=true работает |
| `python:3.10-slim` как базовый Docker образ | `python:3.12-slim` не был доступен в локальном кэше | ✓ Стабильно |
| `python -m pytest` вместо `pytest` | Гарантия PATH в Docker-окружении | ✓ 38 тестов PASS |
| `shutil.rmtree` перед записью в `pipeline.py` | Предотвращение накопления файлов между прогонами | ✓ Чистые прогоны |

## Evolution

**After v1.0 (2026-05-10):** Проект закрыт как концепция. Код и артефакты сохранены как исторический пример. GSD-фреймворк признан более подходящим инструментом для задач автоматизации разработки.

---
*Last updated: 2026-05-10 после завершения v1.0 milestone*
