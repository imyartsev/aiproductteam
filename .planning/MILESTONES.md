# Milestones

## v1.0 — MVP

**Shipped:** 2026-05-08
**Archived:** 2026-05-10
**Phases:** 1-3 (3 этапа, 5 планов)
**Timeline:** 2026-04-28 → 2026-05-08 (10 дней)
**Files:** 29 изменено, 2795 добавлено, 42 удалено
**Python LOC:** 954

**Delivered:** Pipeline принимает текстовую задачу и генерирует запускаемый FastAPI сервис (19 файлов) с проходящими тестами, верифицированный через Docker.

**Key accomplishments:**
1. Устранён баг `use_heavy_model` → `use_reasoner` — флаг `HEAVY_MODEL=true` корректно активирует reasoner-модель
2. Реализован парсер `# path:` маркеров — pipeline создаёт реальные файлы из markdown-вывода агентов
3. Улучшены промпты Dev и QA — стабильный Python-стек, TestClient, requirements.txt
4. Создан `verify.py` — автоматическая верификация через Docker (4 шага: build, run, health, pytest)
5. Полный демо-прогон: `verify.py` → PASS, 38 тестов в Docker за 0.37s

**Archive:** `.planning/milestones/v1.0-ROADMAP.md`
**Requirements:** `.planning/milestones/v1.0-REQUIREMENTS.md`
