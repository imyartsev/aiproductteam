from __future__ import annotations

import os
from pathlib import Path

from openai import OpenAI

CHAT_MODEL = "deepseek-chat"
REASONER_MODEL = "deepseek-reasoner"

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com",
        )
    return _client


def _load_prompt(name: str) -> str:
    path = Path(__file__).parent.parent / "prompts" / f"{name}.md"
    return path.read_text(encoding="utf-8")


class BaseAgent:
    """Базовый класс агента. Загружает системный промпт и вызывает DeepSeek API."""

    role: str  # переопределяется в подклассах
    use_reasoner: bool = False  # True → deepseek-reasoner вместо deepseek-chat

    def __init__(self) -> None:
        self._system_prompt = _load_prompt(self.role)
        heavy = os.environ.get("HEAVY_MODEL", "false").lower() == "true"
        self._model = REASONER_MODEL if (heavy and self.use_reasoner) else CHAT_MODEL

    def run(self, user_message: str) -> str:
        """Отправляет сообщение агенту и возвращает текстовый ответ."""
        client = _get_client()
        response = client.chat.completions.create(
            model=self._model,
            max_tokens=8192,
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or ""
