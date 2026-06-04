from __future__ import annotations

from .base import PortalAdapter
from .browser_agent import BrowserAgentPortal
from .configured import SetupRequiredPortal
from .demo_json import DemoJsonPortal
from .feed import FeedPortal
from .saved_search_import import SavedSearchImportPortal

ADAPTERS: dict[str, type[PortalAdapter]] = {
    "browser_agent": BrowserAgentPortal,
    "demo_json": DemoJsonPortal,
    "feed": FeedPortal,
    "saved_search_import": SavedSearchImportPortal,
    "setup_required": SetupRequiredPortal,
}

__all__ = ["ADAPTERS", "PortalAdapter"]
