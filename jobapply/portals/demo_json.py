from __future__ import annotations

import json
from pathlib import Path

from jobapply.models import Job
from jobapply.portals.base import PortalAdapter


class DemoJsonPortal(PortalAdapter):
    def scan(self) -> list[Job]:
        path = Path(str(self.options["path"]))
        if not path.is_absolute():
            path = Path.cwd() / path

        raw_jobs = json.loads(path.read_text(encoding="utf-8"))
        jobs: list[Job] = []
        for item in raw_jobs:
            jobs.append(
                Job(
                    portal=str(item.get("portal") or self.name),
                    portal_id=str(item.get("portal_id", "")),
                    title=str(item["title"]),
                    company=str(item["company"]),
                    location=str(item.get("location", "")),
                    url=str(item.get("url", "")),
                    description=str(item.get("description", "")),
                    requirements=[str(value) for value in item.get("requirements", [])],
                )
            )
        return jobs
