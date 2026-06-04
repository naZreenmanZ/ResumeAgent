import unittest

from jobapply.config import ProfileConfig
from jobapply.models import Job
from jobapply.scoring import score_job


class DedupeAndScoringTest(unittest.TestCase):
    def test_job_fingerprint_prefers_portal_id(self) -> None:
        first = Job(
            portal="demo",
            portal_id="123",
            title="Backend Engineer",
            company="Acme",
            location="Remote",
            url="https://example.com/1",
            description="Python",
        )
        second = Job(
            portal="demo",
            portal_id="123",
            title="Different Title",
            company="Other",
            location="Dubai",
            url="https://example.com/2",
            description="SQL",
        )

        self.assertEqual(first.fingerprint, second.fingerprint)

    def test_blocked_keyword_prevents_queue(self) -> None:
        job = Job(
            portal="demo",
            portal_id="blocked",
            title="Backend Python Engineer",
            company="Acme",
            location="Remote",
            url="https://example.com",
            description="Commission only role using Python.",
        )
        profile = ProfileConfig(
            target_titles=["Backend Python Engineer"],
            target_locations=["Remote"],
            required_keywords=["Python"],
            blocked_keywords=["commission only"],
        )

        scored = score_job(job, profile)

        self.assertFalse(scored.should_queue)
        self.assertEqual(scored.blocked_keywords, ["commission only"])


if __name__ == "__main__":
    unittest.main()
