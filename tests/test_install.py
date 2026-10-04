#!/usr/bin/env python3
"""Exercise staged install and exact-file uninstall behavior."""

from __future__ import annotations

import pathlib
import stat
import subprocess
import sys
import tempfile


PROGRAMS = ("tca-camera", "tca-v4l2", "tca-ffmpeg", "tca-frame-stats",
            "tca-timing-stats", "tca-white-balance", "tca-flat-field")


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

        bridge = binary_directory / "tca-v4l2"
        diagnostic = subprocess.run(
            [str(bridge), "--diagnose-install"],
            check=True,
            capture_output=True,
            text=True,
        )
        assert (
            f"reader={binary_directory / 'tca-camera'} executable=1"
            in diagnostic.stdout
        )
        assert (
            f"flat_field_tool={binary_directory / 'tca-flat-field'} executable=1"
            in diagnostic.stdout
        )
        assert "NO USB TRANSFER SENT" in diagnostic.stdout

        media_helper = binary_directory / "tca-ffmpeg"
        media_diagnostic = subprocess.run(
            [str(media_helper), "--diagnose-install"],
            check=True,
            capture_output=True,
            text=True,
        )
        assert (
            f"reader={binary_directory / 'tca-camera'} executable=1"
            in media_diagnostic.stdout
        )
        assert "NO USB TRANSFER SENT" in media_diagnostic.stdout

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
