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
        return "n/a"
    return f"{value:.1f}h"


def _latency_lines(stat: LatencyStat) -> list[str]:
    lines: list[str] = []
    lines.append(f"{stat.label} (n={stat.sample_size})")
    if stat.sample_size == 0:
        lines.append("  no reviewed pull requests in sample")
        return lines
    if not stat.supported:
        lines.append(
            f"  sample too small for percentiles "
            f"(need n>={MIN_SAMPLE_FOR_PERCENTILE}); raw values in hours:"
        )
        raw = ", ".join(f"{v:.1f}" for v in sorted(stat.values_hours))
        lines.append(f"  {raw}")
        return lines
    for pct in PERCENTILES:
        lines.append(f"  p{int(pct)}  {_fmt_hours(stat.p(pct))}")
    lines.append(f"  min  {_fmt_hours(stat.minimum())}")
    lines.append(f"  max  {_fmt_hours(stat.maximum())}")
    return lines


def _depth_lines(stat: DepthStat) -> list[str]:
    lines: list[str] = []
    lines.append(f"review_depth (n={stat.sample_size})")
    if stat.sample_size == 0:
        lines.append("  no reviewed pull requests in sample")
        return lines
    if not stat.supported:
        lines.append(
            f"  sample too small for percentiles "
            f"(need n>={MIN_SAMPLE_FOR_PERCENTILE})"
        )
        rounds = ", ".join(str(r) for r in sorted(stat.rounds_per_pr))
        comments = ", ".join(str(c) for c in sorted(stat.comments_per_pr))
