import unittest
from datetime import datetime, timezone

from reviewtide.gitlog import GitLogError, parse_numstat


class ParseNumstatTest(unittest.TestCase):
    def test_single_commit(self):
        text = (
            "commit\tabc123\tAlice Rivera\t2026-01-05T09:12:00+00:00\n"
            "14\t2\tsrc/parser.py\n"
            "8\t0\tsrc/tokens.py\n"
        )
        commits = parse_numstat(text)
        self.assertEqual(len(commits), 1)
        c = commits[0]
        self.assertEqual(c.commit_hash, "abc123")
        self.assertEqual(c.author, "Alice Rivera")
        self.assertEqual(
            c.date, datetime(2026, 1, 5, 9, 12, tzinfo=timezone.utc)
