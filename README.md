<p align="center">
  <img src="docs/assets/banner.svg" alt="reviewtide banner: a review timeline with queue time, first review and rounds, and the metric and honesty rules beside it" width="760">
</p>

<div align="center">

<img src="docs/assets/logo.svg" width="240"
  alt="The word reviewtide, review set in slate and tide in teal, split at the compound word boundary, above the caption code review flow" />

# ReviewTide

<table>
<tr>
<td align="center"><strong>3.8h</strong><br/>median first response</td>
<td align="center"><strong>49.2h</strong><br/>p90 first response</td>
<td align="center"><strong>n=18</strong><br/>reviewed PRs in sample</td>
</tr>
</table>

</div>

---

reviewtide refuses to rank people. That is the first thing to know about it,
before any feature. It measures how a change moves through review, not how
"productive" a person is, because the moment a tool puts a number next to a name
the number becomes the target and the work bends to it. This README leads with
the refusal because it is a design position, not an omission: the rest of the
tool follows from it.

reviewtide reads two offline exports, a `git log --numstat` file and a pull
request export in JSON Lines, and reports queue time before first review, first
response latency, review depth, and per-directory knowledge concentration as a
bus-factor signal. It runs on the Python standard library only: no third-party
packages, no network access anywhere. The three figures above are the real
median and p90 first-response latency and the reviewed-PR sample size from the
fixtures in `samples/`, captured by running the CLI in this session. The sample
size is on the strip on purpose, so a small sample can never hide behind a
confident-looking percentile.

## The metric this tool refuses to compute, and why leading with that matters

There is no lines-per-day figure here. No commits-per-person leaderboard. No
ranking of individuals by output of any kind. That absence is the product.

Ranking people by line count rewards churn and punishes the careful work that
keeps a codebase alive: deleting dead code, reviewing thoroughly, pairing,
mentoring, and writing the small change that took a day of thought. A dashboard
that scores those at zero will, over time, produce a team that stops doing
them. reviewtide is built to measure the health of the review process itself,
so the one number it withholds is the one that would corrupt the behaviour it
wants to observe.

The single place reviewtide does count activity per author is the bus-factor
signal, and even there the unit is inverted. The question is not "who did the
most" but "how few people would we have to lose before this directory has
nobody who has recently touched it". That is a risk measure for the team, not a
scoreboard. Leading with the refusal matters because every later section
(percentiles over means, touches over line counts, offline exports over a live
API) is a consequence of the same stance.

## Install

reviewtide targets Python 3.11 or newer. Install it as an editable package,
which registers a `reviewtide` console command:

```
pip install -e .
```

You can also run it without installing by pointing Python at `src`:

```
PYTHONPATH=src python -m reviewtide version
```

## Commands

```
reviewtide flow      --pr <pr_export.jsonl>
reviewtide ownership --gitlog <gitlog.numstat>
reviewtide report    --pr <pr_export.jsonl> --gitlog <gitlog.numstat>
reviewtide version
```

| Command     | Reads                    | Reports                                        |
| ----------- | ------------------------ | ---------------------------------------------- |
| `flow`      | PR export                | queue time, first response latency, depth      |
| `ownership` | git numstat export       | per-directory concentration and bus factor     |
| `report`    | both exports             | flow then ownership in one pass                |
| `version`   | nothing                  | the package version                            |

## What it measures

Four measures, each defined precisely, each with what it cannot tell you. The
definitions live in `src/reviewtide/flow.py` and `src/reviewtide/ownership.py`.

### Queue time before first review

The number of hours between a pull request opening (`opened_at`) and the
timestamp of its first review event, summarised across all reviewed PRs. It
answers "how long does a change wait before anyone engages with it".

What it cannot tell you: in this export, queue time and first response latency
are the same measurement, because the export carries no separate "ready for
review" moment. If your process distinguishes "opened" from "marked ready",
reviewtide treats the open time as the start of the wait.

### First response latency

The same underlying measurement as queue time, reported under its own label so
the two concepts stay legible: hours from open to first review. It is kept
separate because teams reason about "queue time" (a property of the backlog)
and "first response" (a property of reviewers) differently, even when the
export cannot yet separate them.

What it cannot tell you: it says nothing about the quality of that first
response. A one-word "LGTM" and a detailed critique count the same here.

### Review depth

Two numbers per reviewed PR: the number of review rounds (one review event is
one round) and the total comments summed across those rounds. Reported as
percentiles over the reviewed PRs.

What it cannot tell you: comment count is not comment weight. A PR with ten
nitpick comments looks deeper than one with a single comment that caught a real
defect. Depth is a proxy for engagement, not rigour.

### Ownership concentration

For each top-level directory, the number of distinct authors who touched it,
the total touches, the share held by the most active author, and the bus
factor: the smallest set of authors whose combined share of touches exceeds 50
percent. A "touch" is one commit that changed at least one file in the
directory, counted once regardless of how many files or lines it changed.

What it cannot tell you: it does not weight by recency or by how critical a
directory is. A directory of many trivial commits and one of a few large,
careful commits can produce a similar bus factor. It reads only the git export;
work done outside version control is invisible.

## Percentiles and honest sample sizes

Every statistic prints the sample size it was computed from, written as `n=`
next to the label, so a small sample cannot masquerade as a trend. The strip at
the top of this README prints `n=18` for exactly that reason.

Latency is summarised with percentiles, never a mean. A mean hides the shape of
a skewed distribution and lets one very slow review, or one instant merge, drag
the headline away from the typical experience. Percentiles preserve both: the
p50 shows the typical case, the p90 shows the tail. The method is linear
interpolation between closest ranks, in `percentile()` in `flow.py`, so results
are reproducible without a third-party library.

Below a sample of five, reviewtide withholds the percentiles entirely. Instead
of reporting a p90 built from two data points, which would carry the authority
of a statistic and the reliability of a coin flip, it prints the raw values and
an explicit message that the sample is too small. The threshold is
`MIN_SAMPLE_FOR_PERCENTILE = 5` in `flow.py`, and the small-sample branch reads:

```
sample too small for percentiles (need n>=5); raw values in hours:
```

This is the honest failure mode: say "I do not have enough data" rather than
manufacture a confident answer.

## Ownership and the bus factor signal

Bus factor uses a simple majority rule: the smallest number of authors whose
combined touches exceed half of a directory's total. A bus factor of 1 means a
single author accounts for the majority of activity, so if that person becomes
unavailable, nobody else has recently worked in that directory. Directories
sort riskiest first (rising bus factor, then falling top share, then name), an
ordering defined at the end of `compute_ownership()` in `ownership.py`.

In the sample fixtures, two directories are owned by a single author. `infra`
is touched only by Dana Kim across every commit that changes it, and `docs` is
touched only by Carla Nunez. Both report `bus_factor=1` with `authors=1` and a
100 percent top share. `infra` is the directory the sample was built to
surface: the clearest single-owner risk in the export. The remaining
directories (`cli`, `tests`, `src`) also report `bus_factor=1` because one
author holds a majority even where two authors are present, which is exactly
the concentration the majority rule is designed to catch.

## A worked run

The block below was captured in this session by running the CLI against the
fixtures in `samples/`. It is pasted verbatim.

Command:

```
reviewtide report --pr samples/pr_export.jsonl --gitlog samples/gitlog.numstat
```

Output:

```
== flow ==
pull requests in export: 20
never reviewed: 2

queue_time_before_first_review_hours (n=18)
  p50  3.8h
  p75  17.5h
  p90  49.2h
  min  1.0h
  max  67.0h

review_depth (n=18)
  p50  rounds 1.0  comments 4.0
  p75  rounds 1.0  comments 5.0
  p90  rounds 2.0  comments 7.3

== ownership ==
commits in export: 20
directories: 5

directory concentration (riskiest first)
  docs: bus_factor=1 authors=1 touches=4 top=Carla Nunez (100%)
  infra: bus_factor=1 authors=1 touches=6 top=Dana Kim (100%)
  cli: bus_factor=1 authors=2 touches=3 top=Ben Osei (67%)
  tests: bus_factor=1 authors=2 touches=5 top=Ben Osei (60%)
  src: bus_factor=1 authors=2 touches=7 top=Alice Rivera (57%)
```

Reading this run: 20 PRs in the export, 2 of which (ids 107 and 116 in the
sample) were never reviewed, so the flow sample is `n=18` rather than 20.
Median first response is under four hours, but the p90 of 49.2 hours and the
max of 67.0 hours show a long tail. The ownership block flags `docs` and
`infra` as single-owner directories, the finding that should trigger a
conversation about spreading knowledge before those owners take leave.

## Reading the latency asset

The histogram below shows the shape behind the flow percentiles, drawn from the
same run. Its embedded numbers match the output above: n=18, p50=3.8h,
p90=49.2h, max=67.0h.

![Histogram of hours from pull request opened to first review across 18
reviewed pull requests. Median 3.8 hours, 90th percentile 49.2 hours. Bins: 0
to 6 hours has 10, 6 to 12 has 2, 12 to 24 has 3, 24 to 48 has 1, 48 to 72 has
2.](docs/assets/review-latency.svg)

The first bin (0 to 6 hours) holds 10 of the 18 reviewed PRs, which is why the
median sits at 3.8 hours. The rightmost bin (48 to 72 hours) is drawn in amber
because it holds the p90 tail: the two reviews that took over two days are the
ones worth asking about, so the colour points the eye there rather than at the
tall first bar.

## Input formats

reviewtide reads two files. Neither is fetched: you export them yourself and
pass the paths in.

### The git numstat export

Produce it with:

```
git log --numstat --date=iso-strict --pretty=format:'commit%x09%H%x09%an%x09%ad'
```

Each commit is a header line followed by one numstat row per changed file.
Parsing lives in `src/reviewtide/gitlog.py`.

| Line type     | Fields (tab separated)                    | Notes                                   |
| ------------- | ----------------------------------------- | --------------------------------------- |
| commit header | `commit`, hash, author name, ISO date     | literal token `commit` in field one     |
| numstat row   | added, deleted, path                      | added/deleted are `-` for binary files  |

Binary files report `-` for both counts, which reviewtide keeps as `None` so a
binary change is distinguishable from a zero-line text change. A numstat row
before any commit header is a parse error.

### The JSON Lines PR export

One JSON object per line, one object per pull request. Parsing lives in
`src/reviewtide/prexport.py`.

| Field         | Type                | Meaning                                            |
| ------------- | ------------------- | -------------------------------------------------- |
| `id`          | integer or string   | unique per pull request                            |
| `author`      | string              | login of the person who opened it                  |
| `directories` | list of strings     | top-level directories the change touched           |
| `opened_at`   | ISO 8601 string     | when the PR was opened                             |
| `reviews`     | list of objects     | review events; may be empty (never reviewed)       |

Each entry in `reviews` carries three fields:

| Field          | Type            | Meaning                          |
| -------------- | --------------- | -------------------------------- |
| `reviewer`     | string          | login of the reviewer            |
| `submitted_at` | ISO 8601 string | when the review was submitted    |
| `comments`     | integer         | comment count in that review     |

An empty `reviews` list is a real signal (the PR was never reviewed) and is
preserved rather than dropped. Reviews are sorted chronologically on parse so
first-response logic does not depend on export ordering. A missing required
field or malformed JSON is a parse error that stops the run with exit code 2.

See `samples/` for a worked pair of fixtures and `samples/README.md` for how
they were constructed.

## Output format

Output is line-oriented and deterministic: fixed field order, no wall-clock
time, no randomness, so two runs of the same input diff cleanly in git.
| Line                                                | Meaning                                             |
| --------------------------------------------------- | --------------------------------------------------- |
| `pull requests in export: N`                        | count of PR objects parsed                          |
| `never reviewed: N`                                 | PRs with an empty `reviews` list                    |
| `<label> (n=N)`                                     | a statistic and the sample size it rests on         |
| `  pXX  V.Vh`                                        | latency percentile in hours                         |
| `  min` / `  max`                                   | extremes of the latency sample                      |
| `  pXX  rounds R.R  comments C.C`                   | review-depth percentile                             |
| `commits in export: N`                              | count of commits parsed from the git log            |
| `directories: N`                                    | distinct top-level directories seen                 |
| `  <dir>: bus_factor=B authors=A touches=T top=... (P%)` | one directory concentration line              |

The `report` command wraps the two blocks with `== flow ==` and
`== ownership ==` headers.

## Exit codes

Defined in `src/reviewtide/cli.py`.

| Code | Name            | Meaning                                                          |
| ---- | --------------- | ---------------------------------------------------------------- |
| 0    | `EXIT_CLEAN`    | ran successfully, no findings                                    |
| 1    | `EXIT_FINDINGS` | a finding is present: a bus-factor-1 directory or an unreviewed PR |
| 2    | `EXIT_USAGE`    | usage error: missing file or malformed export                    |

A finding is not an error: exit code 1 means the tool found something worth
attention, which makes it usable in CI (fail on findings, pass otherwise).

## Limitations

reviewtide measures flow, not quality, and cannot see anything outside the
exports you give it.

- Queue time and first response latency are the same measurement here: time from
  open to first review. If your process distinguishes "ready for review" from
  "opened", reviewtide cannot see that, because the export does not carry it.
- A "touch" for ownership is one commit that changed a directory, counted once
  regardless of file or line count. A directory touched by many trivial commits
  and one touched by a few large commits can look similar.
- Bus factor uses a simple majority rule. It does not weight by recency or by
  how critical a directory is to the system.
- reviewtide reads only what is in the exports. It does not fetch anything and
  cannot reconstruct reviews, comments, or conversations that were never
  recorded in the export. Discussion that happened in chat, in a call, or in a
  tool that did not make it into the JSON Lines file is invisible.
- The tool does not merge a PR export with a git log by identity; the two are
  reported side by side. Matching a specific PR to its commits is out of scope.

## Design decisions

Each decision records the alternative that was rejected and why.

### Percentiles, not means

Rejected: reporting the mean first response latency. A single 67-hour outlier
can drag a mean well above the typical experience, making a mostly-healthy
queue look slow. Percentiles preserve the shape a mean flattens into one
misleading figure.

### No per-author productivity metric

Rejected: a lines-per-author or commits-per-author summary. It is easy to
compute from the same git export and is the number teams ask for first. It was
left out because it rewards churn, punishes deletion and review, and turns a
measurement tool into a surveillance one. The bus-factor signal is the
deliberate substitute: it uses per-author data to measure team risk, not
individual output.

### Offline exports, not a live API

Rejected: calling a hosting provider's API directly. An API integration would
remove the export step, but it would bind the tool to one provider's schema and
auth model, require network access and credentials, and make runs
non-reproducible as the upstream data shifts. Reading a file you exported keeps
reviewtide provider-agnostic, offline, dependency-free, and deterministic: the
same file always produces the same report.

## Repository layout

```
reviewtide/
  README.md              this file
  LICENSE                MIT license text
  CHANGELOG.md           release notes, starting at 0.1.0
  pyproject.toml         package metadata and the reviewtide console script
  .gitignore             ignores caches and build artifacts
  src/reviewtide/
    __init__.py          package marker and version string
    __main__.py          enables python -m reviewtide
    cli.py               argument parsing, subcommands, exit codes
    gitlog.py            parse git log --numstat exports
    prexport.py          parse JSON Lines pull request exports
    flow.py              latency, queue time, review depth, percentiles
    ownership.py         per-directory concentration and bus factor
    report.py            deterministic line-oriented rendering
  samples/
    README.md            how the fixtures were built and what they exercise
    gitlog.numstat       20 commits across 5 directories
    pr_export.jsonl      20 PRs, 2 never reviewed
  docs/assets/
    logo.svg             the wordmark, review in slate and tide in teal
    review-latency.svg   first response latency histogram for the sample
  tests/
    test_cli.py          CLI exit codes and output on the fixtures
    test_flow.py         percentile math, latency, depth, small-sample rule
    test_gitlog.py       numstat parsing and error cases
    test_ownership.py    top-level dir, bus factor, at-risk detection
    test_prexport.py     JSONL parsing, sorting, error cases
```

## Glossary

| Term                    | Meaning in reviewtide                                                     |
| ----------------------- | ------------------------------------------------------------------------- |
| queue time              | hours a PR waits from open to first review                                |
| first response latency  | same measurement as queue time, reported under its own label             |
| review round            | one review event on a PR                                                  |
| review depth            | rounds and total comments per reviewed PR                                 |
| touch                   | one commit that changed at least one file in a directory, counted once   |
| top share               | fraction of a directory's touches held by its most active author         |
| bus factor              | smallest set of authors whose combined touches exceed 50 percent         |
| at-risk directory       | a directory with bus factor 1: a single dominant author                  |
| never reviewed          | a PR whose `reviews` list is empty                                       |
| n                       | the sample size a statistic was computed from, printed with every stat  |

## Verification

The test suite runs on the standard library test runner with no extra
dependencies:

```
PYTHONPATH=src python -m unittest discover -s tests -v
```

In this session the full suite reported:

```
Ran 34 tests in 0.005s

OK
```

The 34 tests break down as 6 in `test_cli.py`, 9 in `test_flow.py`, 6 in
`test_gitlog.py`, 7 in `test_ownership.py`, and 6 in `test_prexport.py`. They
cover the percentile math and small-sample withholding rule, latency in hours
with unreviewed PRs excluded, review-depth sums, numstat parsing (including
binary `-` counts and malformed headers), JSONL parsing (including review
sorting, preserved empty reviews, and parse errors), and the CLI exit codes,
sample-size output, single-owner detection, and deterministic repeat runs.

## Roadmap

No dates are promised. In rough order of intent:

- An optional "ready for review" timestamp so queue time and first response
  latency can be separated when the export carries it.
- Recency weighting for the bus-factor signal so an owner who left six months
  ago does not count the same as an active one.
- A machine-readable output mode (JSON) alongside the current text, and a way to
  diff two reports so a team can see whether concentration and latency improve
  between exports.

## License

MIT. See [LICENSE](LICENSE).

<!-- draft note 748 -->
