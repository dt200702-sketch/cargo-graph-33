"""Configuration validation tests."""

from dataclasses import replace
from pathlib import Path
import unittest

from cargo_graph.config import load_config, validate

ROOT = Path(__file__).resolve().parents[1]


class ConfigTests(unittest.TestCase):
    """Check all configurable parameters."""

    def setUp(self):
        self.config = load_config(ROOT / "examples/test.ini")

    def test_valid(self):
        self.assertEqual(self.config.package, "A")
        self.assertTrue(Path(self.config.repository).is_absolute())

    def test_invalid_values(self):
        cases = {"package": "../x", "version": "latest",
                 "max_depth": -1, "repository": "missing",
                 "exclude": "a\nb"}
        for field, value in cases.items():
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(replace(self.config, **{field: value}))

    def test_network_url(self):
        config = replace(self.config, test_mode=False)
        with self.assertRaises(ValueError):
            validate(config)
        config = replace(config, repository="https://index.crates.io")
        self.assertEqual(validate(config), config)
