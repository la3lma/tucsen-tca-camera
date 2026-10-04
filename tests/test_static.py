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
    if len(sys.argv) != 4:
        raise SystemExit(f"usage: {sys.argv[0]} BINARY SOURCE VERSION")
    binary = pathlib.Path(sys.argv[1]).resolve()
    source = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")
    expected_version = pathlib.Path(sys.argv[3]).read_text(
        encoding="utf-8"
    ).strip()
    symbols = subprocess.run(
        ["nm", "-u", str(binary)], check=True, capture_output=True, text=True
    ).stdout
    imports = set(re.findall(r"_?(libusb_[A-Za-z0-9_]+)", symbols))
    assert imports == ALLOWED, imports
    assert "TCA_MODE2_DEVICE_BYTES 1229312u" in source
    assert "TCA_MODE2_WIDTH 1280u" in source
    assert "TCA_MODE2_HEIGHT 960u" in source
    assert "TCA_MODE0_DEVICE_BYTES 10068992u" in source
    assert "TCA_MODE0_WIDTH 3664u" in source
    assert "TCA_MODE0_HEIGHT 2748u" in source
    assert "TCA_NEXT_PACKET_BYTES" in source
    assert "TCA_PREFIX_MARKER_BYTES 10u" in source
    assert '"mode 2 record prefix must be 512 bytes"' in source
    assert '"mode 0 head plus next-record continuation must be one frame"' in source
    assert "record request=%zu" in source
    assert "head_bytes" in source
    assert "device_frame + mode->head_offset" in source
    assert "next_device_frame + mode->continuation_offset" in source
    assert "while (*received < mode->device_bytes)" not in source
    assert "TCA_INITIAL_RESYNC_LIMIT 2u" in source
    assert "TCA_MODE2_ROW_TIME_US 120u" in source
    assert "TCA_MODE0_ROW_TIME_US 309u" in source
    assert "0x3012u" in source and "0x305eu" in source
    assert '"--exposure-ms"' in source and '"--gain"' in source
    assert '"--timestamps"' in source
    assert "CLOCK_MONOTONIC" in source
    assert '"frame,monotonic_ns\\n"' in source
    assert 'perror("flush raw-first")' in source
    assert "fflush(raw_first)" in source
    assert "discarding bounded warm-up record %u/%u" in source
    assert "int raw_written = 0" in source
    assert "trace_command_result_accepted" in source
    assert "result == 1 && response[0] == request" in source
    assert '"result=bytes (%d) first=0x%02x\\n"' in source
    assert "control-settle discarded one pre-control buffered record" in source
    assert "libusb_reset_device" not in source
    assert "libusb_set_configuration" not in source
    dry = subprocess.run([str(binary)], check=True, capture_output=True, text=True)
    assert "NO TRANSFER SENT" in dry.stdout
    assert "available-modes=0:3664x2748-still,2:1280x960-preview" in dry.stdout
    version = subprocess.run(
        [str(binary), "--version"], check=True, capture_output=True, text=True
    )
    assert version.stdout.strip() == f"tca-camera {expected_version}"
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
        invalid_timestamps = subprocess.run(
            [str(binary), "capture", "--frames", "1",
             "--raw-first", str(raw), "--bayer", str(bayer),
             "--timestamps", "-"],
            capture_output=True,
            text=True,
        )
        assert invalid_timestamps.returncode == 64
        assert "NO TRANSFER SENT" in invalid_timestamps.stderr
        assert not raw.exists() and not bayer.exists()
        invalid_mode = subprocess.run(
            [str(binary), "capture", "--frames", "1",
             "--raw-first", str(raw), "--bayer", str(bayer),
             "--mode", "1"],
            capture_output=True,
            text=True,
        )
        assert invalid_mode.returncode == 64
        assert "NO TRANSFER SENT" in invalid_mode.stderr
        assert not raw.exists() and not bayer.exists()
    print("Linux stream reader static/inert checks: PASS")


if __name__ == "__main__":
    main()
