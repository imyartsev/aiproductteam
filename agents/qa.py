from __future__ import annotations

from orchestrator.state import ProjectState, TestReport
from .base import BaseAgent


class QAAgent(BaseAgent):
    role = "qa"

    def process(self, state: ProjectState) -> ProjectState:
        prompt = (
            f"Технические требования:\n\n{state.tech_spec.content}\n\n"
            f"Реализованный код:\n\n{state.code_artifact.content}"
        )
        result = self.run(prompt)
        state.test_report = TestReport(content=result)
        return state
