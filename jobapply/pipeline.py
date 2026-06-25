from __future__ import annotations

from .config import AppConfig
from .db import JobStore
from .portals import ADAPTERS
from .portals.base import PortalSetupRequired
from .scoring import score_job


def scan_enabled_portals(config: AppConfig, store: JobStore) -> dict[str, object]:
    stats: dict[str, object] = {
        "seen": 0,
        "inserted": 0,
        "queued": 0,
        "blocked": 0,
        "skipped_portals": 0,
        "warnings": [],
    }

    for portal in config.portals:
        if not portal.enabled:
            continue
        adapter_type = ADAPTERS.get(portal.type)
        if adapter_type is None:
            raise ValueError(f"Unknown portal adapter type: {portal.type}")

        adapter = adapter_type(portal.name, portal.options)
        try:
            jobs = adapter.scan()
        except PortalSetupRequired as exc:
            record_portal_warning(stats, str(exc))
            continue
        except Exception as exc:
            record_portal_warning(
                stats,
                f"{portal.name} scan failed ({type(exc).__name__}): {exc}",
            )
            continue

        for job in jobs:
            stats["seen"] = int(stats["seen"]) + 1
            scored = score_job(job, config.profile)
            status = "queued" if scored.should_queue else "rejected"
            if scored.blocked_keywords:
                stats["blocked"] = int(stats["blocked"]) + 1
            if scored.should_queue:
                stats["queued"] = int(stats["queued"]) + 1
            inserted = store.upsert_job(
                scored.job,
                scored.score,
                scored.matched_keywords,
                scored.blocked_keywords,
                status,
            )
            if inserted:
                stats["inserted"] = int(stats["inserted"]) + 1

    return stats


def record_portal_warning(stats: dict[str, object], message: str) -> None:
    stats["skipped_portals"] = int(stats["skipped_portals"]) + 1
    warnings = stats["warnings"]
    if isinstance(warnings, list):
        warnings.append(message)
