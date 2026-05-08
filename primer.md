# primer.md — рабочий журнал сессий

> Читай этот файл в начале каждой сессии. Дополняй в конце. Лимит: 50 строк.

---

## Архив сессий (сжатый)

**Сессия 1 (до 2026-04-28):** Реализован полный pipeline 6 агентов (PO→Arch→Analyst→Dev→QA→DevOps).
Стек: Python 3.13, DeepSeek API (openai SDK, base_url=https://api.deepseek.com).
Запуск: `PYTHONIOENCODING=utf-8 python main.py "задача"`.

**Этап 1 (2026-04-28..05-05):** Исправлен баг с флагом `use_heavy_model` → переименован в `use_reasoner`.
Починены тесты, верификация пройдена.

**Этап 2 (2026-05-05..05-07):** Реализован парсер `# path:` маркеров — агенты теперь
указывают целевые пути файлов в выводе, orchestrator корректно извлекает их в `projects/`.

**Этап 3 (2026-05-07..05-08):** Демо-прогон завершён. verify.py → PASS, 38 тестов.
Ключевые фиксы промптов: app/ вместо src/, python:3.10-slim, не исключать tests/ в .dockerignore.
pipeline.py: shutil.rmtree перед записью, гарантия pytest/httpx в requirements.txt.

---

## Текущий статус

- Ветка: master
- **Milestone v1 ДОСТИГНУТ** — все 3 этапа завершены
- Следующий шаг: новая задача / расширение функциональности

---

## Ключевые технические детали

- DeepSeek API: `DEEPSEEK_API_KEY` в `.env`, `HEAVY_MODEL=true` → deepseek-reasoner для PO/Arch
- Windows: запускать с `PYTHONIOENCODING=utf-8`
- Результаты пайплайна → `projects/`
- Верификация: `python verify.py projects/<slug>` (нужен запущенный Docker)
