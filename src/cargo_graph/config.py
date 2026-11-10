"""Strict INI configuration and user-facing validation."""

import configparser
from dataclasses import dataclass
from pathlib import Path
import re
from urllib.parse import urlparse

MAX_DEPTH = 200
NAME = r"[A-Za-z][A-Za-z0-9_-]{0,63}"
VERSION = r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"


@dataclass(frozen=True)
class Config:
    """Validated settings; repository paths are relative to the INI file."""

    package: str
    repository: str
    test_mode: bool
    version: str
    max_depth: int
    exclude: str


def validate(config):
    """Reject unsupported values before any network operation."""
    if not re.fullmatch(NAME, config.package):
        raise ValueError("package: invalid Cargo package name")
    if not re.fullmatch(VERSION, config.version):
        raise ValueError("version: expected a stable version X.Y.Z")
    if not 0 <= config.max_depth <= MAX_DEPTH:
        raise ValueError(f"max_depth: expected 0..{MAX_DEPTH}")
    if config.test_mode:
        if not re.fullmatch(r"[A-Z]+", config.package):
            raise ValueError("package: test names must be uppercase A-Z")
        if not Path(config.repository).is_file():
            raise ValueError("repository: test file does not exist")
    else:
        url = urlparse(config.repository)
        if url.scheme not in {"http", "https"} or not url.hostname:
            raise ValueError("repository: expected an HTTP(S) sparse index")
        if url.query or url.fragment or url.username or url.password:
            raise ValueError("repository: credentials/query are unsupported")
    if any(ord(char) < 32 for char in config.exclude):
        raise ValueError("exclude: control characters are forbidden")
    return config


def load_config(filename):
    """Read exactly six settings from the [graph] section."""
    path = Path(filename).resolve()
    parser = configparser.ConfigParser(interpolation=None)
    with path.open(encoding="utf-8") as stream:
        parser.read_file(stream)
    expected = set(Config.__dataclass_fields__)
    if parser.sections() != ["graph"] or parser.defaults():
        raise ValueError("config: expected only [graph], without DEFAULT")
    section = parser["graph"]
    if set(section) != expected:
        missing = sorted(expected - set(section))
        extra = sorted(set(section) - expected)
        raise ValueError(f"config: missing={missing}, unknown={extra}")
    repository = section["repository"].strip()
    test_mode = section.getboolean("test_mode")
    if test_mode and repository:
        repository = str((path.parent / repository).resolve())
    config = Config(
        section["package"].strip(), repository, test_mode,
        section["version"].strip(), section.getint("max_depth"),
        section["exclude"].strip(),
    )
    return validate(config)
