from __future__ import annotations

import os
import shutil
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from agents import POAgent, ArchitectAgent, AnalystAgent, DevAgent, QAAgent, DevOpsAgent
from orchestrator.extractor import extract_files
from orchestrator.state import ProjectState

console = Console(highlight=False, legacy_windows=False)

STEPS = [
    ("PO",        POAgent,        "task_spec"),
    ("Architect", ArchitectAgent, "arch_decision"),
    ("Analyst",   AnalystAgent,   "tech_spec"),
    ("Dev",       DevAgent,       "code_artifact"),
    ("QA",        QAAgent,        "test_report"),
    ("DevOps",    DevOpsAgent,    "deploy_config"),
]


def run_pipeline(task: str, dry_run: bool = False) -> ProjectState:
    state = ProjectState(raw_task=task)

    console.print(Panel(f"[bold cyan]Задача:[/] {task}", title="AI Product Team"))

    for name, AgentClass, artifact_field in STEPS:
        console.print(f"\n[bold yellow]>> {name}[/] обрабатывает задачу...")

        if dry_run:
            setattr(
                state,
                artifact_field,
                getattr(state, artifact_field).__class__(
                    content=f"[dry-run] {name} output"
                ),
            )
            console.print(f"[dim]  (dry-run, пропущено)[/]")
            continue

        agent = AgentClass()
        state = agent.process(state)
        artifact = getattr(state, artifact_field)
        preview = artifact.content[:200].replace("\n", " ")
        console.print(f"[green]  OK[/] {preview}{'...' if len(artifact.content) > 200 else ''}")

    return state


def save_results(state: ProjectState, output_dir: str | None = None) -> Path:
    base = Path(output_dir or os.environ.get("PROJECTS_DIR", "./projects"))
    # Используем первые 40 символов задачи как имя папки
    slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in state.raw_task[:40])
    project_dir = base / slug
    if project_dir.exists():
        shutil.rmtree(project_dir)
    project_dir.mkdir(parents=True)

    artifacts = {
        "01_task_spec.md": state.task_spec.content,
        "02_arch_decision.md": state.arch_decision.content,
        "03_tech_spec.md": state.tech_spec.content,
        "04_code.md": state.code_artifact.content,
        "05_test_report.md": state.test_report.content,
        "06_deploy_config.md": state.deploy_config.content,
    }

    for filename, content in artifacts.items():
        (project_dir / filename).write_text(content, encoding="utf-8")

    # Извлекаем реальные файлы из вывода Dev, QA и DevOps
    extract_files(state.code_artifact.content, project_dir)
    extract_files(state.test_report.content, project_dir)
    extract_files(state.deploy_config.content, project_dir)

    # Гарантируем наличие тестовых зависимостей в requirements.txt
    req_file = project_dir / "requirements.txt"
    if req_file.exists():
        req_content = req_file.read_text(encoding="utf-8")
        additions = []
        for pkg in ("pytest", "httpx"):
            if pkg not in req_content:
                additions.append(pkg)
        if additions:
            req_file.write_text(req_content.rstrip() + "\n" + "\n".join(additions) + "\n", encoding="utf-8")

    real_files = [f for f in project_dir.rglob("*") if f.is_file() and not f.name.endswith(".md")]
    console.print(f"\n[bold green]OK Результаты сохранены:[/] {project_dir}")
    if real_files:
        console.print(f"[dim]  Создано файлов проекта: {len(real_files)}[/]")
    return project_dir
