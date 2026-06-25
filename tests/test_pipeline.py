from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from jobapply.config import AppConfig, PortalConfig, ProfileConfig
from jobapply.db import JobStore
from jobapply.models import Job
from jobapply.pipeline import scan_enabled_portals
from jobapply.portals.base import PortalAdapter


class FailingPortal(PortalAdapter):
    def scan(self) -> list[Job]:
        raise RuntimeError("browser could not launch")


class HealthyPortal(PortalAdapter):
    def scan(self) -> list[Job]:
        return [
            Job(
                portal=self.name,
                portal_id="healthy-1",
                title="Python Engineer",
                company="Example",
                location="Dubai",
                url="https://example.com/jobs/healthy-1",
                description="Python API automation",
            )
        ]


class PipelineTest(unittest.TestCase):
    def test_setup_required_portal_is_skipped_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            config = AppConfig(
                database_path=tmp_path / "jobs.sqlite3",
                base_resume_path=tmp_path / "resume.md",
                mena_resume_path=tmp_path / "resume.md",
                non_mena_resume_path=tmp_path / "resume.md",
                output_dir=tmp_path / "generated",
                profile=ProfileConfig(),
                portals=[
                    PortalConfig(
                        name="linkedin",
                        enabled=True,
                        type="setup_required",
                        options={"method": "approved browser workflow"},
                    )
                ],
            )
            store = JobStore(config.database_path)

            stats = scan_enabled_portals(config, store)

            self.assertEqual(stats["skipped_portals"], 1)
            self.assertIn("linkedin", str(stats["warnings"]))

    def test_runtime_failure_does_not_abort_other_portals(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            config = AppConfig(
                database_path=tmp_path / "jobs.sqlite3",
                base_resume_path=tmp_path / "resume.md",
                mena_resume_path=tmp_path / "resume.md",
                non_mena_resume_path=tmp_path / "resume.md",
                output_dir=tmp_path / "generated",
                profile=ProfileConfig(required_keywords=["Python"]),
                portals=[
                    PortalConfig(name="broken", enabled=True, type="failing_test", options={}),
                    PortalConfig(name="healthy", enabled=True, type="healthy_test", options={}),
                ],
            )
            store = JobStore(config.database_path)
            try:
                with patch.dict(
                    "jobapply.pipeline.ADAPTERS",
                    {"failing_test": FailingPortal, "healthy_test": HealthyPortal},
                    clear=False,
                ):
                    stats = scan_enabled_portals(config, store)

                self.assertEqual(stats["skipped_portals"], 1)
                self.assertEqual(stats["seen"], 1)
                self.assertEqual(stats["queued"], 1)
                self.assertIn("broken scan failed", str(stats["warnings"]))
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
