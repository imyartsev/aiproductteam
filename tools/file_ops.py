"""Инструменты для чтения/записи файлов — используются агентами через tool use."""
from __future__ import annotations

from pathlib import Path


def read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written {len(content)} chars to {path}"


def list_files(directory: str, pattern: str = "**/*") -> list[str]:
    base = Path(directory)
    return [str(p.relative_to(base)) for p in base.glob(pattern) if p.is_file()]


# Определения инструментов для Claude tool use API
TOOL_DEFINITIONS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to read"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file, creating directories if needed",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to write"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "list_files",
        "description": "List files in a directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory to list"},
                "pattern": {"type": "string", "description": "Glob pattern", "default": "**/*"},
            },
            "required": ["directory"],
        },
    },
]
