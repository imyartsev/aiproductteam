---
plan: 03-03
status: complete
completed_at: 2026-05-08
duration: ~90min (итеративный цикл запуск→verify)
---

# SUMMARY: 03-03 — Демо-прогон и верификация

## Что сделано

Выполнен полный pipeline с задачей "Создай FastAPI сервис для управления задачами".

Все 6 агентов отработали: PO → Architect → Analyst → Dev → QA → DevOps.
Сгенерирована папка `projects/Создай_FastAPI_сервис_для_управления_зад/` с 19 файлами.

Финальный результат `verify.py`:
```
[OK] docker build -t fastapi
[OK] docker run -d -p 8000:8000
[OK] GET /health → 200 {"status":"ok"}
[OK] docker run pytest
  ============================== 38 passed in 0.37s ==============================
PASS
```

## Ключевые исправления (итерации)

В ходе цикла запуск→verify исправлены системные промпты:

| Проблема | Решение |
|----------|---------|
| `.dockerignore` исключал `tests/` и `*.md` | Добавлено явное правило "НЕЛЬЗЯ добавлять `tests/`, `*.md`" в `prompts/devops.md` |
| `python:3.12-slim` недоступен (нет в кэше Docker) | Зафиксирован `python:3.10-slim` как единственный допустимый образ |
| Dev → `app/main.py`, DevOps → `src/main.py` (конфликт) | Добавлено требование `app/` во все три промпта (dev, qa, devops) |
| pytest не в PATH при `docker run pytest` | `verify.py` теперь использует `python -m pytest` |
| pytest отсутствует в `requirements.txt` | `pipeline.py` гарантирует наличие `pytest` и `httpx` в `requirements.txt` |
| Накопление старых файлов между прогонами | `pipeline.py` делает `shutil.rmtree(project_dir)` перед созданием |

## Артефакты

- `projects/Создай_FastAPI_сервис_для_управления_зад/` — рабочий FastAPI сервис (19 файлов)
- `verify.py` — скрипт верификации через Docker (создан в плане 03-02)
- `prompts/dev.md`, `prompts/qa.md`, `prompts/devops.md` — обновлённые системные промпты
- `orchestrator/pipeline.py` — добавлена очистка папки и гарантия pytest/httpx

## Статус: PASS — milestone v1 достигнут
