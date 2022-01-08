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
        self.assertEqual(percentile([5.0], 50), 5.0)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            percentile([], 50)


class LatencyTest(unittest.TestCase):
    def test_latency_computed_in_hours(self):
        prs = [make_pr(i, hours_to_first=i + 1) for i in range(6)]
        stat = first_response_latency(prs)
        self.assertEqual(stat.sample_size, 6)
        self.assertTrue(stat.supported)
        self.assertAlmostEqual(stat.minimum(), 1.0)
        self.assertAlmostEqual(stat.maximum(), 6.0)

    def test_unreviewed_excluded_from_sample(self):
        prs = [make_pr(1, hours_to_first=2), make_pr(2)]
        stat = first_response_latency(prs)
        self.assertEqual(stat.sample_size, 1)
