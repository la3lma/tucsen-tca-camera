#!/usr/bin/env python3
"""Verify the camera-free V4L2 reader test double."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


FRAME_BYTES = 1280 * 960
RAW_BYTES = FRAME_BYTES + 512


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} FAKE_READER")
    reader = pathlib.Path(sys.argv[1]).resolve()
    source = reader.read_text(encoding="utf-8")
    assert "libusb" not in source
    assert "USB" in source

    with tempfile.TemporaryDirectory(prefix="tca-fake-reader-") as directory:
        root = pathlib.Path(directory)
        raw = root / "first.raw"
        bayer = root / "two.bayer"
        timestamps = root / "timestamps.csv"
        run = subprocess.run(
            [
                str(reader),
                "capture",
                "--frames", "2",
                "--raw-first", str(raw),
                "--bayer", str(bayer),
                "--timestamps", str(timestamps),
                "--exposure-ms", "100",
                "--gain", "20",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert "synthetic=true" in run.stderr
        assert raw.stat().st_size == RAW_BYTES
        assert raw.read_bytes()[:10] == bytes([0x88]) * 10
        assert bayer.stat().st_size == 2 * FRAME_BYTES
        payload = bayer.read_bytes()
        assert payload[:FRAME_BYTES] == bytes([60]) * FRAME_BYTES
        assert payload[FRAME_BYTES:] == bytes([61]) * FRAME_BYTES
        rows = timestamps.read_text(encoding="ascii").splitlines()
        assert rows[0] == "frame,monotonic_ns"
        assert [row.split(",", 1)[0] for row in rows[1:]] == ["0", "1"]
        assert int(rows[2].split(",", 1)[1]) > int(rows[1].split(",", 1)[1])

    print("TCA camera-free reader test double: PASS")


if __name__ == "__main__":
    main()
