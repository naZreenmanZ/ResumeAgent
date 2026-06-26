from __future__ import annotations

from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from . import services


app = FastAPI(
    title="ResumeAgent API",
    version="0.1.0",
    description="Local API for the ResumeAgent engine.",
)


class ExportPdfRequest(BaseModel):
    draft_path: str


class PlanRequest(BaseModel):
    mode: Literal["review_before_submit", "full_auto"] = "review_before_submit"


class MarkAppliedRequest(BaseModel):
    portal_ref: str
    resume_path: Optional[str] = None


def handle_service_error(exc: services.ServiceError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=str(exc))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "resume-agent-api"}


@app.get("/config")
def get_config_summary(config_path: str = Query("config.toml")) -> dict[str, object]:
    try:
        return services.config_summary(config_path)
    except services.ServiceError as exc:
        raise handle_service_error(exc) from exc


@app.post("/scan")
def scan(config_path: str = Query("config.toml")) -> dict[str, object]:
    try:
        return services.scan(config_path)
    except services.ServiceError as exc:
        raise handle_service_error(exc) from exc


@app.get("/queue")
def queue(config_path: str = Query("config.toml")) -> dict[str, object]:
    try:
        rows = services.queued_jobs(config_path)
    except services.ServiceError as exc:
        raise handle_service_error(exc) from exc
    return {"count": len(rows), "jobs": rows}


@app.get("/jobs/{job_id}")
def job_detail(job_id: str, config_path: str = Query("config.toml")) -> dict[str, object]:
    try:
        return services.job_detail(config_path, job_id)
    except services.ServiceError as exc:
        raise handle_service_error(exc) from exc


@app.post("/jobs/{job_id}/tailor")
def tailor_job(job_id: str, config_path: str = Query("config.toml")) -> dict[str, object]:
    try:
        return services.tailor_job(config_path, job_id)
    except services.ServiceError as exc:
        raise handle_service_error(exc) from exc


@app.post("/export-pdf")
def export_pdf(request: ExportPdfRequest) -> dict[str, object]:
    try:
        return services.export_pdf(request.draft_path)
    except services.ServiceError as exc:
        raise handle_service_error(exc) from exc


@app.post("/jobs/{job_id}/plan")
def create_application_plan(
    job_id: str,
    request: PlanRequest,
    config_path: str = Query("config.toml"),
) -> dict[str, object]:
    try:
        return services.create_application_plan(config_path, job_id, request.mode)
    except services.ServiceError as exc:
        raise handle_service_error(exc) from exc


@app.post("/jobs/{job_id}/mark-applied")
def mark_applied(
    job_id: str,
    request: MarkAppliedRequest,
    config_path: str = Query("config.toml"),
) -> dict[str, object]:
    try:
        return services.mark_applied(
            config_path,
            job_id,
            request.portal_ref,
            request.resume_path,
        )
    except services.ServiceError as exc:
        raise handle_service_error(exc) from exc


@app.get("/tracker/summary")
def tracker_summary(config_path: str = Query("config.toml")) -> dict[str, object]:
    try:
        return services.tracker_summary(config_path)
    except services.ServiceError as exc:
        raise handle_service_error(exc) from exc
