"""Инструменты для работы с Git."""
from __future__ import annotations

import subprocess
from pathlib import Path


def _git(args: list[str], cwd: str | None = None) -> str:
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return (result.stdout + result.stderr).strip()


def git_status(repo_path: str = ".") -> str:
    return _git(["status", "--short"], cwd=repo_path)


def git_commit(message: str, repo_path: str = ".") -> str:
    _git(["add", "-A"], cwd=repo_path)
    return _git(["commit", "-m", message], cwd=repo_path)


TOOL_DEFINITIONS = [
    {
        "name": "git_status",
        "description": "Show the git status of a repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_path": {"type": "string", "description": "Path to git repo", "default": "."},
            },
        },
    },
    {
        "name": "git_commit",
        "description": "Stage all changes and create a git commit",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Commit message"},
                "repo_path": {"type": "string", "description": "Path to git repo", "default": "."},
            },
            "required": ["message"],
        },
    },
]
