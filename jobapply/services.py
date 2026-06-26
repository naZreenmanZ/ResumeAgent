from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from sqlite3 import Row
from typing import Iterator

from .application_agent import build_application_plan, write_application_plan
from .config import AppConfig, load_config
from .db import JobStore
from .pdf_export import export_tailored_pdf
from .pipeline import scan_enabled_portals
from .resume import select_resume_path, tailor_resume
from .tracker import application_rows, export_application_tracker


class ServiceError(Exception):
    status_code = 400


class JobNotFound(ServiceError):
    status_code = 404


class AmbiguousJobId(ServiceError):
    status_code = 409


@contextmanager
def open_store(config: AppConfig) -> Iterator[JobStore]:
    store = JobStore(config.database_path)
    try:
        yield store
    finally:
        store.close()


def load_app_config(config_path: str | Path = "config.toml") -> AppConfig:
    return load_config(config_path)


def ensure_runtime_dirs(config: AppConfig) -> None:
    config.base_resume_dir.mkdir(parents=True, exist_ok=True)
    config.tailored_resume_dir.mkdir(parents=True, exist_ok=True)
    config.tracking_dir.mkdir(parents=True, exist_ok=True)


def resolve_job_id(store: JobStore, value: str) -> str:
    rows = store.connection.execute(
        "SELECT fingerprint FROM jobs WHERE fingerprint LIKE ?",
        (f"{value}%",),
    ).fetchall()
    if not rows:
        raise JobNotFound(f"No job found for id prefix: {value}")
    if len(rows) > 1:
        raise AmbiguousJobId(f"Job id prefix is ambiguous: {value}")
    return str(rows[0]["fingerprint"])


def config_summary(config_path: str | Path = "config.toml") -> dict[str, object]:
    config = load_app_config(config_path)
    return {
        "database_path": str(config.database_path),
        "base_resume_dir": str(config.base_resume_dir),
        "tailored_resume_dir": str(config.tailored_resume_dir),
        "tracking_dir": str(config.tracking_dir),
        "resumes": {
            "mena_configured": config.mena_resume_path.exists(),
            "non_mena_configured": config.non_mena_resume_path.exists(),
        },
        "profile": {
            "target_titles": config.profile.target_titles,
            "target_locations": config.profile.target_locations,
            "required_keywords": config.profile.required_keywords,
            "blocked_keywords": config.profile.blocked_keywords,
        },
        "portals": [
            {
                "name": portal.name,
                "enabled": portal.enabled,
                "type": portal.type,
                "method": str(portal.options.get("method", portal.type)),
                "notes": str(portal.options.get("notes", "")),
            }
            for portal in config.portals
        ],
    }


def scan(config_path: str | Path = "config.toml") -> dict[str, object]:
    config = load_app_config(config_path)
    with open_store(config) as store:
        return scan_enabled_portals(config, store)


def queued_jobs(config_path: str | Path = "config.toml") -> list[dict[str, object]]:
    config = load_app_config(config_path)
    with open_store(config) as store:
        return [job_summary(row) for row in store.queued_jobs()]


def job_detail(config_path: str | Path, job_id: str) -> dict[str, object]:
    config = load_app_config(config_path)
    with open_store(config) as store:
        fingerprint = resolve_job_id(store, job_id)
        row = store.get_job(fingerprint)
        if row is None:
            raise JobNotFound(f"No job found: {job_id}")
        return job_summary(row, include_detail=True)


def tailor_job(config_path: str | Path, job_id: str) -> dict[str, object]:
    config = load_app_config(config_path)
    ensure_runtime_dirs(config)
    with open_store(config) as store:
        fingerprint = resolve_job_id(store, job_id)
        row = store.get_job(fingerprint)
        if row is None:
            raise JobNotFound(f"No job found: {job_id}")
        source_resume_path = select_resume_path(config, row)
        draft_path = tailor_resume(source_resume_path, config.tailored_resume_dir, row)
        store.set_job_status(fingerprint, "tailored")
        return {
            "job_id": fingerprint,
            "status": "tailored",
            "draft_path": str(draft_path),
            "source_resume_type": "mena" if source_resume_path == config.mena_resume_path else "non_mena",
        }


def export_pdf(draft_path: str | Path) -> dict[str, object]:
    output_path = export_tailored_pdf(Path(draft_path))
    return {"draft_path": str(draft_path), "pdf_path": str(output_path)}


def create_application_plan(
    config_path: str | Path,
    job_id: str,
    mode: str = "review_before_submit",
) -> dict[str, object]:
    config = load_app_config(config_path)
    ensure_runtime_dirs(config)
    with open_store(config) as store:
        fingerprint = resolve_job_id(store, job_id)
        resume_path, upload_resume_path, plan_path = prepare_application_assets(
            config,
            store,
            fingerprint,
            mode,
        )
        row = store.get_job(fingerprint)
        if row is None:
            raise JobNotFound(f"No job found after tailoring: {job_id}")
        plan = build_application_plan(row, resume_path, upload_resume_path, mode)
        return {
            "job_id": fingerprint,
            "mode": mode,
            "final_submit_allowed": plan.final_submit_allowed,
            "draft_path": str(resume_path),
            "pdf_path": str(upload_resume_path),
            "plan_path": str(plan_path),
            "summary": plan.summary(),
        }


def prepare_application_assets(
    config: AppConfig,
    store: JobStore,
    fingerprint: str,
    mode: str,
) -> tuple[Path, Path, Path]:
    row = store.get_job(fingerprint)
    if row is None:
        raise JobNotFound(f"No job found: {fingerprint}")
    source_resume_path = select_resume_path(config, row)
    resume_path = tailor_resume(source_resume_path, config.tailored_resume_dir, row)
    upload_resume_path = export_tailored_pdf(resume_path)
    store.set_job_status(fingerprint, "tailored")
    plan = build_application_plan(row, resume_path, upload_resume_path, mode)
    plan_path = write_application_plan(plan, config.tailored_resume_dir)
    return resume_path, upload_resume_path, plan_path


def mark_applied(
    config_path: str | Path,
    job_id: str,
    portal_ref: str,
    resume_path: str | None = None,
) -> dict[str, object]:
    config = load_app_config(config_path)
    with open_store(config) as store:
        fingerprint = resolve_job_id(store, job_id)
        store.mark_applied(fingerprint, portal_ref, resume_path)
        csv_path, xlsx_path = export_application_tracker(store, config.tracking_dir)
        return {
            "job_id": fingerprint,
            "status": "applied",
            "portal_ref": portal_ref,
            "resume_path": resume_path,
            "tracker": {
                "csv_path": str(csv_path),
                "xlsx_path": str(xlsx_path),
            },
        }


def tracker_summary(config_path: str | Path = "config.toml") -> dict[str, object]:
    config = load_app_config(config_path)
    with open_store(config) as store:
        rows = application_rows(store)
    return {
        "count": len(rows),
        "rows": rows,
        "csv_path": str(config.tracking_dir / "applications.csv"),
        "xlsx_path": str(config.tracking_dir / "applications.xlsx"),
    }


def job_summary(row: Row, include_detail: bool = False) -> dict[str, object]:
    summary: dict[str, object] = {
        "id": str(row["fingerprint"]),
        "portal": str(row["portal"]),
        "portal_id": str(row["portal_id"]),
        "title": str(row["title"]),
        "company": str(row["company"]),
        "location": str(row["location"]),
        "url": str(row["url"]),
        "discovered_at": str(row["discovered_at"]),
        "status": str(row["status"]),
        "score": int(row["score"]),
        "matched_keywords": split_csv(str(row["matched_keywords"])),
        "blocked_keywords": split_csv(str(row["blocked_keywords"])),
    }
    if include_detail:
        summary["description"] = str(row["description"])
        summary["requirements"] = [
            item.strip() for item in str(row["requirements"]).splitlines() if item.strip()
        ]
    return summary


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]
