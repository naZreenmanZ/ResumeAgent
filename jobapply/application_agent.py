from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from sqlite3 import Row


@dataclass(frozen=True)
class ApplicationPlan:
    job_id: str
    portal: str
    title: str
    company: str
    url: str
    resume_path: Path
    upload_resume_path: Path
    mode: str
    final_submit_allowed: bool

    def summary(self) -> str:
        submit_state = "full-auto submit allowed" if self.final_submit_allowed else "stops before submit"
        return (
            f"{self.job_id[:8]} | {self.portal} | {self.title} | {self.company} | "
            f"{submit_state} | {self.upload_resume_path}"
        )


def build_application_plan(
    job: Row,
    resume_path: Path,
    upload_resume_path: Path,
    mode: str,
) -> ApplicationPlan:
    final_submit_allowed = mode == "full_auto"
    return ApplicationPlan(
        job_id=str(job["fingerprint"]),
        portal=str(job["portal"]),
        title=str(job["title"]),
        company=str(job["company"]),
        url=str(job["url"]),
        resume_path=resume_path,
        upload_resume_path=upload_resume_path,
        mode=mode,
        final_submit_allowed=final_submit_allowed,
    )


def write_application_plan(plan: ApplicationPlan, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"apply-plan-{plan.job_id[:8]}.md"
    path.write_text(
        "\n".join(
            [
                f"# Application Plan: {plan.title}",
                "",
                f"- Portal: {plan.portal}",
                f"- Company: {plan.company}",
                f"- Job URL: {plan.url}",
                f"- Tailored draft: {plan.resume_path}",
                f"- Upload resume PDF: {plan.upload_resume_path}",
                f"- Mode: {plan.mode}",
                f"- Final submit allowed: {plan.final_submit_allowed}",
                "",
                "## Steps",
                "",
                "1. Open the job URL in the portal account session.",
                "2. Confirm this job has not already been applied to.",
                "3. Upload or attach the tailored resume.",
                "4. Fill required profile fields from saved account details.",
                "5. Stop for review unless this portal is explicitly set to full_auto.",
            ]
        ),
        encoding="utf-8",
    )
    return path
