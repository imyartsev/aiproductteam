# AI Product Team

## What This Is

Автономная команда ИИ-агентов, которая принимает описание задачи и прогоняет её через полный цикл разработки: PO → Architect → Analyst → Dev → QA → DevOps. На выходе — реальные файлы проекта, которые можно запустить.

## Core Value

Дать задачу текстом — получить рабочий, запускаемый код: от пользовательских историй до Dockerfile.

## Requirements

### Validated

- ✓ Последовательный pipeline из 6 агентов (PO → Architect → Analyst → Dev → QA → DevOps) — существующий код
- ✓ Интеграция с DeepSeek API через OpenAI SDK — существующий код
- ✓ Shared state (ProjectState) передаётся через весь pipeline — существующий код
- ✓ CLI-интерфейс: `python main.py "задача"` — существующий код
- ✓ Dry-run режим для тестирования без API-вызовов — существующий код
- ✓ Markdown-артефакты сохраняются в `projects/<slug>/` — существующий код

### Active

- [ ] Dev-агент извлекает код из markdown (блоки `# path: ...`) и создаёт реальные файлы на диске
- [ ] QA-агент создаёт реальные тестовые файлы (не только отчёт в markdown)
- [ ] DevOps-агент создаёт Dockerfile и CI-конфиги как реальные файлы
- [ ] Исправлен баг: атрибут `use_heavy_model` в PO и Architect не совпадает с `use_reasoner` в BaseAgent
- [ ] Pipeline успешно выполняется с задачей "Создай FastAPI сервис для управления задачами"
- [ ] Сгенерированный FastAPI сервис запускается (`uvicorn`) и тесты проходят

### Out of Scope

- Параллельное выполнение агентов — усложнение без необходимости для текущей цели
- Интеграция `tools/` (file_ops, code_exec, git_ops) — заготовки, не нужны для demo
- Retry-логика и расширенная обработка ошибок API — за рамками demo
- Поддержка других языков кроме Python — нет такого требования

## Context

Проект уже реализован и запускаем. DeepSeek API-ключ настроен в `.env`.

Ключевая проблема: Dev-агент пишет код в блоках с маркером `# path: src/main.py` внутри markdown-файла `04_code.md`. Код там есть, но как реальные файлы не раскладывается — нужен парсер, который извлечёт блоки и создаст настоящие `.py`-файлы.

Аналогично для QA (тесты) и DevOps (Dockerfile, CI yml).

**Известные баги из карты кодовой базы:**
- `agents/po.py:9` и `agents/architect.py:9` устанавливают `use_heavy_model = True`, но `agents/base.py:33` проверяет `self.use_reasoner` — флаг `HEAVY_MODEL=true` никогда не активирует reasoner-модель

## Constraints

- **Стек:** Python, DeepSeek API (OpenAI-совместимый), Pydantic — менять не нужно
- **Вывод:** `projects/<slug>/` — реальная структура проекта, а не только markdown
- **Запускаемость:** Сгенерированный FastAPI ToDo сервис должен стартовать без ручных правок

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| DeepSeek вместо Claude для агентов | Дешевле и быстрее для серийных запросов pipeline | — Pending |
| Markdown с `# path:` маркерами как формат вывода Dev | Позволяет агенту писать свободно, потом парсим | — Pending |
| Один `ProjectState` на весь pipeline | Простота — каждый агент видит всё что было до него | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-08 после инициализации*
