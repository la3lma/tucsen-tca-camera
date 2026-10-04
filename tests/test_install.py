#!/usr/bin/env python3
"""Exercise staged install and exact-file uninstall behavior."""

from __future__ import annotations

import pathlib
import stat
import subprocess
import sys
import tempfile


PROGRAMS = ("tca-camera", "tca-v4l2", "tca-frame-stats",
            "tca-white-balance")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} REPOSITORY")
    repository = pathlib.Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="tca-install-") as directory:
        destination = pathlib.Path(directory)
        make_arguments = [
            "make",
            f"DESTDIR={destination}",
            "PREFIX=/usr/local",
        ]
        subprocess.run(
            [*make_arguments, "install"], cwd=repository, check=True
        )
        binary_directory = destination / "usr" / "local" / "bin"
        installed = [binary_directory / program for program in PROGRAMS]
        for program in installed:
            mode = program.stat().st_mode
            assert stat.S_ISREG(mode)
            assert mode & stat.S_IXUSR

        sentinel = binary_directory / "unrelated-program"
        sentinel.write_text("must remain\n", encoding="utf-8")
        subprocess.run(
            [*make_arguments, "uninstall"], cwd=repository, check=True
        )
        assert all(not program.exists() for program in installed)
        assert sentinel.read_text(encoding="utf-8") == "must remain\n"
    print("TCA staged install/uninstall checks: PASS")


if __name__ == "__main__":
    main()
