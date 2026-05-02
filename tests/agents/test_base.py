"""Tests for BaseAgent abstract class."""

import pytest

from bid_acceleration_engine.agents.base import BaseAgent
from bid_acceleration_engine.schemas.results import AgentStatus


class EchoAgent(BaseAgent):
    """Simple test agent that echoes its input."""

    def run(self, message: str) -> dict:
        """Echo the message back.

        Args:
            message: The message to echo.

        Returns:
            Wrapped result containing the echoed message.
        """
        start = __import__("time").time()
        output = {"echoed": message}
        duration = __import__("time").time() - start
        return self._wrap_result(output, duration)


def test_base_agent_cannot_be_instantiated():
    """Test that BaseAgent cannot be instantiated directly (abstract)."""
    with pytest.raises(TypeError):
        BaseAgent("test")  # type: ignore


def test_agent_stores_name():
    """Test that agent stores its name."""
    agent = EchoAgent("echo_agent")
    assert agent.name == "echo_agent"


def test_agent_has_logger():
    """Test that agent creates a logger."""
    agent = EchoAgent("echo_agent")
    assert agent.logger is not None
    assert "echo_agent" in agent.logger.name.lower()


def test_agent_run_returns_wrapped_result():
    """Test that agent.run() returns an AgentResult."""
    agent = EchoAgent("echo_agent")
    result = agent.run("hello")

    assert result.agent_name == "echo_agent"
    assert result.status == AgentStatus.SUCCESS
    assert result.output == {"echoed": "hello"}
    assert result.duration_seconds >= 0.0


def test_wrap_result_success_state():
    """Test _wrap_result with success (no error)."""
    agent = EchoAgent("test_agent")
    result = agent._wrap_result(output="test", duration_seconds=1.5)

    assert result.agent_name == "test_agent"
    assert result.status == AgentStatus.SUCCESS
    assert result.output == "test"
    assert result.error_message is None
    assert result.duration_seconds == 1.5


def test_wrap_result_failure_state():
    """Test _wrap_result with failure (error set)."""
    agent = EchoAgent("test_agent")
    result = agent._wrap_result(
        output=None,
        duration_seconds=0.0,
        error="Something went wrong",
    )

    assert result.agent_name == "test_agent"
    assert result.status == AgentStatus.FAILURE
    assert result.output is None
    assert result.error_message == "Something went wrong"


def test_wrap_result_with_dict_output():
    """Test _wrap_result with dictionary output."""
    agent = EchoAgent("test_agent")
    output_dict = {"key": "value", "count": 42}
    result = agent._wrap_result(output=output_dict, duration_seconds=0.1)

    assert result.output == output_dict
    assert result.output["key"] == "value"
    assert result.output["count"] == 42


def test_wrap_result_sets_produced_at():
    """Test that _wrap_result sets produced_at timestamp."""
    agent = EchoAgent("test_agent")
    result = agent._wrap_result(output="test", duration_seconds=0.1)

    assert result.produced_at is not None
    from datetime import datetime
    assert isinstance(result.produced_at, datetime)


def test_multiple_agents_independent():
    """Test that multiple agent instances are independent."""
    agent1 = EchoAgent("agent_1")
    agent2 = EchoAgent("agent_2")

    result1 = agent1.run("message_1")
    result2 = agent2.run("message_2")

    assert result1.agent_name == "agent_1"
    assert result2.agent_name == "agent_2"
    assert result1.output["echoed"] == "message_1"
    assert result2.output["echoed"] == "message_2"
