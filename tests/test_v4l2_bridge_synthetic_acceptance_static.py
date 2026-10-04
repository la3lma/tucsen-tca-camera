#!/usr/bin/env python3
"""Static and inert checks for the camera-free V4L2 lifecycle harness."""

from __future__ import annotations

import pathlib
import subprocess
import sys


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} HARNESS")
    harness = pathlib.Path(sys.argv[1]).resolve()
    source = harness.read_text(encoding="utf-8")
    subprocess.run(["sh", "-n", str(harness)], check=True)
    inert = subprocess.run(
        [str(harness)], check=True, capture_output=True, text=True
    )
    assert "transfer=none system_change=none" in inert.stdout
    assert "NO USB TRANSFER SENT. NO SYSTEM CHANGE MADE." in inert.stdout

    required = (
        "--run-v4l2-bridge-synthetic-acceptance",
        'TCA_CAMERA_READER="$fake_reader"',
        'TCA_FLAT_FIELD="$output_dir/uniform.tca-flat"',
        'TCA_TIMESTAMPS="$output_dir/reader-timestamps.csv"',
        "--stream-sleep=count=1,sleep=350,mode=1",
        "consumer_detach_reattach=pass",
        "bridge_tree_rss_growth_kib",
        "module_cleanup=pass",
        "manifest.sha256",
        "usb_transfer=none",
    )
    for token in required:
        assert token in source, token

    forbidden = (
        "build/tca-camera",
        "libusb_control_transfer",
        "libusb_bulk_transfer",
        "usb_modeswitch",
        "authorized=0",
        "authorized=1",
        "--set-configuration",
        "modprobe -r usb",
    )
    for token in forbidden:
        assert token not in source, token

    print("V4L2 bridge synthetic lifecycle harness checks: PASS")


if __name__ == "__main__":
    main()
