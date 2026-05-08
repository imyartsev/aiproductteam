# Phase 1: Исправление бага - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-08
**Phase:** 1-Исправление бага
**Areas discussed:** Тесты

---

## Тесты

### Что делаем с существующими тестами

| Вариант | Описание | Выбран |
|---------|----------|--------|
| Починить + добавить тест на баг | Исправить существующие тесты под OpenAI SDK И добавить проверку что use_reasoner работает | ✓ |
| Только переименовать атрибут | Сделать минимальную правку, не трогать сломанные тесты | |
| Удалить старые тесты | Убрать test_agents.py целиком, написать правильные потом | |

**User's choice:** Починить + добавить тест на баг

---

### Что именно проверяет тест на баг

| Вариант | Описание | Выбран |
|---------|----------|--------|
| Поведение: модель меняется при HEAVY_MODEL | При HEAVY_MODEL=true → deepseek-reasoner, без флага → deepseek-chat | ✓ |
| Структура: атрибут use_reasoner есть в классе | Просто hasattr(POAgent, 'use_reasoner') == True | |

**User's choice:** Поведение: модель меняется при HEAVY_MODEL

---

## Claude's Discretion

- Имена тестовых функций и внутренняя структура test_agents.py — на усмотрение планировщика

## Deferred Ideas

None — обсуждение не выходило за рамки этапа
