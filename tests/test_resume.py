from pathlib import Path
import tempfile
import unittest

from jobapply.config import AppConfig, ProfileConfig
from jobapply.db import JobStore
from jobapply.models import Job
from jobapply.resume import select_resume_path, tailor_resume


class ResumeTest(unittest.TestCase):
    def test_tailor_resume_creates_reviewable_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            store = JobStore(tmp_path / "jobs.sqlite3")
            job = Job(
                portal="demo",
                portal_id="job-1",
                title="Backend Python Engineer",
                company="Acme",
                location="Remote",
                url="https://example.com",
                description="Python API automation role.",
                requirements=["Python", "API", "SQL"],
            )
            store.upsert_job(job, 50, ["Python", "API"], [], "queued")
            row = store.get_job(job.fingerprint)
            self.assertIsNotNone(row)

            base = tmp_path / "base.md"
            base.write_text("# Candidate\n\nPython engineer.", encoding="utf-8")

            output = tailor_resume(base, tmp_path / "generated", row)

            self.assertTrue(output.exists())
            content = output.read_text(encoding="utf-8")
            self.assertIn("Professional Summary", content)
            self.assertIn("Technical Skills", content)
            self.assertIn("**Backend:**", content)
            self.assertIn("Professional Experience", content)
            self.assertIn("Certifications & Achievements", content)
            self.assertIn("Languages", content)
            visible_content = "\n".join(
                line for line in content.splitlines() if not line.startswith("<!--")
            )
            self.assertNotIn("Targeted Summary", visible_content)
            self.assertNotIn("Base Resume Content", visible_content)
            self.assertNotIn("Job URL", visible_content)

    def test_selects_mena_resume_for_dubai_job(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            store = JobStore(tmp_path / "jobs.sqlite3")
            job = Job(
                portal="gulftalent",
                portal_id="job-2",
                title="Engineer",
                company="Acme",
                location="Dubai",
                url="https://example.com/uae/jobs/engineer",
                description="Python",
            )
            store.upsert_job(job, 50, ["Python"], [], "queued")
            row = store.get_job(job.fingerprint)
            self.assertIsNotNone(row)
            config = AppConfig(
                database_path=tmp_path / "jobs.sqlite3",
                base_resume_path=tmp_path / "base.md",
                mena_resume_path=tmp_path / "photo.pdf",
                non_mena_resume_path=tmp_path / "np.pdf",
                output_dir=tmp_path / "generated",
                profile=ProfileConfig(),
                portals=[],
            )

            self.assertEqual(select_resume_path(config, row), tmp_path / "photo.pdf")

    def test_selects_np_resume_for_non_mena_job(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            store = JobStore(tmp_path / "jobs.sqlite3")
            job = Job(
                portal="gulftalent",
                portal_id="job-3",
                title="Engineer",
                company="Acme",
                location="Pakistan",
                url="https://example.com/pakistan/jobs/engineer",
                description="Python",
            )
            store.upsert_job(job, 50, ["Python"], [], "queued")
            row = store.get_job(job.fingerprint)
            self.assertIsNotNone(row)
            config = AppConfig(
                database_path=tmp_path / "jobs.sqlite3",
                base_resume_path=tmp_path / "base.md",
                mena_resume_path=tmp_path / "photo.pdf",
                non_mena_resume_path=tmp_path / "np.pdf",
                output_dir=tmp_path / "generated",
                profile=ProfileConfig(),
                portals=[],
            )

            self.assertEqual(select_resume_path(config, row), tmp_path / "np.pdf")


if __name__ == "__main__":
    unittest.main()
