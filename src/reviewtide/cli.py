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


def _emit(lines: list[str]) -> None:
    sys.stdout.write("\n".join(lines) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reviewtide",
        description="Measure code review flow from offline exports.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_flow = sub.add_parser("flow", help="review latency and depth")
    p_flow.add_argument("--pr", required=True, help="path to JSONL PR export")

    p_own = sub.add_parser("ownership", help="directory bus factor")
    p_own.add_argument(
        "--gitlog", required=True, help="path to git numstat export"
    )

    p_rep = sub.add_parser("report", help="combined flow and ownership")
    p_rep.add_argument("--pr", required=True, help="path to JSONL PR export")
    p_rep.add_argument(
        "--gitlog", required=True, help="path to git numstat export"
    )

    sub.add_parser("version", help="print version and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        _emit([f"reviewtide {__version__}"])
        return EXIT_CLEAN

    try:
        if args.command == "flow":
            prs = parse_jsonl_file(args.pr)
            _emit(render_flow(prs))
            return EXIT_FINDINGS if any(
                not pr.reviews for pr in prs
            ) else EXIT_CLEAN

        if args.command == "ownership":
            commits = parse_numstat_file(args.gitlog)
            _emit(render_ownership(commits))
            from reviewtide.ownership import at_risk, compute_ownership

            return (
                EXIT_FINDINGS
                if at_risk(compute_ownership(commits))
                else EXIT_CLEAN
            )

        if args.command == "report":
            prs = parse_jsonl_file(args.pr)
            commits = parse_numstat_file(args.gitlog)
            _emit(render_report(prs, commits))
            return (
                EXIT_FINDINGS
                if has_findings(prs, commits)
                else EXIT_CLEAN
            )
    except FileNotFoundError as exc:
        sys.stderr.write(f"error: file not found: {exc.filename}\n")
        return EXIT_USAGE
    except (GitLogError, PrExportError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return EXIT_USAGE

    parser.error("unknown command")  # pragma: no cover
    return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
