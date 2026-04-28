# AI Product Team

Автономная команда ИИ-агентов, моделирующая продуктовую команду разработки.

## Назначение
Принимает задачу на входе (текстовое описание), прогоняет её через полный pipeline
и выдаёт готовый код, тесты и конфигурацию деплоя в папку `projects/`.

## Pipeline (последовательность)

```
PO → Architect → Analyst → Dev → QA → DevOps
```

## Агенты и роли

| Агент     | Файл                 | Ответственность |
|-----------|----------------------|-----------------|
| PO        | agents/po.py         | Бизнес-цели, user stories, критерии приёмки |
| Architect | agents/architect.py  | Архитектурные решения (стек, паттерны, ADR) |
| Analyst   | agents/analyst.py    | Детальные требования и спецификации на основе архитектуры |
| Dev       | agents/dev.py        | Написание кода по спецификациям |
| QA        | agents/qa.py         | Тесты, проверка, баг-репорты |
| DevOps    | agents/devops.py     | Dockerfile, CI pipeline, конфиги деплоя |

### Логика pipeline
- **PO** получает бизнес-задачу → формулирует user stories и критерии приёмки
- **Architect** читает user stories → принимает архитектурные решения (стек, структура)
- **Analyst** читает user stories + архитектуру → пишет детальные технические требования и API-контракты
- **Dev** читает спецификации Analyst → пишет код
- **QA** читает спецификации + код → пишет тесты и фиксирует баги
- **DevOps** читает всё → готовит инфраструктуру и CI/CD

## Shared State (Pydantic)

Артефакты передаются через `orchestrator/state.py`:

```
TaskSpec → ArchDecision → TechSpec → CodeArtifact → TestReport → DeployConfig
```

## Структура проекта

```
ai-product-team/
├── agents/          # Реализация агентов
├── prompts/         # System prompts (Markdown)
├── orchestrator/    # Pipeline + Shared State
├── tools/           # Инструменты (file, code, git)
├── projects/        # Вывод: результаты работы команды
└── tests/           # Тесты
```

## Запуск

```bash
cp .env.example .env   # добавить ANTHROPIC_API_KEY
pip install -e .
python main.py "Создай FastAPI сервис для управления задачами"
```

## Добавление нового агента
1. Создать `agents/<role>.py`, унаследовать от `BaseAgent`
2. Написать system prompt в `prompts/<role>.md`
3. Добавить Pydantic-модель артефакта в `orchestrator/state.py`
4. Зарегистрировать шаг в `orchestrator/pipeline.py`

## Модели DeepSeek
- По умолчанию: `deepseek-chat` (V3, быстро + дёшево)
- PO и Architect: `deepseek-reasoner` (R1) при установке `HEAVY_MODEL=true` в `.env`

## Разработка

```bash
pytest tests/          # запуск тестов
python main.py --dry-run "задача"   # без реальных вызовов API
```
