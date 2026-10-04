#!/usr/bin/env python3
"""Static and inert checks for the live Linux V4L2 acceptance harness."""

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
    assert "harness=dry-run target=0547:c003 transfer=none" in inert.stdout
    assert "NO USB TRANSFER SENT" in inert.stdout

    rejected = subprocess.run(
        [str(harness), "--wrong-token", "/no/release", "/no/map", "/no/evidence"],
        capture_output=True,
        text=True,
    )
    assert rejected.returncode == 64
    assert "NO USB TRANSFER SENT" in rejected.stderr

    required = (
        "--run-live-linux-v4l2-acceptance",
        "TCA_FLAT_FIELD=\"$calibration\" TCA_TIMESTAMPS=\"$timestamps\"",
        "profile=tca-linux-v4l2-acceptance-v2",
        "reader-timestamps.csv",
        "consumer.yuyv",
        "consumer.framemd5",
        "producer-consumer-summary.txt",
        "producer_minus_consumer",
        "not by itself a proven drop count",
        "bridge-exit-status.txt",
        "reopen-one-frame.bayer",
        "manifest.sha256",
        "sudo -n true",
        "release worktree must be clean",
        "expected exactly one 0547:c003 camera",
        "MODE must be 0 or 2",
        "width=3664",
        "height=2748",
        "yuyv_frame_bytes=20137344",
        '"$exposure_ms" "$gain" "$mode"',
        '--mode "$mode"',
        'geometry=%sx%s',
        "linux_v4l2_acceptance=PASS",
    )
    for token in required:
        assert token in source, token

    forbidden = (
        "libusb_reset_device",
        "usb_modeswitch",
        "authorized=0",
        "authorized=1",
        "--set-configuration",
        "modprobe -r usb",
    )
    for token in forbidden:
        assert token not in source, token

    print("Linux V4L2 live acceptance harness checks: PASS")


if __name__ == "__main__":
    main()
