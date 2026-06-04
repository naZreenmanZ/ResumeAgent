from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import re


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_text(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
    return re.sub(r"\s+", " ", normalized)


@dataclass(frozen=True)
class Job:
    portal: str
    portal_id: str
    title: str
    company: str
    location: str
    url: str
    description: str
    requirements: list[str] = field(default_factory=list)
    discovered_at: str = field(default_factory=now_iso)

    @property
    def fingerprint(self) -> str:
        stable_id = self.portal_id.strip()
        if stable_id:
            raw = f"{self.portal}:{stable_id}"
        else:
            raw = ":".join(
                [
                    self.portal,
                    normalize_text(self.title),
                    normalize_text(self.company),
                    normalize_text(self.location),
                ]
            )
        return sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ScoredJob:
    job: Job
    score: int
    matched_keywords: list[str]
    blocked_keywords: list[str]

    @property
    def should_queue(self) -> bool:
        return self.score > 0 and not self.blocked_keywords
