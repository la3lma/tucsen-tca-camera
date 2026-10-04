#!/usr/bin/env python3
"""Inert/static checks for the synthetic flat-field V4L2 preflight."""

from __future__ import annotations

import pathlib
import subprocess
import sys


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} SCRIPT")
    script = pathlib.Path(sys.argv[1]).resolve()
    source = script.read_text(encoding="utf-8")
    subprocess.run(["sh", "-n", str(script)], check=True)
    inert = subprocess.run(["sh", str(script)], capture_output=True, text=True)
    assert inert.returncode == 0
    assert "NO USB TRANSFER SENT. NO SYSTEM CHANGE MADE." in inert.stderr
    assert "--run-flat-field-v4l2-preflight" in source
    assert "build/tca-flat-field" in source
    assert "v4l2loopback" in source
    assert "libusb" not in source
    assert "tca-camera capture" not in source
    print("TCA flat-field V4L2 preflight static/inert checks: PASS")


if __name__ == "__main__":
    main()
