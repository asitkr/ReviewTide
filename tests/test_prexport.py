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
