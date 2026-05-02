"""Base agent abstract class."""

from abc import ABC, abstractmethod
from datetime import datetime

from bid_acceleration_engine.schemas.results import AgentResult, AgentStatus
from bid_acceleration_engine.utils.logging import get_logger


class BaseAgent(ABC):
    """Abstract base class for all pipeline agents."""

    def __init__(self, name: str) -> None:
        """Initialize the agent.

        Args:
            name: Agent name for logging and results.
        """
        self.name = name
        self.logger = get_logger(f"bid_acceleration_engine.agents.{name}")

    @abstractmethod
    def run(self, *args, **kwargs) -> AgentResult:
        """Run the agent.

        Agents must implement this method to define their transformation logic.
        Should return an AgentResult wrapping the output.

        Returns:
            AgentResult with status and output.
        """
        pass  # noqa: PIE790

    def _wrap_result(
        self,
        output,
        duration_seconds: float,
        error: str | None = None,
    ) -> AgentResult:
        """Wrap an agent output in an AgentResult.

        Args:
            output: The agent's output (can be any type).
            duration_seconds: How long the agent took to run.
            error: Optional error message if the agent failed.

        Returns:
            AgentResult with appropriate status.
        """
        status = AgentStatus.FAILURE if error else AgentStatus.SUCCESS
        return AgentResult(
            agent_name=self.name,
            status=status,
            output=output,
            error_message=error,
            duration_seconds=duration_seconds,
            produced_at=datetime.now(),
        )
