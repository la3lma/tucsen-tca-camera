#!/usr/bin/env python3
"""Offline checks for tca-frame-stats."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} SCRIPT")
    script = pathlib.Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="tca-frame-stats-") as directory:
        root = pathlib.Path(directory)
        frame = root / "synthetic.bayer"
        values = bytearray()
        for row in range(6):
            for column in range(6):
                values.append(((row & 1) * 2 + (column & 1) + 1) * 10)
        frame.write_bytes(values)

        completed = subprocess.run(
            [str(script), str(frame), "--width", "6", "--height", "6"],
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(completed.stdout)
        assert report["schema"] == "tca-frame-stats-v1"
        assert report["mode"] is None
        assert report["bytes"] == 36
        assert report["intensity"]["mean"] == 25.0
        assert report["parity"]["row0_col0"]["mean"] == 10.0
        assert report["parity"]["row0_col1"]["mean"] == 20.0
        assert report["parity"]["row1_col0"]["mean"] == 30.0
        assert report["parity"]["row1_col1"]["mean"] == 40.0
        assert report["focus"]["value"] == 0.0
        assert report["focus"]["samples"] == 1
        assert report["candidate_phase_maps"]["grbg"] == [
            ["G", "R"],
            ["B", "G"],
        ]

        wrong = subprocess.run(
            [str(script), str(frame), "--width", "7", "--height", "6"],
            capture_output=True,
            text=True,
        )
        assert wrong.returncode == 64
        assert "does not match" in wrong.stderr

        report_path = root / "report.json"
        subprocess.run(
            [
                str(script),
                str(frame),
                "--width",
                "6",
                "--height",
                "6",
                "--json",
                str(report_path),
            ],
            check=True,
        )
        assert json.loads(report_path.read_text())["sha256"] == report["sha256"]
        refuses_overwrite = subprocess.run(
            [
                str(script),
                str(frame),
                "--width",
                "6",
                "--height",
                "6",
                "--json",
                str(report_path),
            ],
            capture_output=True,
            text=True,
        )
        assert refuses_overwrite.returncode == 73
    print("TCA Bayer frame statistics checks: PASS")


if __name__ == "__main__":
    main()
