"""Unit-тесты для orchestrator/extractor.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.extractor import extract_files


SIMPLE_CONTENT = '''\
Вот код приложения:

```python
# path: src/main.py
print("hello")
```
'''

NESTED_PATH_CONTENT = '''\
CI конфиг:

```yaml
# path: .github/workflows/ci.yml
name: CI
on: [push]
```
'''

MULTI_FILE_CONTENT = '''\
```python
# path: app.py
x = 1
```

```python
# path: tests/test_app.py
assert True
```
'''

NO_MARKER_CONTENT = '''\
```python
print("no marker here")
```
'''


def test_extract_single_file(tmp_path):
    """Базовый случай: один файл с маркером."""
    created = extract_files(SIMPLE_CONTENT, tmp_path)
    assert len(created) == 1
    assert (tmp_path / "src" / "main.py").exists()
    assert (tmp_path / "src" / "main.py").read_text(encoding="utf-8") == 'print("hello")\n'


def test_extract_nested_path(tmp_path):
    """Вложенные директории создаются автоматически."""
    created = extract_files(NESTED_PATH_CONTENT, tmp_path)
    assert len(created) == 1
    ci_file = tmp_path / ".github" / "workflows" / "ci.yml"
    assert ci_file.exists()


def test_extract_multiple_files(tmp_path):
    """Несколько файлов в одном вводе."""
    created = extract_files(MULTI_FILE_CONTENT, tmp_path)
    assert len(created) == 2
    assert (tmp_path / "app.py").exists()
    assert (tmp_path / "tests" / "test_app.py").exists()


def test_no_markers_returns_empty(tmp_path):
    """Если маркеров нет — возвращает пустой список, файлы не создаются."""
    created = extract_files(NO_MARKER_CONTENT, tmp_path)
    assert created == []


def test_empty_content(tmp_path):
    """Пустая строка — возвращает пустой список."""
    created = extract_files("", tmp_path)
    assert created == []


def test_dry_run_content_not_extracted(tmp_path):
    """Dry-run вывод '[dry-run] Dev output' не содержит маркеров — пустой результат."""
    created = extract_files("[dry-run] Dev output", tmp_path)
    assert created == []
