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
