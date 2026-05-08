---
phase: 1
plan: 1
subsystem: agents/tests
tags: [bugfix, tests, deepseek]
dependency_graph:
  requires: []
  provides: [use_reasoner-fixed, test-suite-openai]
  affects: [agents/po.py, agents/architect.py, tests/test_agents.py]
tech_stack:
  added: []
  patterns: [OpenAI SDK mock pattern, env-var behavioral testing]
key_files:
  modified:
    - agents/po.py
    - agents/architect.py
    - tests/test_agents.py
decisions:
  - "D-01/D-02: use_heavy_model → use_reasoner в po.py и architect.py"
  - "D-03: env var HEAVY_MODEL оставлен без изменений"
  - "D-04: тесты мокируют OpenAI SDK (chat.completions.create), а не Anthropic"
  - "D-05: добавлены 4 поведенческих теста флага HEAVY_MODEL"
metrics:
  duration: "1m 13s"
  completed_date: "2026-05-08"
  tasks_completed: 3
  files_changed: 3
---

# Phase 1 Plan 1: Исправление бага use_heavy_model → use_reasoner Summary

**Одной строкой:** Переименован атрибут `use_heavy_model` → `use_reasoner` в POAgent и ArchitectAgent; тесты переписаны с Anthropic SDK на OpenAI SDK с добавлением 4 поведенческих тестов флага HEAVY_MODEL.

## Что было сделано

### Task 1 — Переименование атрибута (коммит 88401ca)

В `agents/po.py:9` и `agents/architect.py:9` строка `use_heavy_model = True` переименована в `use_reasoner = True`. Теперь атрибут совпадает с тем, что читает `BaseAgent.__init__` на строке 38 (`self.use_reasoner`), и флаг `HEAVY_MODEL=true` корректно активирует `deepseek-reasoner` для обоих агентов.

### Task 2 — Починка существующих тестов (коммит 3c83806)

В `tests/test_agents.py` выполнено:
- `os.environ.setdefault("ANTHROPIC_API_KEY", ...)` → `os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")`
- `_make_mock_response`: структура ответа приведена к OpenAI SDK (`response.choices[0].message.content = text`)
- В `test_base_agent_run` и `test_po_agent_populates_task_spec`: `mock_client.messages.create` → `mock_client.chat.completions.create`
- Тест `test_prompt_cache_control_set` (проверял Anthropic-специфичный `cache_control: ephemeral`) удалён и заменён на `test_base_agent_run_calls_completions_create`, который проверяет правильный вызов OpenAI SDK и наличие двух сообщений (system + user)

### Task 3 — Добавление поведенческих тестов HEAVY_MODEL (коммит 3c83806)

Добавлены 4 теста:
- `test_po_uses_reasoner_when_heavy_model_true` — POAgent с `HEAVY_MODEL=true` → `agent._model == "deepseek-reasoner"`
- `test_po_uses_chat_without_heavy_model` — POAgent без флага → `agent._model == "deepseek-chat"`
- `test_architect_uses_reasoner_when_heavy_model_true` — ArchitectAgent с `HEAVY_MODEL=true` → `deepseek-reasoner`
- `test_architect_uses_chat_without_heavy_model` — ArchitectAgent без флага → `deepseek-chat`

Все тесты используют `@patch("agents.base._load_prompt")` для изоляции от файловой системы и `try/finally` для очистки env var (требование T-1-02 из threat model).

## Результаты тестирования

```
tests/test_agents.py::test_base_agent_run                              PASSED
tests/test_agents.py::test_po_agent_populates_task_spec                PASSED
tests/test_agents.py::test_base_agent_run_calls_completions_create     PASSED
tests/test_agents.py::test_po_uses_reasoner_when_heavy_model_true      PASSED
tests/test_agents.py::test_po_uses_chat_without_heavy_model            PASSED
tests/test_agents.py::test_architect_uses_reasoner_when_heavy_model_true PASSED
tests/test_agents.py::test_architect_uses_chat_without_heavy_model     PASSED

tests/test_pipeline.py::test_dry_run_pipeline_returns_state            PASSED
tests/test_pipeline.py::test_dry_run_all_artifacts_populated           PASSED
tests/test_pipeline.py::test_save_results_creates_files                PASSED

10 passed in 1.40s
```

## Deviations from Plan

None — план выполнен точно как написан. Задачи 2 и 3 реализованы в одном коммите, поскольку оба изменения вносятся в один файл `tests/test_agents.py` и логически неразрывны.

## Known Stubs

Нет. Изменения касаются только переименования атрибута и тестов; никаких заглушек не внесено.

## Threat Flags

Нет новых поверхностей атаки. Threat register плана (T-1-01, T-1-02) выполнен: env var используется только для выбора модели, тесты с `HEAVY_MODEL=true` имеют `try/finally`.

## Self-Check: PASSED

- agents/po.py — FOUND, строка 9: `use_reasoner = True`
- agents/architect.py — FOUND, строка 9: `use_reasoner = True`
- tests/test_agents.py — FOUND, 7 тестов
- Коммит 88401ca — FOUND
- Коммит 3c83806 — FOUND
- pytest: 10 passed, 0 failed
