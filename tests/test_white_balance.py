#!/usr/bin/env python3
"""Deterministic checks for tca-white-balance."""

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
    width, height = 8, 6
    phase = ((100, 50), (25, 100))  # GRBG: G, R / B, G
    frame = bytes(
        phase[y & 1][x & 1]
        for y in range(height)
        for x in range(width)
    )
    with tempfile.TemporaryDirectory(prefix="tca-white-balance-") as directory:
        path = pathlib.Path(directory, "frame.bayer")
        path.write_bytes(frame)
        result = subprocess.run(
            [
                str(script), str(path), "--width", str(width),
                "--height", str(height), "--phase", "grbg",
                "--max-samples", "1000",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        parsed = json.loads(result.stdout)
        assert parsed["medians"] == {
            "b": 25.0, "g1": 100.0, "g2": 100.0, "r": 50.0,
        }
        assert parsed["gains"] == {
            "blue": 4.0, "green": 1.0, "red": 2.0,
        }
        assert parsed["ffmpeg_gains"] == {
            "blue": 2.0, "green": 0.5, "red": 1.0,
        }
        assert parsed["ffmpeg_filter"] == (
            "colorchannelmixer=rr=1.000000:gg=0.500000:bb=2.000000"
        )
    print("TCA white-balance estimator checks: PASS")


if __name__ == "__main__":
    main()
