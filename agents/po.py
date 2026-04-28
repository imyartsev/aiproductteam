from __future__ import annotations

from orchestrator.state import ProjectState, TaskSpec
from .base import BaseAgent


class POAgent(BaseAgent):
    role = "po"
    use_heavy_model = True

    def process(self, state: ProjectState) -> ProjectState:
        prompt = f"Бизнес-задача:\n\n{state.raw_task}"
        result = self.run(prompt)
        state.task_spec = TaskSpec(content=result)
        return state
