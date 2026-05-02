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

    def test_report_combines_both(self):
        code, out = run(["report", "--pr", PR, "--gitlog", GITLOG])
        self.assertIn("== flow ==", out)
        self.assertIn("== ownership ==", out)
        self.assertEqual(code, EXIT_FINDINGS)

    def test_missing_file_is_usage_error(self):
        code, _ = run(["flow", "--pr", "does_not_exist.jsonl"])
        self.assertEqual(code, EXIT_USAGE)

    def test_deterministic_output(self):
        _, a = run(["report", "--pr", PR, "--gitlog", GITLOG])
        _, b = run(["report", "--pr", PR, "--gitlog", GITLOG])
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
