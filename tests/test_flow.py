import unittest
from datetime import datetime, timedelta, timezone

from reviewtide.flow import (
    MIN_SAMPLE_FOR_PERCENTILE,
    first_response_latency,
    percentile,
    review_depth,
)
from reviewtide.prexport import PullRequest, Review

BASE = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)


def make_pr(pr_id, hours_to_first=None, rounds_comments=None):
    reviews = []
    if hours_to_first is not None:
        submitted = BASE + timedelta(hours=hours_to_first)
        comments = rounds_comments[0] if rounds_comments else 1
