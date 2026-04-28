from __future__ import annotations

from orchestrator.state import ProjectState, CodeArtifact
from .base import BaseAgent


class DevAgent(BaseAgent):
    role = "dev"

    def process(self, state: ProjectState) -> ProjectState:
        prompt = (
            f"Технические требования и спецификации:\n\n{state.tech_spec.content}"
        )
        result = self.run(prompt)
        state.code_artifact = CodeArtifact(content=result)
        return state
