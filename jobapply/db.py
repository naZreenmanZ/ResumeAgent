from __future__ import annotations

from pathlib import Path
import sqlite3

from .models import Job, now_iso


SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    fingerprint TEXT PRIMARY KEY,
    portal TEXT NOT NULL,
    portal_id TEXT NOT NULL,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT NOT NULL,
    discovered_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    score INTEGER NOT NULL DEFAULT 0,
    matched_keywords TEXT NOT NULL DEFAULT '',
    blocked_keywords TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_fingerprint TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    portal_ref TEXT NOT NULL,
    resume_path TEXT,
    applied_at TEXT NOT NULL,
    FOREIGN KEY(job_fingerprint) REFERENCES jobs(fingerprint)
);
"""


class JobStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(SCHEMA)

    def close(self) -> None:
        self.connection.close()

    def upsert_job(
        self,
        job: Job,
        score: int,
        matched_keywords: list[str],
        blocked_keywords: list[str],
        status: str,
    ) -> bool:
        existing = self.connection.execute(
            "SELECT fingerprint, status FROM jobs WHERE fingerprint = ?",
            (job.fingerprint,),
        ).fetchone()
        if existing:
            preserved_status = str(existing["status"])
            next_status = preserved_status
            if preserved_status in {"new", "queued", "rejected"}:
                next_status = status
            self.connection.execute(
                """
                UPDATE jobs
                SET title = ?, company = ?, location = ?, url = ?, description = ?,
                    requirements = ?, score = ?, matched_keywords = ?,
                    blocked_keywords = ?, status = ?
                WHERE fingerprint = ?
                """,
                (
                    job.title,
                    job.company,
                    job.location,
                    job.url,
                    job.description,
                    "\n".join(job.requirements),
                    score,
                    ", ".join(matched_keywords),
                    ", ".join(blocked_keywords),
                    next_status,
                    job.fingerprint,
                ),
            )
            self.connection.commit()
            return False

        self.connection.execute(
            """
            INSERT INTO jobs (
                fingerprint, portal, portal_id, title, company, location, url,
                description, requirements, discovered_at, status, score,
                matched_keywords, blocked_keywords
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job.fingerprint,
                job.portal,
                job.portal_id,
                job.title,
                job.company,
                job.location,
                job.url,
                job.description,
                "\n".join(job.requirements),
                job.discovered_at,
                status,
                score,
                ", ".join(matched_keywords),
                ", ".join(blocked_keywords),
            ),
        )
        self.connection.commit()
        return True

    def queued_jobs(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT * FROM jobs
            WHERE status IN ('queued', 'tailored')
            AND fingerprint NOT IN (SELECT job_fingerprint FROM applications)
            ORDER BY score DESC, discovered_at DESC
            """
        ).fetchall()

    def get_job(self, fingerprint: str) -> sqlite3.Row | None:
        return self.connection.execute(
            "SELECT * FROM jobs WHERE fingerprint = ?",
            (fingerprint,),
        ).fetchone()

    def set_job_status(self, fingerprint: str, status: str) -> None:
        self.connection.execute(
            "UPDATE jobs SET status = ? WHERE fingerprint = ?",
            (status, fingerprint),
        )
        self.connection.commit()

    def mark_applied(self, fingerprint: str, portal_ref: str, resume_path: str | None) -> None:
        self.connection.execute(
            """
            INSERT INTO applications (job_fingerprint, status, portal_ref, resume_path, applied_at)
            VALUES (?, 'applied', ?, ?, ?)
            ON CONFLICT(job_fingerprint) DO UPDATE SET
                status = excluded.status,
                portal_ref = excluded.portal_ref,
                resume_path = excluded.resume_path,
                applied_at = excluded.applied_at
            """,
            (fingerprint, portal_ref, resume_path, now_iso()),
        )
        self.connection.execute(
            "UPDATE jobs SET status = 'applied' WHERE fingerprint = ?",
            (fingerprint,),
        )
        self.connection.commit()
