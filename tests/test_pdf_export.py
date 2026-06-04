from pathlib import Path
import tempfile
import unittest

from jobapply.pdf_export import export_tailored_pdf


class PdfExportTest(unittest.TestCase):
    def test_exports_tailored_markdown_to_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            draft = tmp_path / "draft.md"
            draft.write_text(
                "# Targeted Resume Draft\n\n"
                "## Professional Summary\n\n"
                "Engineer aligned to Python and APIs.\n\n"
                "## Technical Skills\n\n"
                "- **Backend:** Python, APIs, SQL\n"
                "- **Frontend:** React, TypeScript\n\n"
                "## Professional Experience\n\n"
                "### Engineer — Acme | 2024 – Present\n\n"
                "- Built scalable APIs.\n\n"
                "## Certifications & Achievements\n\n"
                "- AWS Certified Cloud Practitioner\n\n"
                "## Education\n\n"
                "- MCA, Computer Application\n\n"
                "## Languages\n\n"
                "- English\n",
                encoding="utf-8",
            )

            output = export_tailored_pdf(draft)

            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
