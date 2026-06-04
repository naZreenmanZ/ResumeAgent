import unittest

from jobapply.portals.feed import FeedPortal


class FeedTest(unittest.TestCase):
    def test_reads_json_feed_payload(self) -> None:
        adapter = FeedPortal("wellfound", {"url": "https://example.com/jobs.json"})

        jobs = adapter._scan_json(
            b'{"jobs":[{"title":"AI Engineer","company":"Acme","url":"https://example.com/a"}]}'
        )

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].title, "AI Engineer")
        self.assertEqual(jobs[0].company, "Acme")

    def test_reads_rss_payload(self) -> None:
        adapter = FeedPortal("indeed", {"url": "https://example.com/rss"})

        jobs = adapter._scan_xml(
            b"""
            <rss><channel><item>
              <title>Backend Engineer</title>
              <link>https://example.com/job</link>
              <description>Python APIs</description>
              <guid>job-1</guid>
            </item></channel></rss>
            """
        )

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].portal_id, "job-1")


if __name__ == "__main__":
    unittest.main()
