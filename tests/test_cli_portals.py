from pathlib import Path
from contextlib import redirect_stdout
import io
import tempfile
import unittest

from jobapply.cli import command_portal_add
from jobapply.config import load_config


class PortalCliTest(unittest.TestCase):
    def test_portal_add_appends_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            config_path = tmp_path / "config.toml"
            config_path.write_text(
                'database_path = "jobs.sqlite3"\n'
                'base_resume_path = "resume.md"\n'
                'tailored_resume_dir = "tailored_resumes"\n'
                'tracking_dir = "tracking"\n',
                encoding="utf-8",
            )

            with redirect_stdout(io.StringIO()):
                command_portal_add(str(config_path), "Monster Gulf", "saved search", False)

            config = load_config(config_path)
            self.assertEqual(config.portals[0].name, "monster-gulf")
            self.assertEqual(config.portals[0].type, "setup_required")
            self.assertEqual(config.tailored_resume_dir, (tmp_path / "tailored_resumes").resolve())
            self.assertEqual(config.tracking_dir, (tmp_path / "tracking").resolve())


if __name__ == "__main__":
    unittest.main()
