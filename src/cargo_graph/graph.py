"""Recursive breadth-first traversal by whole frontiers."""

import json
from pathlib import Path
import re


class TestRepository:
    """Strict uppercase adjacency-list fixture, version-independent."""

    def __init__(self, filename):
        self.graph = json.loads(Path(filename).read_text(encoding="utf-8"))
        if not isinstance(self.graph, dict):
            raise ValueError("Test repository must be a JSON object")
        for name, children in self.graph.items():
            if not re.fullmatch(r"[A-Z]+", name):
                raise ValueError(f"Invalid test package: {name}")
            if not isinstance(children, list):
                raise ValueError(f"Expected dependency list: {name}")
            for child in children:
                if not isinstance(child, str) or child not in self.graph:
                    raise ValueError(f"Unknown dependency of {name}: {child}")

    def dependencies(self, node, exclude=""):
        """Return filtered children, rejecting an unknown starting node."""
        if node not in self.graph:
            raise ValueError(f"Unknown test package: {node}")
        return sorted({child for child in self.graph[node]
                       if not exclude or exclude not in child})


def build_graph(root, dependencies, max_depth, exclude=""):
    """Return adjacency and minimum distances using recursive BFS.

    One recursive call processes one complete depth level. Visited nodes
    are marked on discovery, so cycles and diamonds terminate correctly.
    Boundary vertices are retained without fetching their dependencies.
    """
    if exclude and exclude in root.split("@", 1)[0]:
        return {}, {}
    graph, depths = {root: []}, {root: 0}

    def visit(frontier, depth):
        """Expand one frontier, then recurse to the next BFS level."""
        if not frontier or depth >= max_depth:
            return
        following = []
        for node in frontier:
            children = dependencies(node, exclude)
            graph[node] = sorted(set(children))
            for child in graph[node]:
                if child not in depths:
                    depths[child] = depth + 1
                    graph[child] = []
                    following.append(child)
        visit(following, depth + 1)

    visit([root], 0)
    return graph, depths
