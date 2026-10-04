#!/usr/bin/env python3
"""Camera-free test double for the tca-v4l2 process pipeline.

This program implements only the capture arguments used by scripts/tca-v4l2.
It never imports a USB interface library, opens a USB device, or sends a
control transfer.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import signal
import sys
import time


FRAME_BYTES = 1280 * 960
PREFIX_BYTES = 512
stop_requested = False


def request_stop(_signum: int, _frame: object) -> None:
    global stop_requested
    stop_requested = True


def new_binary(path: str):
    if path == "-":
        return sys.stdout.buffer, False
    return open(path, "xb"), True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    capture = subparsers.add_parser("capture")
    capture.add_argument("--frames", type=int, required=True)
    capture.add_argument("--raw-first", required=True)
    capture.add_argument("--bayer", required=True)
    capture.add_argument("--timestamps")
    capture.add_argument("--exposure-ms", type=int, required=True)
    capture.add_argument("--gain", type=int, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.frames < 0:
        raise SystemExit("--frames must be nonnegative")
    if not 1 <= args.exposure_ms <= 480 or not 0 <= args.gain <= 320:
        raise SystemExit("synthetic control value outside mode-2 range")
    if args.raw_first == "-" or pathlib.Path(args.raw_first).exists():
        raise SystemExit("--raw-first must name a new regular file")
    if args.timestamps and (
        args.timestamps == "-"
        or args.timestamps == args.raw_first
        or pathlib.Path(args.timestamps).exists()
    ):
        raise SystemExit("--timestamps must name a distinct new regular file")

    delay_ms = int(os.environ.get("TCA_FAKE_FRAME_DELAY_MS", "0"))
    if not 0 <= delay_ms <= 1000:
        raise SystemExit("TCA_FAKE_FRAME_DELAY_MS must be in 0..1000")

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    first_frame = bytes([60]) * FRAME_BYTES
    with open(args.raw_first, "xb") as raw:
        raw.write(bytes([0x88]) * 10)
        raw.write(bytes(PREFIX_BYTES - 10))
        raw.write(first_frame)
        raw.flush()
        os.fsync(raw.fileno())

    output, close_output = new_binary(args.bayer)
    timestamps = open(args.timestamps, "x", encoding="ascii") if args.timestamps else None
    if timestamps:
        timestamps.write("frame,monotonic_ns\n")
        timestamps.flush()

    delivered = 0
    try:
        while not stop_requested and (args.frames == 0 or delivered < args.frames):
            frame = bytes([60 + delivered % 4]) * FRAME_BYTES
            try:
                output.write(frame)
                output.flush()
            except BrokenPipeError:
                break
            if timestamps:
                timestamps.write(f"{delivered},{time.monotonic_ns()}\n")
                timestamps.flush()
            delivered += 1
            if delay_ms:
                time.sleep(delay_ms / 1000)
    finally:
        if timestamps:
            timestamps.close()
        if close_output:
            output.close()
    print(f"frames={delivered} status=ok synthetic=true", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
