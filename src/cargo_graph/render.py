"""Deterministic D2 source output; rendering is an optional external step."""

import json


def to_d2(graph):
    """Encode labels as JSON strings and use safe synthetic D2 IDs."""
    names = sorted(graph)
    identifiers = {name: f"n{index}" for index, name in enumerate(names)}
    lines = ["direction: right"]
    for name in names:
        label = json.dumps(name, ensure_ascii=False)
        lines.append(f"{identifiers[name]}: {label}")
    for parent in names:
        for child in sorted(set(graph[parent])):
            lines.append(f"{identifiers[parent]} -> {identifiers[child]}")
    return "\n".join(lines)
