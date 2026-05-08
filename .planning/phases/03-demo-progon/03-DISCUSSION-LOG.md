# Phase 3: Демо-прогон - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-08
**Phase:** 03-demo-progon
**Areas discussed:** Промпты агентов, Проверка результата, Что делать если не запустится, Среда запуска

---

## Промпты агентов

### Dev-агент — улучшать ли промпт?

| Option | Description | Selected |
|--------|-------------|----------|
| Да, улучшить | Добавить requirements.txt, SQLite+SQLAlchemy, рабочий FastAPI-код | ✓ |
| Нет, запустить как есть | Проверить текущие промпты без изменений | |

**User's choice:** Да, улучшить

---

### Dev-агент — выбор стека

| Option | Description | Selected |
|--------|-------------|----------|
| FastAPI + SQLite + SQLAlchemy | Простой стек для демо | |
| FastAPI + SQLite (raw sqlite3) | Без ORM | |
| Пусть агент выбирает сам | Architect выбирает, Dev следует | ✓ |

**User's choice:** Пусть агент выбирает сам (Dev читает arch_decision и следует)

---

### Dev-агент — обязательные артефакты

| Option | Description | Selected |
|--------|-------------|----------|
| requirements.txt | Список зависимостей | ✓ |
| README.md с инструкцией запуска | Инструкция через Docker | ✓ |
| Ничего дополнительного | Только Python-файлы | |

**User's choice:** requirements.txt + README.md с инструкцией запуска

---

### QA-агент — формат тестов

| Option | Description | Selected |
|--------|-------------|----------|
| pytest с TestClient | Тесты через FastAPI TestClient, не нужен живой сервер | ✓ |
| httpx / requests | Нужен запущенный сервер | |
| Пусть QA-агент выбирает сам | Адаптируется к коду Dev | |

**User's choice:** pytest с TestClient

---

## Проверка результата

### Способ проверки

| Option | Description | Selected |
|--------|-------------|----------|
| Написать скрипт проверки | verify.py: pip install → docker build → uvicorn → pytest → /health | ✓ |
| Вручную | Пользователь сам запускает uvicorn и pytest | |
| Встроить в pipeline | Pipeline автоматически пробует запустить сервис | |

**User's choice:** Написать скрипт проверки

---

### Что делает скрипт

| Option | Description | Selected |
|--------|-------------|----------|
| pip install -r requirements.txt | Установить зависимости | ✓ |
| uvicorn + проверить старт | Запустить сервер, убедиться что стартует | ✓ |
| pytest + exit code 0 | Запустить тесты | ✓ |
| HTTP GET /health | Реальный HTTP-запрос к сервису | ✓ |

**User's choice:** Все четыре шага

---

### Расположение скрипта

| Option | Description | Selected |
|--------|-------------|----------|
| В корне проекта | verify.py рядом с main.py | ✓ |
| В папке сгенерированного проекта | Попадает в projects/<slug>/ | |

**User's choice:** В корне проекта

---

## Что делать если не запустится

| Option | Description | Selected |
|--------|-------------|----------|
| Демо провалено, фиксим промпты | Этап не завершён, дорабатываем промпты | ✓ |
| Разрешить ручные правки | Минимальные ручные исправления допускаются | |
| Добавить retry в pipeline | Pipeline повторно запрашивает Dev-агента | |

**User's choice:** Демо провалено, фиксим промпты

---

## Среда запуска

### Runtime среда

| Option | Description | Selected |
|--------|-------------|----------|
| Текущее виртуальное окружение | pip install в текущей venv | |
| Новое виртуальное окружение | Отдельная venv для сгенерированного проекта | |
| Docker | docker build + docker run | ✓ |

**User's choice:** Docker

---

### Как запускать pytest через Docker

| Option | Description | Selected |
|--------|-------------|----------|
| docker run ... pytest | Запуск pytest внутри контейнера | ✓ |
| pytest напрямую (вне Docker) | Установить локально, запустить напрямую | |
| docker-compose up | Добавить test-сервис в docker-compose.yml | |

**User's choice:** docker run ... pytest (запуск в изоляции)

---

## Claude's Discretion

- Таймаут ожидания старта Docker-контейнера
- Имя Docker-образа (slug папки)
- Реализация verify.py (subprocess vs docker SDK)
- Порт uvicorn (8000)
- Очистка Docker-ресурсов после проверки

## Deferred Ideas

None — discussion stayed within phase scope
