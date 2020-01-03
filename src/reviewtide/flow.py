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
