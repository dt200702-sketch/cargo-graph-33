"""Reverse reachability, cycle and depth tests."""

import unittest
from cargo_graph.graph import reverse_dependencies


class ReverseTests(unittest.TestCase):
    """Check inverse BFS on a complete fixture."""

    def test_transitive_and_disconnected(self):
        graph = {"A": ["B"], "B": ["C"], "C": [], "D": []}
        self.assertEqual(reverse_dependencies(graph, "C", 10),
                         {"B": 1, "A": 2})
        self.assertEqual(reverse_dependencies(graph, "C", 1), {"B": 1})
        self.assertEqual(reverse_dependencies(graph, "D", 10), {})

    def test_cycle(self):
        graph = {"A": ["B"], "B": ["A"]}
        self.assertEqual(reverse_dependencies(graph, "A", 10), {"B": 1})

    def test_absent(self):
        with self.assertRaises(ValueError):
            reverse_dependencies({"A": []}, "B", 2)

    def test_filter(self):
        graph = {"A": ["B"], "B": ["C"], "C": []}
        self.assertEqual(reverse_dependencies(graph, "C", 10, "B"), {})
