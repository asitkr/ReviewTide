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
