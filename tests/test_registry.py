"""Offline checks of Cargo records and version requirements."""

import unittest
from cargo_graph.registry import Registry, index_path
from cargo_graph.semver import satisfies


class RegistryTests(unittest.TestCase):
    """Resolve deterministic fixtures without HTTP."""

    def test_paths(self):
        for name, expected in [("a", "1/a"), ("ab", "2/ab"),
                               ("Abc", "3/a/abc"), ("serde", "se/rd/serde")]:
            self.assertEqual(index_path(name), expected)

    def test_requirements(self):
        cases = [("1.4.0", "^1.2", True), ("2.0.0", "1.2", False),
                 ("0.3.0", "^0.2", False), ("0.0.4", "0.0.3", False),
                 ("0.5.0", "0", True), ("1.3.0", "~1.2", False),
                 ("1.2.9", "1.2.*", True), ("1.9.0", ">=1,<2", True),
                 ("1.2.0", "=1.2", True), ("2.0.0", "*", True)]
        for version, requirement, expected in cases:
            with self.subTest(version=version, requirement=requirement):
                self.assertEqual(satisfies(version, requirement), expected)

    def test_resolution_and_filter(self):
        registry = Registry("https://invalid.example")
        registry.cache = {
            "a": [{"vers": "1.0.0", "deps": [
                {"name": "renamed", "package": "b", "req": "^1"},
                {"name": "unused", "kind": "dev", "req": "*"}]}],
            "b": [{"vers": "1.0.0"}, {"vers": "1.1.0", "yanked": True},
                  {"vers": "2.0.0"}],
        }
        self.assertEqual(registry.dependencies("a@1.0.0"), ["b@1.0.0"])
        self.assertEqual(registry.dependencies("a@1.0.0", "b"), [])
        with self.assertRaises(ValueError):
            registry.record("a", "9.0.0")
