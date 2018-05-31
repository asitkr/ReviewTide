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
