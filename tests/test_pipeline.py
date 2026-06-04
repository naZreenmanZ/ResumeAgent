from pathlib import Path
import tempfile
import unittest

from jobapply.config import AppConfig, PortalConfig, ProfileConfig
from jobapply.db import JobStore
from jobapply.pipeline import scan_enabled_portals


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


if __name__ == "__main__":
    unittest.main()
