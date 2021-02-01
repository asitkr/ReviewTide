"""Command line interface for reviewtide.

Subcommands:
    flow       latency, queue time, and review depth from a PR export
    ownership  per-directory concentration and bus factor from a git log
    report     both of the above in one pass
    version    print the version and exit

Exit codes:
    0  clean, no findings
    1  findings present (a bus-factor-1 directory or an unreviewed PR)
