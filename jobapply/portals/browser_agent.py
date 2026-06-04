from __future__ import annotations

import asyncio
from dataclasses import replace
from urllib.parse import urljoin

from jobapply.models import Job
from jobapply.portals.base import PortalAdapter, PortalSetupRequired


class BrowserAgentPortal(PortalAdapter):
    """Scan a portal with Playwright using configured selectors.

    This adapter is intentionally configurable because job portal HTML changes often.
    Portal-specific subclasses can replace it once a site needs special login,
    pagination, or apply behavior.
    """

    def scan(self) -> list[Job]:
        search_url = str(self.options.get("search_url", "")).strip()
        if not search_url:
            raise PortalSetupRequired(f"{self.name} needs search_url for browser scanning.")

        required_selectors = ["job_card_selector", "title_selector", "company_selector"]
        missing = [key for key in required_selectors if not str(self.options.get(key, "")).strip()]
        if missing:
            raise PortalSetupRequired(
                f"{self.name} browser scan needs selectors: {', '.join(missing)}."
            )

        return asyncio.run(self._scan_with_playwright(search_url))

    async def _scan_with_playwright(self, search_url: str) -> list[Job]:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise PortalSetupRequired(
                "Browser scanning needs Playwright. Install with: "
                "python3 -m pip install playwright && python3 -m playwright install chromium"
            ) from exc

        headless = bool(self.options.get("headless", False))
        max_jobs = int(self.options.get("max_jobs", 25))
        card_selector = str(self.options["job_card_selector"])

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=headless)
            page = await browser.new_page()
            await page.goto(search_url, wait_until="domcontentloaded")
            await page.wait_for_selector(card_selector, timeout=30000)
            cards = await page.query_selector_all(card_selector)

            jobs: list[Job] = []
            for card in cards[:max_jobs]:
                job = await self._job_from_card(card)
                if job is not None:
                    jobs.append(job)

            if bool(self.options.get("fetch_detail_descriptions", False)):
                jobs = await self._with_detail_descriptions(page, jobs)

            await browser.close()
            return jobs

    async def _with_detail_descriptions(self, page: object, jobs: list[Job]) -> list[Job]:
        selector = str(self.options.get("detail_description_selector", "main"))
        enriched: list[Job] = []
        for job in jobs:
            if not job.url:
                enriched.append(job)
                continue
            try:
                await page.goto(job.url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_selector(selector, timeout=15000)
                detail_text = await text_from_selector(page, selector)
                enriched.append(replace(job, description=detail_text[:12000]))
            except Exception:
                enriched.append(job)
        return enriched

    async def _job_from_card(self, card: object) -> Job | None:
        title = await text_from_selector(card, str(self.options["title_selector"]))
        company = await text_from_selector(card, str(self.options["company_selector"]))
        if not title or not company:
            return None

        location = await text_from_selector(card, str(self.options.get("location_selector", "")))
        description = await text_from_selector(card, str(self.options.get("description_selector", "")))
        url = await href_from_selector(card, str(self.options.get("url_selector", "")))
        base_url = str(self.options.get("base_url", "")).strip()
        if base_url and url:
            url = urljoin(base_url, url)
        portal_id = url or f"{title}:{company}:{location}"

        return Job(
            portal=self.name,
            portal_id=portal_id,
            title=title,
            company=company,
            location=location,
            url=url,
            description=description,
            requirements=[],
        )


async def text_from_selector(root: object, selector: str) -> str:
    if not selector:
        return ""
    element = await root.query_selector(selector)
    if element is None:
        return ""
    text = await element.inner_text()
    return text.strip()


async def href_from_selector(root: object, selector: str) -> str:
    if not selector:
        return ""
    element = await root.query_selector(selector)
    if element is None:
        return ""
    href = await element.get_attribute("href")
    return (href or "").strip()
