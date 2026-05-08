# AI Product Team

Автономная команда ИИ-агентов, моделирующая продуктовую команду разработки.

## Что делает

Принимает задачу на входе (текстовое описание), прогоняет через полный pipeline и выдаёт готовый код, тесты и конфигурацию деплоя.

**Pipeline:** PO → Architect → Analyst → Dev → QA → DevOps

## Быстрый старт

```bash
cp .env.example .env   # добавить ANTHROPIC_API_KEY
pip install -e .
python main.py "Опиши задачу здесь"
```

Без API-ключа (для проверки структуры):
```bash
python main.py --dry-run "Опиши задачу здесь"
```

## Структура

```
agents/        — реализация агентов
prompts/       — system prompts (Markdown)
orchestrator/  — pipeline + shared state (Pydantic)
tools/         — инструменты (file, code, git)
projects/      — результаты работы команды
tests/         — тесты
памятки/       — техническая документация проекта
```

## Модели

- По умолчанию: `deepseek-chat` (V3)
- PO и Architect: `deepseek-reasoner` (R1) при `HEAVY_MODEL=true` в `.env`

## Тесты

```bash
pytest tests/
```
