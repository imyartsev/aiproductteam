# Phase 1: Исправление бага - Context

**Gathered:** 2026-05-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Переименовать атрибут `use_heavy_model` → `use_reasoner` в `agents/po.py` и `agents/architect.py`, чтобы флаг `HEAVY_MODEL=true` корректно активировал модель `deepseek-reasoner` для PO и Architect.

Попутно: исправить существующие тесты (`tests/test_agents.py`), которые мокают Anthropic SDK вместо OpenAI SDK, и добавить поведенческий тест на исправленный баг.

</domain>

<decisions>
## Implementation Decisions

### Исправление бага
- **D-01:** В `agents/po.py:9` заменить `use_heavy_model = True` на `use_reasoner = True`
- **D-02:** В `agents/architect.py:9` заменить `use_heavy_model = True` на `use_reasoner = True`
- **D-03:** Env var остаётся `HEAVY_MODEL` — менять не нужно, ROADMAP зафиксировал именно это имя

### Тесты
- **D-04:** Исправить `tests/test_agents.py`: заменить мок Anthropic SDK (`messages.create`, `cache_control: ephemeral`) на мок OpenAI SDK (`chat.completions.create`) — текущие тесты падают из-за несовпадения API
- **D-05:** Добавить поведенческий тест: при `HEAVY_MODEL=true` PO и Architect инициализируются с `deepseek-reasoner`, без флага — с `deepseek-chat`

### Claude's Discretion
- Имена тестовых функций и структура файла — на усмотрение планировщика, главное покрытие поведения

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Код с багом
- `agents/po.py` — строка 9: `use_heavy_model = True` (нужно переименовать)
- `agents/architect.py` — строка 9: `use_heavy_model = True` (нужно переименовать)
- `agents/base.py` — строки 33-38: определяет `use_reasoner` и логику выбора модели по `HEAVY_MODEL` env var

### Тесты
- `tests/test_agents.py` — текущие тесты (сломаны: мокают Anthropic SDK вместо OpenAI SDK)
- `tests/test_pipeline.py` — dry-run тесты pipeline (не сломаны, не трогаем)

### Контекст архитектуры
- `.planning/codebase/ARCHITECTURE.md` — описание паттерна BaseAgent и anti-patterns (включая именно этот баг)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `agents/base.py:_get_client()` — singleton OpenAI клиент, именно его нужно мокать в тестах (через `@patch("agents.base._get_client")`)
- `agents/base.py:CHAT_MODEL`, `REASONER_MODEL` — константы моделей (`"deepseek-chat"`, `"deepseek-reasoner"`)

### Established Patterns
- Паттерн мока в тестах: `@patch("agents.base._get_client")` уже используется — нужно исправить что мокается внутри (`mock_client.chat.completions.create`, а не `mock_client.messages.create`)
- Ответ OpenAI SDK: `response.choices[0].message.content` (не `response.content[0].text`)

### Integration Points
- `agents/base.py:__init__`: читает `os.environ.get("HEAVY_MODEL")` и `self.use_reasoner` — именно здесь происходит выбор модели, здесь и проверяем поведение в тесте

</code_context>

<specifics>
## Specific Ideas

- Тест на поведение: создать агент с `HEAVY_MODEL=true` в окружении, проверить что `agent._model == "deepseek-reasoner"` (атрибут устанавливается в `__init__`, не требует API-вызова)
- Тест без флага: создать агент без `HEAVY_MODEL` (или `HEAVY_MODEL=false`), проверить `agent._model == "deepseek-chat"`
- Оба теста можно написать без мока API — `__init__` устанавливает `_model` до любых API-вызовов

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 1-Исправление бага*
*Context gathered: 2026-05-08*
