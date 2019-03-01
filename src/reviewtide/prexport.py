"""Parse a pull request export in JSON Lines format.

Each line is one JSON object describing a pull request. The offline export
is expected to carry these fields:

    id            integer or string, unique per pull request
    author        login of the person who opened it
    directories   list of top-level directories the change touched
    opened_at     ISO 8601 timestamp when the PR was opened
    reviews       list of review events, each with:
                      reviewer    login of the reviewer
                      submitted_at ISO 8601 timestamp
                      comments    integer count of comments in that review

`reviews` may be empty, meaning the PR was never reviewed. That is a real
signal and is preserved rather than dropped.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Review:
    """A single review event on a pull request."""

    reviewer: str
    submitted_at: datetime
    comments: int


@dataclass
class PullRequest:
    """A pull request with its ordered review events."""

    pr_id: str
    author: str
    directories: list[str]
    opened_at: datetime
    reviews: list[Review] = field(default_factory=list)


class PrExportError(ValueError):
    """Raised when a JSONL PR record cannot be parsed."""


def _iso(value: str, lineno: int, field_name: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError) as exc:
        raise PrExportError(
            f"line {lineno}: bad ISO datetime for {field_name}: {value!r}"
        ) from exc


def parse_pr_record(obj: dict, lineno: int) -> PullRequest:
    """Turn one decoded JSON object into a PullRequest."""

    for required in ("id", "author", "directories", "opened_at", "reviews"):
        if required not in obj:
            raise PrExportError(f"line {lineno}: missing field {required!r}")

    directories = obj["directories"]
    if not isinstance(directories, list):
        raise PrExportError(f"line {lineno}: directories must be a list")

    reviews: list[Review] = []
    for idx, rev in enumerate(obj["reviews"]):
        for required in ("reviewer", "submitted_at", "comments"):
            if required not in rev:
                raise PrExportError(
                    f"line {lineno}: review {idx} missing field {required!r}"
                )
        reviews.append(
            Review(
                reviewer=str(rev["reviewer"]),
                submitted_at=_iso(rev["submitted_at"], lineno, "submitted_at"),
                comments=int(rev["comments"]),
            )
        )

    # Order reviews chronologically so first-response logic is stable
    # regardless of export ordering.
    reviews.sort(key=lambda r: r.submitted_at)

    return PullRequest(
        pr_id=str(obj["id"]),
        author=str(obj["author"]),
        directories=[str(d) for d in directories],
        opened_at=_iso(obj["opened_at"], lineno, "opened_at"),
        reviews=reviews,
    )


def parse_jsonl(text: str) -> list[PullRequest]:
    """Parse the full JSONL export text into pull requests."""

    prs: list[PullRequest] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
