"""Тесты агентов с мок-ответами DeepSeek/OpenAI API."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")

from agents.base import BaseAgent
from orchestrator.state import ProjectState, TaskSpec


def _make_mock_response(text: str):
    mock_message = MagicMock()
    mock_message.content = text
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    response = MagicMock()
    response.choices = [mock_choice]
    return response


@patch("agents.base._get_client")
def test_base_agent_run(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_mock_response("Hello from agent")
    mock_get_client.return_value = mock_client

    class TestAgent(BaseAgent):
        role = "po"

    agent = TestAgent()
    result = agent.run("test prompt")
    assert result == "Hello from agent"
    mock_client.chat.completions.create.assert_called_once()


@patch("agents.base._get_client")
def test_po_agent_populates_task_spec(mock_get_client):
    from agents.po import POAgent

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_mock_response("## User Stories\n- Story 1")
    mock_get_client.return_value = mock_client

    state = ProjectState(raw_task="Build a todo app")
    agent = POAgent()
    result_state = agent.process(state)

    assert "Story 1" in result_state.task_spec.content


@patch("agents.base._get_client")
def test_base_agent_run_calls_completions_create(mock_get_client):
    """BaseAgent.run вызывает chat.completions.create с model и messages."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_mock_response("ok")
    mock_get_client.return_value = mock_client

    class TestAgent(BaseAgent):
        role = "po"

    TestAgent().run("hello")

    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert "model" in call_kwargs
    assert isinstance(call_kwargs["messages"], list)
    assert len(call_kwargs["messages"]) == 2  # system + user


@patch("agents.base._load_prompt", return_value="system prompt")
def test_po_uses_reasoner_when_heavy_model_true(mock_prompt):
    """При HEAVY_MODEL=true POAgent инициализируется с deepseek-reasoner."""
    from agents.po import POAgent
    os.environ["HEAVY_MODEL"] = "true"
    try:
        agent = POAgent()
        assert agent._model == "deepseek-reasoner"
    finally:
        del os.environ["HEAVY_MODEL"]


@patch("agents.base._load_prompt", return_value="system prompt")
def test_po_uses_chat_without_heavy_model(mock_prompt):
    """Без HEAVY_MODEL POAgent инициализируется с deepseek-chat."""
    from agents.po import POAgent
    os.environ.pop("HEAVY_MODEL", None)
    agent = POAgent()
    assert agent._model == "deepseek-chat"


@patch("agents.base._load_prompt", return_value="system prompt")
def test_architect_uses_reasoner_when_heavy_model_true(mock_prompt):
    """При HEAVY_MODEL=true ArchitectAgent инициализируется с deepseek-reasoner."""
    from agents.architect import ArchitectAgent
    os.environ["HEAVY_MODEL"] = "true"
    try:
        agent = ArchitectAgent()
        assert agent._model == "deepseek-reasoner"
    finally:
        del os.environ["HEAVY_MODEL"]


@patch("agents.base._load_prompt", return_value="system prompt")
def test_architect_uses_chat_without_heavy_model(mock_prompt):
    """Без HEAVY_MODEL ArchitectAgent инициализируется с deepseek-chat."""
    from agents.architect import ArchitectAgent
    os.environ.pop("HEAVY_MODEL", None)
    agent = ArchitectAgent()
    assert agent._model == "deepseek-chat"
