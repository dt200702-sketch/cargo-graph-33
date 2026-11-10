"""Command-line entry point."""

import argparse
import configparser
from dataclasses import asdict
import sys

from .config import load_config


def main(argv=None):
    """Run stage one and return a process exit code."""
    parser = argparse.ArgumentParser(description="Cargo graph, variant 33")
    parser.add_argument("config", help="path to an INI configuration")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        for key, value in asdict(config).items():
            print(f"{key}={value}")
    except (OSError, ValueError, configparser.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
