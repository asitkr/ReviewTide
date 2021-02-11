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
