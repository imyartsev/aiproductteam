"""Тесты pipeline в dry-run режиме (без вызовов API)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Добавляем корень проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from orchestrator.pipeline import run_pipeline, save_results
from orchestrator.state import ProjectState


def test_dry_run_pipeline_returns_state():
    state = run_pipeline("Создай простой REST API", dry_run=True)
    assert isinstance(state, ProjectState)
    assert state.raw_task == "Создай простой REST API"


def test_dry_run_all_artifacts_populated():
    state = run_pipeline("Hello World", dry_run=True)
    assert state.task_spec.content != ""
    assert state.arch_decision.content != ""
    assert state.tech_spec.content != ""
    assert state.code_artifact.content != ""
    assert state.test_report.content != ""
    assert state.deploy_config.content != ""


def test_save_results_creates_files(tmp_path):
    state = run_pipeline("Test task", dry_run=True)
    project_dir = save_results(state, output_dir=str(tmp_path))
    files = list(project_dir.iterdir())
    assert len(files) == 6
    names = {f.name for f in files}
    assert "01_task_spec.md" in names
    assert "06_deploy_config.md" in names
