from __future__ import annotations

from email.utils import parsedate_to_datetime
import json
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from jobapply.models import Job
from jobapply.portals.base import PortalAdapter, PortalSetupRequired
from jobapply.portals.saved_search_import import first_value, split_requirements


class FeedPortal(PortalAdapter):
    """Read jobs from an RSS, Atom, or JSON feed URL."""

    def scan(self) -> list[Job]:
        url = str(self.options.get("url", "")).strip()
        if not url:
            raise PortalSetupRequired(f"{self.name} needs a feed url.")

        request = Request(url, headers={"User-Agent": "resume-automation/0.1"})
        with urlopen(request, timeout=20) as response:
            content_type = response.headers.get("content-type", "")
            body = response.read()

        if "json" in content_type or url.lower().endswith(".json"):
            return self._scan_json(body)
        return self._scan_xml(body)

    def _scan_json(self, body: bytes) -> list[Job]:
        payload = json.loads(body.decode("utf-8"))
        items = payload.get("jobs", payload.get("items", payload)) if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            raise ValueError(f"{self.name} JSON feed must contain a list, jobs, or items.")
        return [self._job_from_mapping(item) for item in items]

    def _scan_xml(self, body: bytes) -> list[Job]:
        root = ET.fromstring(body)
        entries = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
        jobs: list[Job] = []
        for entry in entries:
            title = text_at(entry, "title")
            link = text_at(entry, "link")
            if not link:
                link = attr_at(entry, "{http://www.w3.org/2005/Atom}link", "href")
            description = text_at(entry, "description") or text_at(entry, "summary")
            company = text_at(entry, "company") or str(self.options.get("default_company", "Unknown"))
            location = text_at(entry, "location") or str(self.options.get("default_location", ""))
            portal_id = text_at(entry, "guid") or text_at(entry, "id") or link
            requirements = split_requirements(text_at(entry, "category"))
            if title:
                jobs.append(
                    Job(
                        portal=self.name,
                        portal_id=portal_id,
                        title=title,
                        company=company,
                        location=location,
                        url=link,
                        description=description,
                        requirements=requirements,
                        discovered_at=parse_date(text_at(entry, "pubDate") or text_at(entry, "updated")),
                    )
                )
        return jobs

    def _job_from_mapping(self, item: dict[str, object]) -> Job:
        normalized = {key.strip().lower().replace(" ", "_"): value for key, value in item.items()}
        title = first_value(normalized, "title", "job_title", "position", "role")
        company = first_value(normalized, "company", "company_name", "employer", default="Unknown")
        location = first_value(normalized, "location", "job_location", "city", "country")
        url = first_value(normalized, "url", "job_url", "link", "apply_url")
        description = first_value(normalized, "description", "summary", "job_description")
        portal_id = first_value(normalized, "portal_id", "job_id", "id", "external_id", default=url)
        requirements = split_requirements(
            first_value(normalized, "requirements", "skills", "keywords", default="")
        )
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


def text_at(entry: ET.Element, name: str) -> str:
    element = entry.find(name)
    if element is None:
        element = entry.find(f"{{http://www.w3.org/2005/Atom}}{name}")
    return (element.text or "").strip() if element is not None else ""


def attr_at(entry: ET.Element, name: str, attr: str) -> str:
    element = entry.find(name)
    return element.attrib.get(attr, "").strip() if element is not None else ""


def parse_date(value: str) -> str:
    if not value:
        from jobapply.models import now_iso

        return now_iso()
    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError):
        return value
