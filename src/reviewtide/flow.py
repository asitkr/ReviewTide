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

