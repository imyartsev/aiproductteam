from __future__ import annotations

from orchestrator.state import ProjectState, TechSpec
from .base import BaseAgent


class AnalystAgent(BaseAgent):
    role = "analyst"

    def process(self, state: ProjectState) -> ProjectState:
        prompt = (
            f"User Stories:\n\n{state.task_spec.content}\n\n"
            f"Архитектурные решения:\n\n{state.arch_decision.content}"
        )
        result = self.run(prompt)
        state.tech_spec = TechSpec(content=result)
        return state
