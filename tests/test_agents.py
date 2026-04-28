"""Тесты агентов с мок-ответами Claude API."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from agents.base import BaseAgent
from orchestrator.state import ProjectState, TaskSpec


def _make_mock_response(text: str):
    block = MagicMock()
    block.type = "text"
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


@patch("agents.base._get_client")
def test_base_agent_run(mock_get_client):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_mock_response("Hello from agent")
    mock_get_client.return_value = mock_client

    class TestAgent(BaseAgent):
        role = "po"

    agent = TestAgent()
    result = agent.run("test prompt")
    assert result == "Hello from agent"
    mock_client.messages.create.assert_called_once()


@patch("agents.base._get_client")
def test_po_agent_populates_task_spec(mock_get_client):
    from agents.po import POAgent

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_mock_response("## User Stories\n- Story 1")
    mock_get_client.return_value = mock_client

    state = ProjectState(raw_task="Build a todo app")
    agent = POAgent()
    result_state = agent.process(state)

    assert "Story 1" in result_state.task_spec.content


@patch("agents.base._get_client")
def test_prompt_cache_control_set(mock_get_client):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_mock_response("ok")
    mock_get_client.return_value = mock_client

    class TestAgent(BaseAgent):
        role = "po"

    TestAgent().run("hello")

    call_kwargs = mock_client.messages.create.call_args.kwargs
    system = call_kwargs["system"]
    assert system[0]["cache_control"] == {"type": "ephemeral"}
