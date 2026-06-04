from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from jobapply.db import JobStore
from jobapply.models import Job
from jobapply.tracker import export_application_tracker


class TrackerTest(unittest.TestCase):
    def test_exports_csv_and_xlsx(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            store = JobStore(tmp_path / "jobs.sqlite3")
            try:
                job = Job(
                    portal="gulftalent",
                    portal_id="586804",
                    title="Backend Engineer - Python",
                    company="Michael Page",
                    location="UAE",
                    url="https://www.gulftalent.com/uae/jobs/backend-engineer-python-586804",
                    description="Python backend role",
                )
                store.upsert_job(job, 10, ["Python"], [], "queued")
                store.mark_applied(job.fingerprint, job.url, "tailored_resumes/resume.pdf")

                csv_path, xlsx_path = export_application_tracker(store, tmp_path / "tracking")

                csv_text = csv_path.read_text(encoding="utf-8")
                self.assertIn("Backend Engineer - Python", csv_text)
                self.assertIn("tailored_resumes/resume.pdf", csv_text)
                with ZipFile(xlsx_path) as archive:
                    sheet = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")
                self.assertIn("Backend Engineer - Python", sheet)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
