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


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(argv)
    return code, buf.getvalue()


class CliTest(unittest.TestCase):
    def test_version(self):
        code, out = run(["version"])
        self.assertEqual(code, EXIT_CLEAN)
        self.assertIn("reviewtide", out)

    def test_flow_reports_sample_size(self):
        code, out = run(["flow", "--pr", PR])
        self.assertIn("n=18", out)
        self.assertIn("p50", out)
        self.assertIn("never reviewed: 2", out)
        self.assertEqual(code, EXIT_FINDINGS)

    def test_ownership_finds_single_owner(self):
        code, out = run(["ownership", "--gitlog", GITLOG])
        self.assertIn("infra", out)
        self.assertIn("bus_factor=1", out)
        self.assertEqual(code, EXIT_FINDINGS)
