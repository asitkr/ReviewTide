"""Compute review flow statistics from parsed pull requests.

All latency figures use percentiles rather than means, because a mean hides
the shape of a skewed distribution and lets one slow outlier or one fast
merge distort the headline number. Every statistic is reported with the
sample size it was computed from, and a percentile is withheld when the
sample is too small to support it.
"""

from __future__ import annotations

from dataclasses import dataclass

from reviewtide.prexport import PullRequest

# A percentile is only meaningful when the sample has enough points that the
# requested rank is not just the single most extreme observation. With fewer
# than this many values, we report the raw values and say the sample is too
# small rather than dressing up two numbers as a distribution.
MIN_SAMPLE_FOR_PERCENTILE = 5

SECONDS_PER_HOUR = 3600.0


def percentile(sorted_values: list[float], pct: float) -> float:
    """Linear interpolation percentile on an already sorted list.

    `pct` is in the range 0 to 100. This matches the common
    "linear interpolation between closest ranks" method so results are
    reproducible without a third-party library.
    """

    if not sorted_values:
        raise ValueError("percentile of empty sequence")
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (pct / 100.0) * (len(sorted_values) - 1)
    low = int(rank)
    high = min(low + 1, len(sorted_values) - 1)
    frac = rank - low
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * frac


@dataclass
class LatencyStat:
    """A latency distribution summary, in hours, with its sample size."""

    label: str
    sample_size: int
    values_hours: list[float]

    @property
    def supported(self) -> bool:
        return self.sample_size >= MIN_SAMPLE_FOR_PERCENTILE

    def p(self, pct: float) -> float | None:
        """Percentile in hours, or None when the sample is too small."""

        if not self.supported:
            return None
        return percentile(sorted(self.values_hours), pct)

    def minimum(self) -> float | None:
        return min(self.values_hours) if self.values_hours else None

    def maximum(self) -> float | None:
        return max(self.values_hours) if self.values_hours else None


def _hours(seconds: float) -> float:
    return seconds / SECONDS_PER_HOUR


def first_response_latency(prs: list[PullRequest]) -> LatencyStat:
    """Hours from a PR opening to its first review, across reviewed PRs.

    PRs that were never reviewed are excluded from the latency sample but
    counted separately by `never_reviewed`.
    """

    values: list[float] = []
    for pr in prs:
        if not pr.reviews:
            continue
        first = pr.reviews[0]
        delta = (first.submitted_at - pr.opened_at).total_seconds()
        values.append(_hours(delta))
    return LatencyStat(
        label="first_response_latency_hours",
        sample_size=len(values),
        values_hours=values,
    )


def queue_time(prs: list[PullRequest]) -> LatencyStat:
    """Alias sample for time spent waiting before the first review.

    Queue time is the same measurement as first response latency here: the
    time a PR sits in the queue before anyone engages. It is reported under
    its own label so the two concepts stay legible in output.
    """

    stat = first_response_latency(prs)
    return LatencyStat(
        label="queue_time_before_first_review_hours",
        sample_size=stat.sample_size,
        values_hours=stat.values_hours,
    )


def never_reviewed(prs: list[PullRequest]) -> list[PullRequest]:
    """PRs that carry no review events at all."""

    return [pr for pr in prs if not pr.reviews]


@dataclass
class DepthStat:
    """Review depth: distinct review rounds and comment counts per PR."""

    rounds_per_pr: list[int]
    comments_per_pr: list[int]

    @property
    def sample_size(self) -> int:
