"""Command line interface for reviewtide.

Subcommands:
    flow       latency, queue time, and review depth from a PR export
    ownership  per-directory concentration and bus factor from a git log
    report     both of the above in one pass
    version    print the version and exit

Exit codes:
    0  clean, no findings
    1  findings present (a bus-factor-1 directory or an unreviewed PR)
    2  usage error
"""

from __future__ import annotations

import argparse
import sys

from reviewtide import __version__
from reviewtide.gitlog import GitLogError, parse_numstat_file
from reviewtide.prexport import PrExportError, parse_jsonl_file
from reviewtide.report import (
    has_findings,
    render_flow,
    render_ownership,
    render_report,
)

EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2


