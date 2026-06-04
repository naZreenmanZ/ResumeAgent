from pathlib import Path
import tempfile
import unittest

from jobapply.portals.saved_search_import import SavedSearchImportPortal


class SavedSearchImportTest(unittest.TestCase):
    def test_reads_csv_export(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            path = Path(raw_tmp) / "linkedin.csv"
            path.write_text(
                "title,company,location,url,description,requirements,job_id\n"
                "Backend Engineer,Acme,Remote,https://example.com,Python APIs,Python;SQL,abc\n",
                encoding="utf-8",
            )
            adapter = SavedSearchImportPortal("linkedin", {"path": str(path)})

            jobs = adapter.scan()

            self.assertEqual(len(jobs), 1)
            self.assertEqual(jobs[0].portal, "linkedin")
            self.assertEqual(jobs[0].title, "Backend Engineer")
            self.assertEqual(jobs[0].requirements, ["Python", "SQL"])


if __name__ == "__main__":
    unittest.main()
