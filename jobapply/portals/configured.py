from __future__ import annotations

from jobapply.models import Job
from jobapply.portals.base import PortalAdapter, PortalSetupRequired


class SetupRequiredPortal(PortalAdapter):
    def scan(self) -> list[Job]:
        method = str(self.options.get("method", "not configured"))
        raise PortalSetupRequired(
            f"{self.name} is selected, but its adapter is not implemented yet "
            f"(configured method: {method})."
        )
