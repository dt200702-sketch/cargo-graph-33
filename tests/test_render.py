"""D2 output and CLI error tests."""

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import unittest

from cargo_graph.__main__ import main
from cargo_graph.render import to_d2

ROOT = Path(__file__).resolve().parents[1]


class RenderTests(unittest.TestCase):
    """Check edge direction, isolated nodes and predictable output."""

    def test_d2(self):
        self.assertEqual(to_d2({"B": [], "A": ["B"], "C": []}),
                         'direction: right\nn0: "A"\nn1: "B"\nn2: "C"'
                         '\nn0 -> n1')

    def test_empty(self):
        self.assertEqual(to_d2({}), "direction: right")

    def test_cli(self):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main([str(ROOT / "examples/test.ini")])
        self.assertEqual(code, 0)
        self.assertIn("n3 -> n0", output.getvalue())

    def test_cli_missing_file(self):
        output = io.StringIO()
        with redirect_stderr(output):
            code = main(["/nonexistent/config.ini"])
        self.assertEqual(code, 2)
        self.assertIn("Error:", output.getvalue())
