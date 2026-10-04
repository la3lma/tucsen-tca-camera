#!/usr/bin/env python3
"""Offline checks for tca-timing-stats."""

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
    with tempfile.TemporaryDirectory(prefix="tca-timing-stats-") as directory:
        root = pathlib.Path(directory)
        timestamps = root / "timestamps.csv"
        timestamps.write_text(
            "frame,monotonic_ns\n"
            "1,1000000000\n"
            "2,1100000000\n"
            "3,1220000000\n"
            "4,1330000000\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [str(script), str(timestamps)],
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(completed.stdout)
        assert report["schema"] == "tca-timing-stats-v1"
        assert report["clock"] == "CLOCK_MONOTONIC"
        assert report["frame_count"] == 4
        assert report["interval_count"] == 3
        assert report["duration_seconds"] == 0.33
        assert abs(report["delivered_fps"] - 9.0909090909) < 1e-9
        assert report["interval_ms"]["min"] == 100.0
        assert report["interval_ms"]["p50"] == 110.0
        assert report["interval_ms"]["p95"] == 120.0
        assert report["interval_ms"]["max"] == 120.0

        report_path = root / "report.json"
        subprocess.run(
            [str(script), str(timestamps), "--json", str(report_path)],
            check=True,
        )
        assert json.loads(report_path.read_text(encoding="utf-8")) == report
        overwrite = subprocess.run(
            [str(script), str(timestamps), "--json", str(report_path)],
            capture_output=True,
            text=True,
        )
        assert overwrite.returncode == 73

        for name, contents, expected in (
            ("bad-header.csv", "frame,time\n1,1\n2,2\n", "exact"),
            ("gap.csv", "frame,monotonic_ns\n1,1\n3,2\n", "expected 2"),
            ("backward.csv", "frame,monotonic_ns\n1,2\n2,1\n", "strictly"),
            ("short.csv", "frame,monotonic_ns\n1,1\n", "at least two"),
        ):
            candidate = root / name
            candidate.write_text(contents, encoding="utf-8")
            rejected = subprocess.run(
                [str(script), str(candidate)], capture_output=True, text=True
            )
            assert rejected.returncode == 64
            assert expected in rejected.stderr
    print("TCA timestamp statistics checks: PASS")


if __name__ == "__main__":
    main()
