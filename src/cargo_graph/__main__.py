"""Command-line entry point."""

import argparse
import configparser
from dataclasses import asdict
import sys

from .config import load_config
from .registry import Registry


def main(argv=None):
    """Run stage one and return a process exit code."""
    parser = argparse.ArgumentParser(description="Cargo graph, variant 33")
    parser.add_argument("config", help="path to an INI configuration")
    parser.add_argument("--mode", choices=["config", "direct"],
                        default="direct")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.mode == "config":
            for key, value in asdict(config).items():
                print(f"{key}={value}")
        else:
            registry = Registry(config.repository)
            node = f"{config.package}@{config.version}"
            print("\n".join(registry.dependencies(node, config.exclude)))
    except (OSError, ValueError, configparser.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
