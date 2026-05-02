"""Tests for AgentResult and AgentStatus."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from bid_acceleration_engine.schemas.results import AgentResult, AgentStatus


def test_agent_result_success_state():
    """Test AgentResult in SUCCESS state with output."""
    now = datetime.now(UTC)
    result = AgentResult[str](
        agent_name="test_agent",
        status=AgentStatus.SUCCESS,
        output="hello",
        duration_seconds=1.5,
        produced_at=now,
    )

    assert result.agent_name == "test_agent"
    assert result.status == AgentStatus.SUCCESS
    assert result.output == "hello"
    assert result.error_message is None
    assert result.duration_seconds == 1.5
    assert result.produced_at == now


def test_agent_result_failure_state():
    """Test AgentResult in FAILURE state with error message."""
    now = datetime.now(UTC)
    result = AgentResult[str](
        agent_name="test_agent",
        status=AgentStatus.FAILURE,
        output=None,
        error_message="Something went wrong",
        duration_seconds=0.0,
        produced_at=now,
    )

    assert result.agent_name == "test_agent"
    assert result.status == AgentStatus.FAILURE
    assert result.output is None
    assert result.error_message == "Something went wrong"
    assert result.duration_seconds == 0.0


def test_agent_result_model_dump():
    """Test AgentResult serialization via model_dump."""
    now = datetime.now(UTC)
    result = AgentResult[str](
        agent_name="test_agent",
        status=AgentStatus.SUCCESS,
        output="test_output",
        duration_seconds=2.5,
        produced_at=now,
    )

    dumped = result.model_dump()
    assert dumped["agent_name"] == "test_agent"
    assert dumped["status"] == "success"
    assert dumped["output"] == "test_output"
    assert dumped["duration_seconds"] == 2.5
    assert isinstance(dumped["produced_at"], datetime)


def test_agent_result_json_mode():
    """Test AgentResult serialization in JSON mode."""
    now = datetime.now(UTC)
    result = AgentResult[int](
        agent_name="math_agent",
        status=AgentStatus.SUCCESS,
        output=42,
        duration_seconds=0.1,
        produced_at=now,
    )

    dumped = result.model_dump(mode="json")
    assert dumped["agent_name"] == "math_agent"
    assert dumped["status"] == "success"
    assert dumped["output"] == 42
    assert isinstance(dumped["produced_at"], str)  # ISO 8601 string in JSON mode


def test_agent_result_rejects_extra_fields():
    """Test that AgentResult forbids extra fields (extra='forbid')."""
    with pytest.raises(ValidationError) as exc_info:
        AgentResult[str](
            agent_name="test",
            status=AgentStatus.SUCCESS,
            output="test",
            duration_seconds=1.0,
            produced_at=datetime.now(UTC),
            extra_field="not allowed",  # This should raise
        )

    assert "extra_forbidden" in str(exc_info.value).lower()


def test_agent_status_enum():
    """Test AgentStatus enum values."""
    assert AgentStatus.SUCCESS.value == "success"
    assert AgentStatus.FAILURE.value == "failure"
    assert AgentStatus.SKIPPED.value == "skipped"


def test_agent_result_with_dict_output():
    """Test AgentResult with dict-like output (via Generic[T])."""
    result = AgentResult[dict](
        agent_name="dict_agent",
        status=AgentStatus.SUCCESS,
        output={"key": "value", "count": 123},
        duration_seconds=1.0,
        produced_at=datetime.now(UTC),
    )

    assert result.output == {"key": "value", "count": 123}
    assert result.output["key"] == "value"
