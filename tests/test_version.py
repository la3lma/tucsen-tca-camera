#!/usr/bin/env python3
"""Keep the source, CLI, and Debian package version surfaces consistent."""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys


UPSTREAM_PATTERN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+-alpha\.[0-9]+")
DEBIAN_PATTERN = re.compile(r"([0-9]+\.[0-9]+\.[0-9]+)~alpha([0-9]+)-1")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} REPOSITORY BINARY")
    repository = pathlib.Path(sys.argv[1]).resolve()
    binary = pathlib.Path(sys.argv[2]).resolve()
    upstream = (repository / "VERSION").read_text(encoding="utf-8").strip()
    debian = (repository / "packaging" / "debian" / "version").read_text(
        encoding="utf-8"
    ).strip()

    assert UPSTREAM_PATTERN.fullmatch(upstream), upstream
    match = DEBIAN_PATTERN.fullmatch(debian)
    assert match, debian
    expected_debian_upstream = f"{match.group(1)}-alpha.{match.group(2)}"
    assert upstream == expected_debian_upstream, (upstream, debian)

    reported = subprocess.run(
        [str(binary), "--version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert reported == f"tca-camera {upstream}", reported
    print(f"TCA version surfaces agree: {upstream} / {debian}")


if __name__ == "__main__":
    main()
