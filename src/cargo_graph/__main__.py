"""Command-line entry point with clean stdout and actionable errors."""

import argparse
import configparser
from dataclasses import asdict
import json
import sys

from .config import load_config
from .graph import TestRepository, build_graph, reverse_dependencies
from .registry import Registry


def execute(config, mode, target=None):
    """Dispatch configuration, direct dependency and graph operations."""
    if mode == "config":
        return "\n".join(f"{k}={v}" for k, v in asdict(config).items())
    if config.test_mode:
        source = TestRepository(config.repository)
        root = config.package
        if root not in source.graph:
            raise ValueError(f"Unknown test package: {root}")
    else:
        source = Registry(config.repository)
        root = f"{config.package}@{config.version}"
        source.record(config.package, config.version)
    if mode == "direct":
        return "\n".join(source.dependencies(root, config.exclude))
    graph, depths = build_graph(root, source.dependencies,
                                config.max_depth, config.exclude)
    if mode == "reverse":
        scope = source.graph if config.test_mode else graph
        result = reverse_dependencies(scope, target or root,
                                      config.max_depth, config.exclude)
        return json.dumps(result, indent=2)
    return json.dumps({"graph": graph, "depths": depths}, indent=2)


def main(argv=None):
    """Run an operation; return 2 for invalid input or unavailable data."""
    parser = argparse.ArgumentParser(description="Cargo graph, variant 33")
    parser.add_argument("config", help="path to an INI configuration")
    parser.add_argument("--mode", choices=["config", "direct", "graph",
                                                 "reverse"],
                        default="graph")
    parser.add_argument("--target", help="reverse target: A or name@version")
    args = parser.parse_args(argv)
    try:
        result = execute(load_config(args.config), args.mode, args.target)
        print(result)
    except (OSError, ValueError, configparser.Error, KeyError,
            TypeError, RecursionError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
