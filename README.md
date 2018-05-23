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

