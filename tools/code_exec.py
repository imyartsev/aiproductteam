"""Инструмент выполнения Python-кода в изолированном subprocess."""
from __future__ import annotations

import subprocess
import sys
import textwrap


def run_python(code: str, timeout: int = 30) -> str:
    """Выполняет Python-код и возвращает stdout + stderr."""
    dedented = textwrap.dedent(code)
    result = subprocess.run(
        [sys.executable, "-c", dedented],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = result.stdout
    if result.stderr:
        output += f"\n[stderr]\n{result.stderr}"
    if result.returncode != 0:
        output += f"\n[exit code: {result.returncode}]"
    return output or "(no output)"


TOOL_DEFINITIONS = [
    {
        "name": "run_python",
        "description": "Execute Python code and return stdout/stderr output",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"},
                "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30},
            },
            "required": ["code"],
        },
    },
]
