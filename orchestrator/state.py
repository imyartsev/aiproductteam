from __future__ import annotations

from pydantic import BaseModel, Field


class Artifact(BaseModel):
    content: str = ""


class TaskSpec(Artifact):
    """Артефакт PO: user stories + критерии приёмки."""


class ArchDecision(Artifact):
    """Артефакт Architect: стек, ADR, структура проекта."""


class TechSpec(Artifact):
    """Артефакт Analyst: API-контракты, модели данных, бизнес-логика."""


class CodeArtifact(Artifact):
    """Артефакт Dev: готовый код."""


class TestReport(Artifact):
    """Артефакт QA: тесты + баг-репорты."""


class DeployConfig(Artifact):
    """Артефакт DevOps: Dockerfile, CI, инструкция деплоя."""


class ProjectState(BaseModel):
    """Общее состояние, передаваемое через весь pipeline."""

    raw_task: str
    task_spec: TaskSpec = Field(default_factory=TaskSpec)
    arch_decision: ArchDecision = Field(default_factory=ArchDecision)
    tech_spec: TechSpec = Field(default_factory=TechSpec)
    code_artifact: CodeArtifact = Field(default_factory=CodeArtifact)
    test_report: TestReport = Field(default_factory=TestReport)
    deploy_config: DeployConfig = Field(default_factory=DeployConfig)
