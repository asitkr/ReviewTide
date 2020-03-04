"""Parse a `git log --numstat` export.

The expected export is produced by:

    git log --numstat --date=iso-strict \
        --pretty=format:'commit%x09%H%x09%an%x09%ad'

Each commit begins with a header line whose first field is the literal
token `commit`, followed by the hash, author name, and an ISO 8601 date.
Numstat lines follow, one per changed file:

    <added>\\t<deleted>\\t<path>

Binary files report `-` for added and deleted counts; those are kept as
None so callers can distinguish them from a zero-line text change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class FileChange:
    """One changed file inside a commit."""

    path: str
    added: int | None
    deleted: int | None


@dataclass
class Commit:
    """A single commit with its per-file numstat rows."""

    commit_hash: str
    author: str
    date: datetime
    files: list[FileChange] = field(default_factory=list)


class GitLogError(ValueError):
    """Raised when the numstat export cannot be parsed."""


def _parse_count(token: str) -> int | None:
    if token == "-":
        return None
    try:
        return int(token)
    except ValueError as exc:  # pragma: no cover - defensive
        raise GitLogError(f"invalid numstat count: {token!r}") from exc


def parse_numstat(text: str) -> list[Commit]:
    """Parse the full numstat export text into a list of commits.

    Blank lines separate commits in the raw git output; they are ignored
    here because the `commit` header token already delimits records.
    """

    commits: list[Commit] = []
    current: Commit | None = None

    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip("\n")
        if not line.strip():
            continue

        fields = line.split("\t")
