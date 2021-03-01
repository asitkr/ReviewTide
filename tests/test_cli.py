import io
import os
import unittest
from contextlib import redirect_stdout

from reviewtide.cli import EXIT_CLEAN, EXIT_FINDINGS, EXIT_USAGE, main

SAMPLES = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "samples"
)
PR = os.path.join(SAMPLES, "pr_export.jsonl")
GITLOG = os.path.join(SAMPLES, "gitlog.numstat")
