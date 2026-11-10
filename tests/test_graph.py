"""Graph topology and traversal-order regression tests."""

import unittest
from cargo_graph.graph import build_graph


class GraphTests(unittest.TestCase):
    """Exercise cycles, breadth-first order, boundaries and filtering."""

    def setUp(self):
        self.data = {"A": ["B", "C"], "B": ["D"],
                     "C": ["D", "E"], "D": ["A"], "E": []}
        self.calls = []

    def dependencies(self, node, exclude):
        self.calls.append(node)
        return [n for n in self.data[node] if not exclude or exclude not in n]

    def test_bfs_cycle_diamond(self):
        graph, depths = build_graph("A", self.dependencies, 10)
        self.assertEqual(self.calls, ["A", "B", "C", "D", "E"])
        self.assertEqual(depths["D"], 2)
        self.assertEqual(graph["D"], ["A"])

    def test_depth_zero(self):
        self.assertEqual(build_graph("A", self.dependencies, 0),
                         ({"A": []}, {"A": 0}))
        self.assertEqual(self.calls, [])

    def test_depth_one(self):
        graph, depths = build_graph("A", self.dependencies, 1)
        self.assertEqual(graph, {"A": ["B", "C"], "B": [], "C": []})
        self.assertEqual(self.calls, ["A"])

    def test_filter(self):
        graph, _ = build_graph("A", self.dependencies, 10, "C")
        self.assertNotIn("C", graph)
        self.assertNotIn("E", graph)
        self.assertEqual(build_graph("A", self.dependencies, 10, "A"),
                         ({}, {}))

    def test_self_loop(self):
        graph, _ = build_graph("X", lambda *_: ["X"], 200)
        self.assertEqual(graph, {"X": ["X"]})

    def test_wide_frontier(self):
        data = {"A": [str(i) for i in range(1500)]}
        graph, _ = build_graph("A", lambda n, _: data.get(n, []), 200)
        self.assertEqual(len(graph), 1501)
