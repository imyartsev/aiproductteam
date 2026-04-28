from __future__ import annotations

from orchestrator.state import ProjectState, DeployConfig
from .base import BaseAgent


class DevOpsAgent(BaseAgent):
    role = "devops"

    def process(self, state: ProjectState) -> ProjectState:
        prompt = (
            f"Архитектура:\n\n{state.arch_decision.content}\n\n"
            f"Код:\n\n{state.code_artifact.content}\n\n"
            f"Отчёт QA:\n\n{state.test_report.content}"
        )
        result = self.run(prompt)
        state.deploy_config = DeployConfig(content=result)
        return state
