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
        lines.append(f"  rounds per pr:   {rounds}")
        lines.append(f"  comments per pr: {comments}")
        return lines
    for pct in PERCENTILES:
        rp = stat.rounds_percentile(pct)
        cp = stat.comments_percentile(pct)
        lines.append(
            f"  p{int(pct)}  rounds {rp:.1f}  comments {cp:.1f}"
        )
    return lines


def render_flow(prs: list[PullRequest]) -> list[str]:
    """Return the flow report as a list of output lines."""

    lines: list[str] = []
    lines.append(f"pull requests in export: {len(prs)}")
    unreviewed = never_reviewed(prs)
    lines.append(f"never reviewed: {len(unreviewed)}")
    lines.append("")

    lines.extend(_latency_lines(queue_time(prs)))
    lines.append("")
    lines.extend(_depth_lines(review_depth(prs)))
    return lines


def _fmt_share(share: float) -> str:
    return f"{share * 100:.0f}%"


def render_ownership(commits: list[Commit]) -> list[str]:
    """Return the ownership report as a list of output lines."""

    ownership = compute_ownership(commits)
    lines: list[str] = []
    lines.append(f"commits in export: {len(commits)}")
    lines.append(f"directories: {len(ownership)}")
    lines.append("")
    lines.append("directory concentration (riskiest first)")
    for d in ownership:
        top_author, top_count = d.ranked_authors()[0]
        lines.append(
            f"  {d.directory}: bus_factor={d.bus_factor()} "
            f"authors={d.author_count} touches={d.total_touches} "
            f"top={top_author} ({_fmt_share(d.top_share())})"
        )
    return lines


def render_report(
    prs: list[PullRequest], commits: list[Commit]
) -> list[str]:
    """Combined flow plus ownership report."""

    lines: list[str] = ["== flow =="]
    lines.extend(render_flow(prs))
    lines.append("")
    lines.append("== ownership ==")
    lines.extend(render_ownership(commits))
    return lines


def has_findings(prs: list[PullRequest], commits: list[Commit]) -> bool:
    """A finding is any bus-factor-1 directory or any never-reviewed PR."""

    from reviewtide.ownership import at_risk

    if never_reviewed(prs):
        return True
    if at_risk(compute_ownership(commits)):
        return True
    return False

// draft note 1255
