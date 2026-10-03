#!/usr/bin/env python3
"""Static and inert checks for the trace-confirmed Linux stream reader."""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile


ALLOWED = {
    "libusb_bulk_transfer",
    "libusb_claim_interface",
    "libusb_close",
    "libusb_control_transfer",
    "libusb_error_name",
    "libusb_exit",
    "libusb_init",
    "libusb_open_device_with_vid_pid",
    "libusb_release_interface",
}


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} BINARY SOURCE")
    binary = pathlib.Path(sys.argv[1]).resolve()
    source = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")
    symbols = subprocess.run(
        ["nm", "-u", str(binary)], check=True, capture_output=True, text=True
    ).stdout
    imports = set(re.findall(r"_?(libusb_[A-Za-z0-9_]+)", symbols))
    assert imports == ALLOWED, imports
    assert "TCA_DEVICE_BYTES 1229312u" in source
    assert "TCA_WIDTH 1280u" in source and "TCA_HEIGHT 960u" in source
    assert "524288u, 524288u, 180736u" in source
    assert "0u, 524288u, 1048576u" in source
    assert "TCA_MODE2_ROW_TIME_US 120u" in source
    assert "0x3012u" in source and "0x305eu" in source
    assert '"--exposure-ms"' in source and '"--gain"' in source
    assert 'perror("flush raw-first")' in source
    assert "fflush(raw_first)" in source
    assert "libusb_reset_device" not in source
    assert "libusb_set_configuration" not in source
    dry = subprocess.run([str(binary)], check=True, capture_output=True, text=True)
    assert "NO TRANSFER SENT" in dry.stdout
    with tempfile.TemporaryDirectory(prefix="tca-linux-stream-") as directory:
        raw = pathlib.Path(directory, "no.raw")
        bayer = pathlib.Path(directory, "no.bayer")
        invalid = subprocess.run(
            [str(binary), "--wrong-token", "--frames", "1", "--raw-first",
             str(raw), "--bayer", str(bayer)],
            capture_output=True,
            text=True,
        )
        assert invalid.returncode == 64
        assert not raw.exists() and not bayer.exists()
        out_of_range = subprocess.run(
            [str(binary), "capture", "--frames", "1",
             "--raw-first", str(raw), "--bayer", str(bayer),
             "--exposure-ms", "481"],
            capture_output=True,
            text=True,
        )
        assert out_of_range.returncode == 64
        assert "NO TRANSFER SENT" in out_of_range.stderr
        assert not raw.exists() and not bayer.exists()
    print("Linux stream reader static/inert checks: PASS")


if __name__ == "__main__":
    main()
