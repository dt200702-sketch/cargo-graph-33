"""Read and resolve raw Cargo sparse-index records via HTTP."""

import json
import re
from urllib.request import Request, urlopen

from .semver import satisfies, version_tuple

TIMEOUT = 30
MAX_RESPONSE = 32 * 1024 * 1024


def index_path(name):
    """Compute the path mandated by the Cargo sparse-index format."""
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", name):
        raise ValueError(f"Invalid package name: {name}")
    name = name.lower()
    if len(name) <= 2:
        return f"{len(name)}/{name}"
    if len(name) == 3:
        return f"3/{name[0]}/{name}"
    return f"{name[:2]}/{name[2:4]}/{name}"


class Registry:
    """Cache records; include all declared normal/build dependencies.

    Optional dependencies and all target platforms are included. This is
    a declaration graph, not a feature-aware Cargo build plan.
    """

    def __init__(self, url):
        self.url = url.rstrip("/")
        self.cache = {}

    def records(self, name):
        """Fetch raw newline-delimited JSON without a package manager."""
        if name not in self.cache:
            request = Request(
                f"{self.url}/{index_path(name)}",
                headers={"User-Agent": "cargo-graph-33/1.0 (educational)"},
            )
            with urlopen(request, timeout=TIMEOUT) as response:
                payload = response.read(MAX_RESPONSE + 1)
            if len(payload) > MAX_RESPONSE:
                raise ValueError("Registry response exceeds size limit")
            records = [json.loads(line) for line in payload.splitlines()
                       if line.strip()]
            if not records or any(not isinstance(r, dict) for r in records):
                raise ValueError(f"Invalid index records for {name}")
            self.cache[name] = records
        return self.cache[name]

    def record(self, name, version):
        """Find the exact requested root/dependency version."""
        for record in self.records(name):
            if record.get("vers") == version:
                if not isinstance(record.get("deps"), list):
                    raise ValueError(f"Invalid dependency list for {name}")
                return record
        raise ValueError(f"Version not found: {name}@{version}")

    def resolve(self, name, requirement):
        """Select the newest non-yanked stable matching version."""
        candidates = []
        for record in self.records(name):
            version = record.get("vers", "")
            if record.get("yanked") or "-" in version:
                continue
            if satisfies(version, requirement):
                candidates.append(version)
        if not candidates:
            raise ValueError(f"No stable version: {name} {requirement}")
        return max(candidates, key=version_tuple)

    def dependencies(self, node, exclude=""):
        """Resolve declared dependencies, filtering before network access."""
        name, version = node.rsplit("@", 1)
        result = set()
        for dep in self.record(name, version)["deps"]:
            target = dep.get("package") or dep["name"]
            if dep.get("kind") == "dev" or (exclude and exclude in target):
                continue
            if dep.get("registry"):
                raise ValueError("Cross-registry dependencies unsupported")
            resolved = self.resolve(target, dep["req"])
            result.add(f"{target}@{resolved}")
        return sorted(result)
