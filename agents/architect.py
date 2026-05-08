from __future__ import annotations

from orchestrator.state import ProjectState, ArchDecision
from .base import BaseAgent


class ArchitectAgent(BaseAgent):
    role = "architect"
    use_reasoner = True

    def process(self, state: ProjectState) -> ProjectState:
        prompt = (
            f"User Stories и критерии приёмки:\n\n{state.task_spec.content}"
        )
        result = self.run(prompt)
        state.arch_decision = ArchDecision(content=result)
        return state
