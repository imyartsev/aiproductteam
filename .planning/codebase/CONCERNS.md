# Codebase Concerns

**Analysis Date:** 2026-05-08

## Tech Debt

**Сломанный флаг `use_heavy_model` в PO и Architect агентах:**
- Issue: В `agents/po.py` и `agents/architect.py` объявлен атрибут `use_heavy_model = True`, тогда как `BaseAgent` читает атрибут `use_reasoner`. Флаг тихо игнорируется — PO и Architect **никогда** не используют deepseek-reasoner, даже при `HEAVY_MODEL=true`.
- Files: `agents/po.py` (строка 9), `agents/architect.py` (строка 9), `agents/base.py` (строка 33, 38)
- Impact: Функция "умной" модели для стратегических агентов не работает. Пользователь устанавливает `HEAVY_MODEL=true` в `.env`, не получает никакого эффекта и не узнаёт об этом.
- Fix approach: Переименовать атрибуты в `po.py` и `architect.py` с `use_heavy_model` на `use_reasoner`, либо добавить псевдоним в `BaseAgent.__init__`.

**Инструменты `tools/` не подключены к агентам:**
- Issue: Модули `tools/file_ops.py`, `tools/code_exec.py`, `tools/git_ops.py` содержат `TOOL_DEFINITIONS` для Claude tool use API, но ни один агент их не вызывает. `BaseAgent.run()` передаёт в API только системный промпт и сообщение пользователя — без параметра `tools`.
- Files: `agents/base.py` (строки 43–51), `tools/file_ops.py`, `tools/code_exec.py`, `tools/git_ops.py`
- Impact: Dev-агент генерирует код, но не может фактически записать файлы. QA-агент не может запустить тесты. DevOps-агент не может сделать коммит. Вся работа остаётся текстом в одном Markdown-файле.
- Fix approach: Добавить в `BaseAgent.run()` поддержку tool use loop: передавать `tools` в `chat.completions.create`, обрабатывать `tool_calls` в ответе, диспетчеризировать вызовы к реальным функциям, возвращать результаты в следующем сообщении.

**Переменная окружения названа `ANTHROPIC_API_KEY` в тестах, а нужна `DEEPSEEK_API_KEY`:**
- Issue: `tests/test_pipeline.py` и `tests/test_agents.py` устанавливают `os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")`, тогда как `agents/base.py` читает `os.environ["DEEPSEEK_API_KEY"]`. Если тесты когда-либо выйдут за пределы dry-run или мок-слоя, возникнет `KeyError`.
- Files: `tests/test_pipeline.py` (строка 13), `tests/test_agents.py` (строка 13), `agents/base.py` (строка 18)
- Impact: Скрытая бомба: тесты сейчас проходят только потому что `_get_client()` не вызывается в dry-run, а в `test_agents.py` клиент замокирован. При любом изменении тестов без мока произойдёт `KeyError`.
- Fix approach: Заменить `ANTHROPIC_API_KEY` на `DEEPSEEK_API_KEY` в обоих тестовых файлах.

**Dry-run режим работает только с дефолтными Pydantic-полями:**
- Issue: `pipeline.py` (строки 33–38) в режиме dry-run вызывает `getattr(state, artifact_field).__class__(content=...)`. Это работает только если у класса артефакта нет обязательных полей кроме `content`. Если в будущем добавить поле с `Field(...)` без дефолта — dry-run сломается с `ValidationError`.
- Files: `orchestrator/pipeline.py` (строки 33–38), `orchestrator/state.py`
- Impact: Хрупкий dry-run, который ломается при расширении моделей состояния.
- Fix approach: Использовать явные фабрики `TaskSpec(content=...)` вместо динамического `__class__()`, либо вынести dry-run заглушки в сами классы артефактов.

**Глобальный синглтон клиента без thread-safety:**
- Issue: `agents/base.py` использует глобальную переменную `_client: OpenAI | None = None` с паттерном ленивой инициализации (строки 11–21), который не защищён блокировкой.
- Files: `agents/base.py` (строки 11–21)
- Impact: В однопоточном pipeline это безопасно. При добавлении параллельного выполнения агентов возможно создание нескольких клиентов или race condition.
- Fix approach: Добавить `threading.Lock()` вокруг инициализации, либо инициализировать клиент явно при старте pipeline.

## Known Bugs

**Тест `test_prompt_cache_control_set` проверяет несуществующую функцию:**
- Symptoms: Тест проверяет `call_kwargs["system"][0]["cache_control"]`, но `BaseAgent.run()` строит `messages` как список dict с ключами `role`/`content` и не добавляет `system` как отдельный параметр с `cache_control`. Тест упадёт с `KeyError`.
- Files: `tests/test_agents.py` (строки 59–71), `agents/base.py` (строки 43–51)
- Trigger: `pytest tests/test_agents.py::test_prompt_cache_control_set`
- Workaround: Тест пишет в мок `messages.create`, тогда как реальный код вызывает `chat.completions.create` — мок вообще не перехватывает реальный вызов, поэтому тест может случайно "пройти" не проверив ничего реального.

**Слаг папки проекта обрезается до 40 символов без проверки уникальности:**
- Symptoms: Две задачи с одинаковыми первыми 40 символами перезапишут папку друг друга без предупреждения.
- Files: `orchestrator/pipeline.py` (строки 54–56)
- Trigger: Запустить pipeline дважды с похожими задачами (например, отличающимися после 40-го символа).
- Workaround: Нет; результаты тихо перезаписываются.

## Security Considerations

**Выполнение произвольного Python-кода без изоляции:**
- Risk: `tools/code_exec.py` выполняет любой Python-код через `subprocess.run([sys.executable, "-c", code])`. Код запускается от имени текущего пользователя с полным доступом к файловой системе и сети.
- Files: `tools/code_exec.py` (строки 9–23)
- Current mitigation: Только таймаут (30 сек по умолчанию). Никакой sandbox-изоляции, chroot, или ограничений syscall.
- Recommendations: Если инструмент планируется реально подключить к агентам, необходима изоляция: Docker-контейнер, `seccomp`-профиль, или специализированный sandbox (например, `pyodide`, `RestrictedPython`). Минимум — запрет сетевого доступа и ограничение разрешённых путей файловой системы.

**`git_commit` выполняет `git add -A` без фильтрации:**
- Risk: `tools/git_ops.py` индексирует все изменения в репозитории (`git add -A`) перед коммитом. Если агент вызовет этот инструмент в рабочем репозитории, в коммит попадут все незакоммиченные изменения, включая `.env` и другие чувствительные файлы.
- Files: `tools/git_ops.py` (строки 22–24)
- Current mitigation: Инструмент не подключён к агентам (см. раздел Tech Debt), поэтому риск пока не реализован.
- Recommendations: При подключении — ограничить область `git add` только папкой `projects/`, добавить проверку `.gitignore` перед коммитом.

**Ключ API хранится только в `.env` без валидации при старте:**
- Risk: Если `DEEPSEEK_API_KEY` отсутствует, `agents/base.py` бросает `KeyError: 'DEEPSEEK_API_KEY'` только при первом обращении к агенту (внутри pipeline). Пользователь видит трассировку стека вместо понятного сообщения об ошибке.
- Files: `agents/base.py` (строка 18), `main.py`
- Current mitigation: `.env.example` документирует переменную.
- Recommendations: Добавить явную проверку наличия `DEEPSEEK_API_KEY` в `main.py` до запуска pipeline с понятным сообщением об ошибке.

## Performance Bottlenecks

**Последовательный pipeline без возможности параллелизации:**
- Problem: Все 6 агентов выполняются строго последовательно. Каждый агент ожидает ответа LLM (типичное время: 10–60 сек на запрос). Итого pipeline занимает 1–6 минут при `deepseek-chat` и потенциально 10+ минут с `deepseek-reasoner`.
- Files: `orchestrator/pipeline.py` (строки 29–47)
- Cause: Жёстко последовательный цикл `for name, AgentClass, artifact_field in STEPS`. Нет ни async, ни параллельных веток.
- Improvement path: Некоторые агенты могут выполняться параллельно (например, после Architect можно запускать Analyst и DevOps параллельно). Переход на `asyncio` + `asyncio.gather` для независимых шагов.

**Нет ограничения на размер контекста, передаваемого в LLM:**
- Problem: Каждый следующий агент получает в промпте полный текст артефактов предыдущих. К DevOps-агенту в промпт попадает сумма arch + code + test_report, что может превышать 30K токенов.
- Files: `agents/devops.py` (строки 11–17), `agents/qa.py` (строки 11–15)
- Cause: Нет обрезки, суммаризации или выборки релевантных частей контекста.
- Improvement path: Добавить максимальный размер контекста на входе каждого агента, либо промежуточный агент-суммаризатор.

## Fragile Areas

**`orchestrator/pipeline.py` — связка имён полей через строки:**
- Files: `orchestrator/pipeline.py` (строки 14–21, 33–47)
- Why fragile: Имена артефактов в `STEPS` (`"task_spec"`, `"arch_decision"` и т.д.) — строковые литералы. Переименование поля в `ProjectState` не вызовет ошибку компиляции, только `AttributeError` в рантайме. IDE-рефакторинг не поможет.
- Safe modification: При добавлении нового агента нужно синхронно обновить: `orchestrator/state.py` (новый класс + поле), `orchestrator/pipeline.py` (новая строка в `STEPS`), `agents/__init__.py` (экспорт). Легко пропустить один шаг.
- Test coverage: Тесты проверяют только dry-run и не поймают опечатку в имени поля до реального запуска.

**`tools/` — `TOOL_DEFINITIONS` не синхронизированы с сигнатурами функций:**
- Files: `tools/file_ops.py`, `tools/code_exec.py`, `tools/git_ops.py`
- Why fragile: JSON-схемы `TOOL_DEFINITIONS` описывают параметры функций вручную. Если изменить сигнатуру функции (например, добавить параметр в `write_file`), схема устареет без каких-либо ошибок.
- Safe modification: Рассмотреть генерацию схем через `inspect` или библиотеку типа `instructor`/`pydantic` для автоматической синхронизации.
- Test coverage: Нет тестов, проверяющих соответствие схем реальным функциям.

## Scaling Limits

**Один текстовый файл как единственный артефакт кода:**
- Current capacity: Dev-агент генерирует весь код одним блоком Markdown в `04_code.md`.
- Limit: Для проектов с 5+ файлами LLM начинает путать структуру и пропускать файлы. Контекстное окно ограничивает объём генерируемого кода примерно 500–1000 строками.
- Scaling path: Добавить структурированный `CodeArtifact` с полем `files: dict[str, str]` (путь → содержимое) и реальную запись файлов через `tools/file_ops.py`.

## Dependencies at Risk

**`openai` SDK используется как клиент DeepSeek:**
- Risk: DeepSeek имеет OpenAI-совместимый API, поэтому это работает, но зависит от совместимости. Обновление `openai` SDK может сломать совместимость (изменения в форматах запросов/ответов).
- Impact: `agents/base.py` — единственное место интеграции. При поломке упадут все агенты.
- Migration plan: Абстрагировать клиент за интерфейсом (например, `LLMClient` protocol), чтобы легко переключаться между провайдерами. Зафиксировать версию `openai` в `pyproject.toml` (сейчас только `>=1.0` без верхней границы).

## Missing Critical Features

**Нет обработки ошибок API:**
- Problem: `BaseAgent.run()` не обрабатывает ошибки сети, rate limit, таймаут или невалидный ответ от DeepSeek API. Любое исключение поднимается до `main.py`, который тоже не имеет `try/except`.
- Blocks: Надёжная работа в production. При rate limit или кратковременном сбое сети весь pipeline падает без сохранения уже выполненных артефактов.

**Нет возобновления (resume) pipeline после сбоя:**
- Problem: Если pipeline упал на шаге 4 (Dev), результаты шагов 1–3 потеряны (не сохранены на диск до завершения). Нужно запускать заново с нуля.
- Blocks: Экономное использование API-квот. При цене ~$0.01–0.10 на запрос повторный прогон 6 агентов дорог.

## Test Coverage Gaps

**Нет интеграционных тестов реальных агентов:**
- What's not tested: Реальные вызовы к DeepSeek API. Качество и структура выходных артефактов.
- Files: `tests/test_agents.py`, `tests/test_pipeline.py`
- Risk: Изменение промптов в `prompts/*.md` не обнаруживается тестами — деградация качества вывода невидима.
- Priority: Medium

**Нет тестов для `tools/`:**
- What's not tested: `read_file`, `write_file`, `list_files`, `run_python`, `git_status`, `git_commit`.
- Files: `tools/file_ops.py`, `tools/code_exec.py`, `tools/git_ops.py`
- Risk: При подключении инструментов к агентам баги в tools будут обнаружены только в рантайме.
- Priority: High (особенно `run_python` и `git_commit` — функции с side effects)

**Тест `test_base_agent_run` мокирует неправильный метод:**
- What's not tested: Реальный путь вызова `client.chat.completions.create()`. Тест мокирует `client.messages.create` (Anthropic API), тогда как код вызывает `client.chat.completions.create` (OpenAI API).
- Files: `tests/test_agents.py` (строки 31, 40)
- Risk: Тест проходит, но реальный вызов не верифицирован. При смене клиента тест продолжит проходить некорректно.
- Priority: High

---

*Concerns audit: 2026-05-08*
