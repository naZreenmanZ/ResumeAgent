from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from jobapply.api import app
from jobapply.config import load_config
from jobapply.db import JobStore
from jobapply.models import Job


class ApiTest(unittest.TestCase):
    def test_health(self) -> None:
        client = TestClient(app)

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_queue_returns_jobs_without_private_resume_content(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            config_path = write_config(tmp_path)
            config = load_config(config_path)
            store = JobStore(config.database_path)
            try:
                job = sample_job()
                store.upsert_job(job, 80, ["Python", "API"], [], "queued")
            finally:
                store.close()

            client = TestClient(app)
            response = client.get("/queue", params={"config_path": str(config_path)})

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["jobs"][0]["title"], "Backend Engineer")
            self.assertNotIn("description", payload["jobs"][0])
            self.assertNotIn("resume", str(payload["jobs"][0]).lower())

    def test_scan_returns_setup_warning_as_structured_data(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            config_path = write_config(
                tmp_path,
                portal_block=(
                    '[[portals]]\n'
                    'name = "linkedin"\n'
                    "enabled = true\n"
                    'type = "setup_required"\n'
                    'method = "saved search import"\n'
                ),
            )

            client = TestClient(app)
            response = client.post("/scan", params={"config_path": str(config_path)})

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["skipped_portals"], 1)
            self.assertIsInstance(payload["warnings"], list)
            self.assertIn("linkedin", str(payload["warnings"]))

    def test_tailor_and_export_pdf_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            config_path = write_config(tmp_path)
            config = load_config(config_path)
            store = JobStore(config.database_path)
            try:
                job = sample_job()
                store.upsert_job(job, 80, ["Python", "API"], [], "queued")
            finally:
                store.close()

            client = TestClient(app)
            tailor_response = client.post(
                f"/jobs/{job.fingerprint[:8]}/tailor",
                params={"config_path": str(config_path)},
            )

            self.assertEqual(tailor_response.status_code, 200)
            draft_path = tailor_response.json()["draft_path"]
            self.assertTrue(Path(draft_path).exists())
            self.assertNotIn("Professional Summary", tailor_response.text)

            export_response = client.post("/export-pdf", json={"draft_path": draft_path})

            self.assertEqual(export_response.status_code, 200)
            pdf_path = Path(export_response.json()["pdf_path"])
            self.assertTrue(pdf_path.exists())
            self.assertGreater(pdf_path.stat().st_size, 1000)


def write_config(tmp_path: Path, portal_block: str = "") -> Path:
    base_resume = tmp_path / "base.md"
    base_resume.write_text(
        "NASREEN MANZOOR\n"
        "Dubai | nazreenmanz@example.com | +971 000000000\n"
        "PROFESSIONAL EXPERIENCE\n"
        "- Built Python APIs and React applications for production teams.\n"
        "TECHNICAL SKILLS\n"
        "Backend: Python, APIs, SQL\n"
        "CERTIFICATIONS & ACHIEVEMENTS\n"
        "- AWS Certified Cloud Practitioner\n"
        "EDUCATION\n"
        "- Master of Computer Applications (MCA) APJ Abdul Kalam University | 2018 - 2021\n"
        "LANGUAGES\n"
        "- English\n",
        encoding="utf-8",
    )
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "\n".join(
            [
                'database_path = "jobs.sqlite3"',
                f'base_resume_path = "{base_resume}"',
                f'mena_resume_path = "{base_resume}"',
                f'non_mena_resume_path = "{base_resume}"',
                'tailored_resume_dir = "tailored_resumes"',
                'tracking_dir = "tracking"',
                "",
                "[profile]",
                'target_titles = ["Backend Engineer"]',
                'target_locations = ["Dubai"]',
                'required_keywords = ["Python"]',
                'blocked_keywords = ["unpaid"]',
                "",
                portal_block,
            ]
        ),
        encoding="utf-8",
    )
    return config_path


def sample_job() -> Job:
    return Job(
        portal="demo",
        portal_id="job-1",
        title="Backend Engineer",
        company="Acme",
        location="Dubai",
        url="https://example.com/jobs/job-1",
        description="Python API role with SQL and automation.",
        requirements=["Python", "API", "SQL"],
    )


if __name__ == "__main__":
    unittest.main()
