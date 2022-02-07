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
