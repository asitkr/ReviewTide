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
        reviews.append(
            Review(reviewer="r", submitted_at=submitted, comments=comments)
        )
        if rounds_comments:
            for i, c in enumerate(rounds_comments[1:], start=1):
                reviews.append(
                    Review(
                        reviewer="r",
                        submitted_at=submitted + timedelta(hours=i),
                        comments=c,
                    )
                )
    return PullRequest(
        pr_id=str(pr_id),
        author="a",
        directories=["src"],
        opened_at=BASE,
        reviews=reviews,
    )


class PercentileTest(unittest.TestCase):
    def test_median_odd(self):
        self.assertEqual(percentile([1.0, 2.0, 3.0], 50), 2.0)

    def test_p90_interpolates(self):
        vals = [float(x) for x in range(1, 11)]
        self.assertAlmostEqual(percentile(vals, 90), 9.1)

    def test_single_value(self):
