# Phase 2: Извлечение файлов - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-08
**Phase:** 2-Извлечение файлов
**Areas discussed:** DevOps-маркеры, Markdown-файлы, Где живёт парсер

---

## DevOps-маркеры

### Формат маркера

| Вариант | Описание | Выбран |
|---------|----------|--------|
| `# path: Dockerfile` | Тот же формат что у Dev и QA — единый парсер для всех агентов | ✓ |
| Отдельные секции (без маркеров) | `## Dockerfile`, `## docker-compose.yml` — парсер по заголовкам | |

**Выбор пользователя:** `# path:` маркер, единый для всех агентов

---

### Какие файлы DevOps создаёт как реальные

| Вариант | Описание | Выбран |
|---------|----------|--------|
| Dockerfile + CI-конфиг | Минимум по требованиям DEPLOY-01 + DEPLOY-02 | |
| Все 4 файла | Dockerfile, docker-compose.yml, .github/workflows/ci.yml, .env.example | ✓ |
| Только Dockerfile | Минимальное demo, DEPLOY-02 не закрыт | |

**Выбор пользователя:** Все 4 файла

---

### Prose-разделы DevOps (health check, инструкция по деплою)

| Вариант | Описание | Выбран |
|---------|----------|--------|
| `06_deploy_config.md` | Остаётся в markdown-артефакте, отдельно от реальных файлов | |
| `README.md` в папке проекта | DevOps выводит README.md через `# path: README.md` | ✓ |

**Выбор пользователя:** README.md в папке проекта — итого 5 реальных файлов от DevOps

---

## Markdown-файлы

| Вариант | Описание | Выбран |
|---------|----------|--------|
| Оставить как есть | Сырой LLM-вывод рядом с реальными файлами | ✓ |
| Убрать | Только реальные файлы, папка чище | |
| Переименовать в *.raw.md | Явное разделение raw/code | |

**Выбор пользователя:** Оставить — markdown-файлы (04_code.md, 05_test_report.md, 06_deploy_config.md) остаются рядом с реальными файлами

---

## Где живёт парсер

| Вариант | Описание | Выбран |
|---------|----------|--------|
| `orchestrator/extractor.py` | Отдельный модуль, чистая ответственность, легко тестируется | ✓ |
| Расширить `save_results()` | Всё в одном месте, функция становится больше | |

**Выбор пользователя:** `orchestrator/extractor.py`

---

### Dry-run поведение

| Вариант | Описание | Выбран |
|---------|----------|--------|
| 0 файлов — это нормально | Dry-run проверяет структуру pipeline, не извлечение | ✓ |
| Добавить маркеры в dry-run заглушки | Визуальная проверка что extraction работает без API | |

**Выбор пользователя:** 0 файлов — нормально, тестирование extractor через pytest

---

## Claude's Discretion

- Сигнатура функции: `extract_files(content: str, base_dir: Path) -> list[Path]`
- Технология парсинга: regex по code-блокам с `# path:` в первой строке
- Unit-тесты для `extractor.py` в `tests/`
- Вложенные пути через `pathlib.mkdir(parents=True, exist_ok=True)`

## Deferred Ideas

None — discussion stayed within phase scope
