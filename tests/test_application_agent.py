from pathlib import Path
import tempfile
import unittest

from jobapply.application_agent import build_application_plan, write_application_plan
from jobapply.db import JobStore
from jobapply.models import Job


class ApplicationAgentTest(unittest.TestCase):
    def test_plan_defaults_to_stop_before_submit(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            store = JobStore(tmp_path / "jobs.sqlite3")
            job = Job(
                portal="linkedin",
                portal_id="job-1",
                title="Backend Engineer",
                company="Acme",
                location="Dubai",
                url="https://example.com/job",
                description="Python APIs",
            )
            store.upsert_job(job, 50, ["Python"], [], "queued")
            row = store.get_job(job.fingerprint)
            self.assertIsNotNone(row)

            plan = build_application_plan(
                row,
                tmp_path / "resume.md",
                tmp_path / "resume.pdf",
                "review_before_submit",
            )
            output = write_application_plan(plan, tmp_path)

            self.assertFalse(plan.final_submit_allowed)
            self.assertTrue(output.exists())
            self.assertEqual(plan.upload_resume_path, tmp_path / "resume.pdf")
            self.assertIn("Stop for review", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
