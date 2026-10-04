#!/usr/bin/env python3
"""Deterministic calibration and stream checks for tca-flat-field."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


CHANNELS = (("g1", "r"), ("b", "g2"))  # GRBG
BASE = {"r": 80, "g1": 100, "g2": 100, "b": 60}
EXPECTED = {"r": 40, "g1": 50, "g2": 50, "b": 30}


def synthetic_flat(width: int, height: int, dark: int) -> bytes:
    result = bytearray()
    for y in range(height):
        for x in range(width):
            channel = CHANNELS[y & 1][x & 1]
            # Each Bayer parity sees one shaded and one fully lit tile column.
            signal = BASE[channel] // 2 if x < 2 else BASE[channel]
            result.append(dark + signal)
    return bytes(result)


def expected_corrected(width: int, height: int) -> bytes:
    return bytes(
        EXPECTED[CHANNELS[y & 1][x & 1]]
        for y in range(height)
        for x in range(width)
    )


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} BINARY")
    binary = pathlib.Path(sys.argv[1]).resolve()
    width, height = 4, 4
    with tempfile.TemporaryDirectory(prefix="tca-flat-field-") as directory:
        root = pathlib.Path(directory)
        darks = root / "darks.bayer"
        flats = root / "flats.bayer"
        calibration = root / "calibration.tca-flat"
        input_path = root / "input.bayer"
        output_path = root / "output.bayer"
        darks.write_bytes(bytes([9]) * 16 + bytes([11]) * 16)
        flat = synthetic_flat(width, height, 10)
        flats.write_bytes(flat + flat)
        subprocess.run(
            [
                str(binary), "calibrate", "--width", str(width),
                "--height", str(height), "--phase", "grbg",
                "--dark", str(darks), "--dark-frames", "2",
                "--flat", str(flats), "--flat-frames", "2",
                "--output", str(calibration),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert calibration.stat().st_size == 64 + width * height * 4
        inspected = subprocess.run(
            [str(binary), "inspect", "--calibration", str(calibration)],
            check=True,
            capture_output=True,
            text=True,
        )
        metadata = json.loads(inspected.stdout)
        assert metadata["format"] == "tcaff01"
        assert metadata["width"] == width and metadata["height"] == height
        assert metadata["phase"] == "grbg"
        assert metadata["dark_frames"] == 2
        assert metadata["flat_frames"] == 2

        input_path.write_bytes(flat + flat)
        applied = subprocess.run(
            [
                str(binary), "apply", "--calibration", str(calibration),
                "--input", str(input_path), "--output", str(output_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert "frames=2" in applied.stderr and "status=ok" in applied.stderr
        assert output_path.read_bytes() == expected_corrected(width, height) * 2

        truncated = subprocess.run(
            [
                str(binary), "apply", "--calibration", str(calibration),
                "--input", "-", "--output", "-",
            ],
            input=flat[:-1],
            capture_output=True,
        )
        assert truncated.returncode != 0
        assert b"truncated Bayer frame" in truncated.stderr
        assert truncated.stdout == b""

        refuses_overwrite = subprocess.run(
            [
                str(binary), "apply", "--calibration", str(calibration),
                "--input", str(input_path), "--output", str(output_path),
            ],
            capture_output=True,
            text=True,
        )
        assert refuses_overwrite.returncode != 0
        assert output_path.read_bytes() == expected_corrected(width, height) * 2
    print("TCA flat-field calibration and stream checks: PASS")


if __name__ == "__main__":
    main()
