from __future__ import annotations

from abc import ABC, abstractmethod

from jobapply.models import Job


class PortalSetupRequired(RuntimeError):
    """Raised when a portal is selected but does not have a working adapter yet."""


class PortalAdapter(ABC):
    def __init__(self, name: str, options: dict[str, object]) -> None:
        self.name = name
        self.options = options

    @abstractmethod
    def scan(self) -> list[Job]:
        """Return jobs discovered from this portal."""
