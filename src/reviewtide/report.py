"""Render flow and ownership results as line-oriented, deterministic text.

Output is designed to diff cleanly in git: fixed field order, no wall-clock
time, no randomness. Every statistic prints the sample size it rests on.
"""

from __future__ import annotations

from reviewtide.flow import (
    DepthStat,
    LatencyStat,
    MIN_SAMPLE_FOR_PERCENTILE,
    never_reviewed,
    queue_time,
    review_depth,
)
from reviewtide.ownership import DirectoryOwnership, compute_ownership
from reviewtide.gitlog import Commit
from reviewtide.prexport import PullRequest

PERCENTILES = (50.0, 75.0, 90.0)


def _fmt_hours(value: float | None) -> str:
    if value is None:
