#!/usr/bin/env python3
"""Inert/static checks for the trace-confirmed V4L2 adapter."""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} SCRIPT")
    script = pathlib.Path(sys.argv[1]).resolve()
    source = script.read_text(encoding="utf-8")
    subprocess.run(["sh", "-n", str(script)], check=True)
    inert = subprocess.run(["sh", str(script)], capture_output=True, text=True)
    assert inert.returncode == 0
    assert "NO USB TRANSFER SENT" in inert.stderr
    assert "bayer_grbg8" in source
    assert "v4l2loopback" in source
    assert "build/tca-camera" in source
    assert "TCA_FLAT_FIELD" in source
    assert "TCA_TIMESTAMPS" in source
    assert '--timestamps "$timestamps"' in source
    assert "reader timestamp sidecar active" in source
    assert "TCA_TIMESTAMPS must name a distinct new regular file" in source
    assert '"$flat_field_tool" apply --calibration "$flat_field"' in source
    assert "raw-bayer.fifo" in source
    assert "flat-field calibration must be 1280x960 GRBG for V4L2" in source
    assert "flat-field exposure/gain must match" in source
    assert '\\"exposure_ms\\": $exposure_ms,' in source
    assert '\\"camera_gain\\": $gain,' in source
    assert "libusb_control_transfer" not in source
    with tempfile.TemporaryDirectory(prefix="tca-v4l2-inert-") as directory:
        raw = pathlib.Path(directory, "must-not-exist.raw")
        invalid = subprocess.run(
            ["sh", str(script), "--serve", str(raw),
             "42", "481", "20"],
            capture_output=True,
            text=True,
        )
        assert invalid.returncode == 64
        assert not raw.exists()
        timestamp_conflict = subprocess.run(
            ["sh", str(script), "--serve", str(raw), "42", "100", "20"],
            capture_output=True,
            text=True,
            env={**dict(os.environ), "TCA_TIMESTAMPS": str(raw)},
        )
        assert timestamp_conflict.returncode == 73
        assert "distinct new regular file" in timestamp_conflict.stderr
        assert not raw.exists()
    print("TCA live V4L2 adapter static/inert checks: PASS")


if __name__ == "__main__":
    main()
