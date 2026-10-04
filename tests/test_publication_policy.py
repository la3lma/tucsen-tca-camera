#!/usr/bin/env python3
"""Enforce the public/private reverse-engineering artifact boundary."""

from __future__ import annotations

import pathlib
import subprocess
import sys


BANNED_COMPONENTS = {
    "analysis",
    "ghidra",
    "private",
    "vendor-extracted",
    "vendor-static",
    "vendor-zips",
    "work",
}
BANNED_SUFFIXES = {
    ".7z", ".bin", ".bndb", ".cab", ".cat", ".dll", ".etl", ".exe",
    ".fw", ".gpr", ".gzf", ".hex", ".i64", ".idb", ".msi", ".pcap",
    ".pcapng", ".rar", ".rep", ".sys", ".zip",
}
BANNED_NAME_FRAGMENTS = (
    ".disasm",
    ".functions.tsv",
    ".headers.txt",
    ".strings.txt",
)


def reason(path_text: str) -> str | None:
    path = pathlib.PurePosixPath(path_text)
    lowered_parts = {part.lower() for part in path.parts}
    if lowered_parts & BANNED_COMPONENTS:
        return "private work/analysis path"
    name = path.name.lower()
    if pathlib.PurePosixPath(name).suffix in BANNED_SUFFIXES:
        return "forbidden raw/proprietary artifact suffix"
    if any(fragment in name for fragment in BANNED_NAME_FRAGMENTS):
        return "forbidden disassembly/export filename"
    return None


def git_output(root: pathlib.Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=True, capture_output=True, text=True
    ).stdout


def check_paths(paths: set[str], label: str) -> None:
    violations = [(path, reason(path)) for path in sorted(paths) if reason(path)]
    assert not violations, f"{label} contains prohibited public artifacts: {violations}"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} PROJECT_ROOT")
    root = pathlib.Path(sys.argv[1]).resolve()
    policy = (root / "PUBLICATION_POLICY.md").read_text(encoding="utf-8")
    for token in (
        "disassembly listings",
        "Ghidra projects/databases",
        "vendor executables",
        "raw packet captures",
        "Never weaken the denylist",
    ):
        assert token in policy, f"publication policy missing {token!r}"

    if (root / ".git").exists():
        tracked = set(git_output(root, "ls-files").splitlines())
        check_paths(tracked, "tracked tree")
        shallow = git_output(root, "rev-parse", "--is-shallow-repository").strip()
        if shallow == "false":
            history = set()
            for line in git_output(root, "rev-list", "--objects", "--all").splitlines():
                fields = line.split(" ", 1)
                if len(fields) == 2:
                    history.add(fields[1])
            check_paths(history, "public Git history")
        else:
            print("publication policy: history audit skipped in shallow checkout")
    else:
        candidates = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and "build" not in path.relative_to(root).parts
        }
        check_paths(candidates, "source archive")
    print("Public/private publication boundary checks: PASS")


if __name__ == "__main__":
    main()
