"""Malformed input and I/O failure coverage."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

from cargo_graph.config import load_config
from cargo_graph.graph import TestRepository
from cargo_graph.registry import Registry

VALID = """[graph]
package = crate
repository = https://index.crates.io
test_mode = false
version = 1.0.0
max_depth = 3
exclude =
"""


class ErrorTests(unittest.TestCase):
    """Make every parameter's invalid input reproducible offline."""

    def test_ini_errors(self):
        changes = [("crate", "bad/name"), ("https://", "file://"),
                   ("false", "perhaps"), ("1.0.0", "latest"),
                   ("max_depth = 3", "max_depth = x"),
                   ("max_depth = 3", "max_depth = 201"),
                   ("exclude =", "unknown ="),
                   ("[graph]", "[other]")]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.ini"
            for old, new in changes:
                path.write_text(VALID.replace(old, new))
                with self.subTest(new=new), self.assertRaises(ValueError):
                    load_config(path)

    def test_invalid_graphs(self):
        values = ['[]', '{"a": []}', '{"A": ["B"]}', '{"A": "B"}']
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "graph.json"
            for value in values:
                path.write_text(value)
                with self.subTest(value=value), self.assertRaises(ValueError):
                    TestRepository(path)

    def test_network_failure(self):
        with patch("cargo_graph.registry.urlopen", side_effect=URLError("x")):
            with self.assertRaises(URLError):
                Registry("https://invalid.example").records("crate")

    def test_unknown_version_requirement(self):
        registry = Registry("https://invalid.example")
        registry.cache = {"a": [{"vers": "1.0.0"}]}
        with self.assertRaises(ValueError):
            registry.resolve("a", "=2.0.0")
        with self.assertRaises(ValueError):
            registry.resolve("a", "^1.0.0-beta")
