"""Stable Cargo version requirements without external dependencies."""

import re

PARTS = 3


def version_tuple(text):
    """Parse a stable version; prereleases are deliberately unsupported."""
    core = text.split("+", 1)[0]
    if not re.fullmatch(r"\d+\.\d+\.\d+", core):
        raise ValueError(f"Unsupported stable version: {text}")
    return tuple(map(int, core.split(".")))


def upper_bound(parts, operator):
    """Return the exclusive upper bound for caret or tilde."""
    padded = tuple(parts) + (0,) * (PARTS - len(parts))
    if operator == "~":
        pivot = min(len(parts) - 1, 1)
    else:
        pivot = next((i for i, n in enumerate(parts) if n), len(parts) - 1)
    return padded[:pivot] + (padded[pivot] + 1,) + (0,) * (2 - pivot)


def matches_clause(version, clause):
    """Match one stable comparator, wildcard, caret or tilde clause."""
    match = re.fullmatch(r"\s*(>=|<=|>|<|=|\^|~)?\s*([\d.*xX]+)\s*", clause)
    if not match:
        raise ValueError(f"Unsupported version requirement: {clause}")
    operator, text = match.groups()
    tokens = text.split(".")
    if len(tokens) > PARTS:
        raise ValueError(f"Invalid version requirement: {clause}")
    if any(token in {"*", "x", "X"} for token in tokens):
        pivot = next(i for i, token in enumerate(tokens)
                     if token in {"*", "x", "X"})
        if operator or any(t not in {"*", "x", "X"}
                           for t in tokens[pivot:]):
            raise ValueError(f"Invalid wildcard: {clause}")
        return version[:pivot] == tuple(map(int, tokens[:pivot]))
    parts = tuple(map(int, tokens))
    lower = parts + (0,) * (PARTS - len(parts))
    if operator in {">", ">=", "<", "<=", "="}:
        actual = version[:len(parts)]
        return {">": actual > parts, ">=": actual >= parts,
                "<": actual < parts, "<=": actual <= parts,
                "=": actual == parts}[operator]
    return lower <= version < upper_bound(parts, operator)


def satisfies(version, requirement):
    """Match comma-separated Cargo requirements for stable versions."""
    parsed = version_tuple(version)
    return all(matches_clause(parsed, part)
               for part in requirement.split(","))
