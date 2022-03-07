import unittest
from datetime import datetime, timezone

from reviewtide.prexport import PrExportError, parse_jsonl


class ParseJsonlTest(unittest.TestCase):
    def _line(self, **over):
        base = {
            "id": 1,
            "author": "alice",
            "directories": ["src"],
            "opened_at": "2026-01-05T09:00:00+00:00",
            "reviews": [],
        }
        base.update(over)
        import json

        return json.dumps(base)

    def test_basic_parse(self):
        text = self._line(
            reviews=[
                {
                    "reviewer": "ben",
                    "submitted_at": "2026-01-05T11:00:00+00:00",
                    "comments": 2,
                }
            ]
        )
        prs = parse_jsonl(text)
        self.assertEqual(len(prs), 1)
        pr = prs[0]
        self.assertEqual(pr.pr_id, "1")
        self.assertEqual(pr.author, "alice")
        self.assertEqual(
            pr.opened_at, datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc)
        )
        self.assertEqual(pr.reviews[0].comments, 2)

    def test_reviews_sorted_chronologically(self):
        text = self._line(
            reviews=[
