"""Per-directory contribution concentration and a bus-factor signal.

Concentration is measured on commit touches per directory, not on line
counts, and never per person as a productivity score. The question this
module answers is "how many people would we need to lose before this
directory has nobody who has recently touched it", which is a risk signal,
not a ranking of individuals.

Bus factor here is the smallest number of authors whose combined share of
a directory's commit touches exceeds 50 percent. A bus factor of 1 means a
single author accounts for the majority of activity in that directory.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from reviewtide.gitlog import Commit


def top_level_dir(path: str) -> str:
    """Return the first path segment, or "(root)" for top-level files."""

    norm = path.replace("\\", "/")
    if "/" not in norm:
        return "(root)"
    return norm.split("/", 1)[0]


@dataclass
class DirectoryOwnership:
    """Concentration facts for one directory."""

    directory: str
    total_touches: int
    author_touches: dict[str, int]

    @property
    def author_count(self) -> int:
        return len(self.author_touches)

    def ranked_authors(self) -> list[tuple[str, int]]:
        """Authors by touch count, descending, then by name for stability."""

        return sorted(
            self.author_touches.items(),
            key=lambda kv: (-kv[1], kv[0]),
        )

    def bus_factor(self) -> int:
        """Smallest author count whose share exceeds 50 percent of touches."""

        if self.total_touches == 0:
            return 0
        cumulative = 0
        threshold = self.total_touches / 2.0
        for count, (_author, touches) in enumerate(self.ranked_authors(), 1):
            cumulative += touches
            if cumulative > threshold:
                return count
        return self.author_count

    def top_share(self) -> float:
        """Fraction of touches held by the single most active author."""

        if self.total_touches == 0:
            return 0.0
