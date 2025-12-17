#!/usr/bin/env python3
"""
Small guard to ensure VERSION and pyproject.toml stay in sync.
"""

from __future__ import annotations

import pathlib
import sys
import tomllib


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    version_file = root / "VERSION"
    pyproject_file = root / "pyproject.toml"

    version = version_file.read_text().strip()
    pyproject = tomllib.loads(pyproject_file.read_text())
    py_version = pyproject.get("tool", {}).get("poetry", {}).get("version")

    if version != py_version:
        print(f"Version mismatch: VERSION={version!r} pyproject.toml={py_version!r}")
        return 1

    print(f"Versions match: {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
