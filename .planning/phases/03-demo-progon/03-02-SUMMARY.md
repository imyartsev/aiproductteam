---
plan: 03-02
status: completed
completed_at: 2026-05-08
duration: ~1m
---

# SUMMARY: 03-02 — Создание verify.py

## Что сделано
- Создан `verify.py` в корне проекта
- Реализованы все 4 шага верификации: docker build, docker run + wait, GET /health, docker run pytest
- Cleanup в finally (docker stop + docker rm)
- Retry-loop: 3 попытки по 5 сек = 15 сек максимум
- Выводит пошаговый [OK]/[FAIL] лог и итоговый PASS/FAIL

## Артефакты
- `verify.py` — создан

## Проверки прошли
- Синтаксис Python корректен ✓
- Принимает 1 аргумент (путь к папке) ✓
- docker build ✓
- docker run -d + retry-loop ✓
- GET http://localhost:8000/health ✓
- docker run pytest ✓
- cleanup в finally ✓
- sys.exit(0)/sys.exit(1) ✓
