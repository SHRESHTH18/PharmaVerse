# agents/base_agent.py

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Abstract base class for all Worker Agents."""

    def __init__(self, base_url: str) -> None:
        # Base URL of the mock API server
        self.base_url = base_url.rstrip("/")

    @property
    @abstractmethod
    def name(self) -> str:
        """Human readable name for the agent."""
        raise NotImplementedError

    @abstractmethod
    def run(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute this agent's main function.

        kwargs will be different per agent (molecule, indication, etc.).
        """
        raise NotImplementedError