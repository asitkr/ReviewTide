import unittest
from datetime import datetime, timezone

from reviewtide.gitlog import Commit, FileChange
from reviewtide.ownership import at_risk, compute_ownership, top_level_dir

BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def commit(author, *paths):
    return Commit(
        commit_hash="h",
        author=author,
        date=BASE,
        files=[FileChange(path=p, added=1, deleted=0) for p in paths],
    )


class TopLevelDirTest(unittest.TestCase):
    def test_nested(self):
        self.assertEqual(top_level_dir("src/a/b.py"), "src")

    def test_root_file(self):
        self.assertEqual(top_level_dir("README.md"), "(root)")

    def test_backslash_normalised(self):
        self.assertEqual(top_level_dir("infra\\deploy.tf"), "infra")


class OwnershipTest(unittest.TestCase):
    def test_single_owner_bus_factor_one(self):
        commits = [commit("dana", "infra/a.tf") for _ in range(4)]
        own = compute_ownership(commits)
        self.assertEqual(len(own), 1)
        self.assertEqual(own[0].bus_factor(), 1)
        self.assertEqual(own[0].top_share(), 1.0)
