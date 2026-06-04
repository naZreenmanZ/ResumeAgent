from __future__ import annotations

import csv
import json
from pathlib import Path

from jobapply.models import Job
from jobapply.portals.base import PortalAdapter, PortalSetupRequired


class SavedSearchImportPortal(PortalAdapter):
    """Read jobs from a portal export file.

    Supported formats:
    - CSV with headers
    - JSON list of job objects
    """

    def scan(self) -> list[Job]:
        path = Path(str(self.options.get("path", "")))
        if not path:
            raise PortalSetupRequired(f"{self.name} needs a saved-search import path.")
        if not path.exists():
            raise PortalSetupRequired(f"{self.name} import file does not exist yet: {path}")

        if path.suffix.lower() == ".json":
            return self._scan_json(path)
        return self._scan_csv(path)

    def _scan_json(self, path: Path) -> list[Job]:
        raw_jobs = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw_jobs, list):
            raise ValueError(f"{path} must contain a JSON list of jobs.")
        return [self._job_from_mapping(item) for item in raw_jobs]

    def _scan_csv(self, path: Path) -> list[Job]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [self._job_from_mapping(row) for row in csv.DictReader(handle)]

    def _job_from_mapping(self, item: dict[str, object]) -> Job:
        normalized = {key.strip().lower().replace(" ", "_"): value for key, value in item.items()}

        title = first_value(normalized, "title", "job_title", "position", "role")
        company = first_value(normalized, "company", "company_name", "employer", "organization")
        location = first_value(normalized, "location", "job_location", "city", "country")
        url = first_value(normalized, "url", "job_url", "link", "apply_url")
        description = first_value(normalized, "description", "summary", "job_description")
        portal_id = first_value(normalized, "portal_id", "job_id", "id", "external_id")
        requirements = split_requirements(
            first_value(normalized, "requirements", "skills", "keywords", default="")
        )

        if not title or not company:
            raise ValueError(f"{self.name} import row needs at least title and company.")

        if not portal_id:
            portal_id = url

        return Job(
            portal=self.name,
            portal_id=portal_id,
            title=title,
            company=company,
            location=location,
            url=url,
            description=description,
            requirements=requirements,
        )


def first_value(mapping: dict[str, object], *keys: str, default: str = "") -> str:
    for key in keys:
        value = mapping.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


def split_requirements(value: str) -> list[str]:
    if not value:
        return []
    separators = [";", "|", "\n"]
    parts = [value]
    for separator in separators:
        if separator in value:
            parts = value.split(separator)
            break
    return [part.strip() for part in parts if part.strip()]
