# Requirements: AI Product Team

**Defined:** 2026-05-08
**Core Value:** Дать задачу текстом — получить рабочий, запускаемый код: от пользовательских историй до Dockerfile.

## v1 Requirements

### Исправление багов

- [x] **FIX-01**: Атрибут `use_heavy_model` в `agents/po.py` и `agents/architect.py` переименован в `use_reasoner` — флаг `HEAVY_MODEL=true` активирует reasoner-модель для PO и Architect

### Извлечение кода

- [ ] **CODE-01**: После вызова Dev-агента pipeline парсит `# path: <путь>` маркеры из вывода и создаёт реальные файлы в `projects/<slug>/`
- [ ] **CODE-02**: Вложенные пути обрабатываются корректно (`src/api/router.py` создаёт директории и файл)
- [ ] **CODE-03**: Тестовые файлы из вывода QA-агента сохраняются как отдельные `.py` файлы (не только в отчёте `05_test_report.md`)

### DevOps-файлы

- [ ] **DEPLOY-01**: Dockerfile из вывода DevOps-агента создаётся как реальный файл в `projects/<slug>/`
- [ ] **DEPLOY-02**: CI-конфиг (GitHub Actions `.yml` или аналог) из вывода DevOps-агента создаётся как реальный файл

### Демо-прогон

- [ ] **DEMO-01**: Pipeline полностью выполняется с задачей "Создай FastAPI сервис для управления задачами" — все 6 агентов отрабатывают без ошибок
- [ ] **DEMO-02**: Вывод каждого агента содержательный и соответствует роли: PO — user stories с критериями приёмки, Architect — решения по стеку/структуре, Analyst — API-контракты, Dev — Python-код, QA — тесты, DevOps — Dockerfile/CI
- [ ] **DEMO-03**: Сгенерированный FastAPI проект запускается командой `uvicorn` без дополнительных ручных правок
- [ ] **DEMO-04**: Тесты в сгенерированном проекте проходят (`pytest`)

## v2 Requirements

### Надёжность

- **REL-01**: Retry-логика при ошибках DeepSeek API (rate limit, network timeout)
- **REL-02**: Валидация вывода агента — предупреждение при пустом `content`
- **REL-03**: Рефакторинг dry-run логики — `DryRunAgent` вместо inline-ветки в pipeline

### Расширение возможностей

- **EXT-01**: Интеграция инструментов из `tools/` — агенты могут вызывать file_ops, code_exec, git_ops
- **EXT-02**: Параллельное выполнение независимых агентов
- **EXT-03**: Поддержка JavaScript/TypeScript-проектов (не только Python)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Веб-интерфейс / UI для пайплайна | Командная строка достаточна для v1, UI сильно усложняет |
| Хранилище истории запусков (БД) | Файловый вывод достаточен, БД избыточна |
| Многоагентное параллельное выполнение | Pipeline последовательный по дизайну — каждый агент читает предыдущих |
| Docker-контейнер для самого пайплайна | Выходит за рамки demo |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FIX-01 | Phase 1 | Done (2026-05-08) |
| CODE-01 | Phase 2 | Pending |
| CODE-02 | Phase 2 | Pending |
| CODE-03 | Phase 2 | Pending |
| DEPLOY-01 | Phase 2 | Pending |
| DEPLOY-02 | Phase 2 | Pending |
| DEMO-01 | Phase 3 | Pending |
| DEMO-02 | Phase 3 | Pending |
| DEMO-03 | Phase 3 | Pending |
| DEMO-04 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-08*
*Last updated: 2026-05-08 — FIX-01 закрыт планом 01-01*
