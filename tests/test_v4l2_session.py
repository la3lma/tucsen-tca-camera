#!/usr/bin/env python3
"""Inert and delegated-session checks for the V4L2 service wrapper."""

from __future__ import annotations

import os
import pathlib
import stat
import subprocess
import sys
import tempfile


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            f"usage: {sys.argv[0]} WRAPPER UNIT_EXAMPLE ENV_EXAMPLE"
        )
    wrapper = pathlib.Path(sys.argv[1]).resolve()
    unit = pathlib.Path(sys.argv[2]).resolve()
    environment_example = pathlib.Path(sys.argv[3]).resolve()
    source = wrapper.read_text(encoding="utf-8")

    subprocess.run(["sh", "-n", str(wrapper)], check=True)
    inert = subprocess.run(
        ["sh", str(wrapper)], check=True, capture_output=True, text=True
    )
    assert "NO USB TRANSFER SENT. NO SYSTEM CHANGE MADE." in inert.stderr
    diagnostic = subprocess.run(
        ["sh", str(wrapper), "--diagnose-install"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "policy=pre-created-loopback-only" in diagnostic.stdout
    assert "NO USB TRANSFER SENT. NO SYSTEM CHANGE MADE." in diagnostic.stdout

    assert 'exec "$bridge" "$SERVE_TOKEN"' in source
    assert "--serve-existing" in source
    assert "TCA_TIMESTAMPS is managed by this session wrapper" in source
    assert "profile=tca-v4l2-service-session-v1" in source
    for forbidden in ("modprobe", "sudo", "chown", "libusb_control_transfer"):
        assert forbidden not in source

    with tempfile.TemporaryDirectory(prefix="tca-v4l2-session-") as directory:
        root = pathlib.Path(directory)
        sessions = root / "sessions"
        sessions.mkdir()
        fake_bridge = root / "fake-v4l2"
        log = root / "bridge.log"
        fake_bridge.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$@\" >\"$TCA_FAKE_LOG\"\n"
            "printf 'timestamps=%s\\n' \"$TCA_TIMESTAMPS\" >>\"$TCA_FAKE_LOG\"\n"
            "printf raw >\"$2\"\n"
            "printf 'frame,monotonic_ns\\n' >\"$TCA_TIMESTAMPS\"\n"
            "exit 23\n",
            encoding="utf-8",
        )
        fake_bridge.chmod(fake_bridge.stat().st_mode | stat.S_IXUSR)
        environment = {
            **os.environ,
            "TCA_V4L2_BRIDGE": str(fake_bridge),
            "TCA_FAKE_LOG": str(log),
        }
        delegated = subprocess.run(
            [
                "sh",
                str(wrapper),
                "--serve-existing",
                str(sessions),
                "47",
                "123",
                "17",
                "2",
            ],
            env=environment,
            capture_output=True,
            text=True,
        )
        assert delegated.returncode == 23
        allocated = list(sessions.iterdir())
        assert len(allocated) == 1
        session = allocated[0]
        resolved_session = session.resolve()
        assert stat.S_IMODE(session.stat().st_mode) == 0o700
        assert (session / "first-device.raw").read_text(encoding="utf-8") == "raw"
        timestamps = session / "reader-timestamps.csv"
        assert timestamps.read_text(encoding="utf-8") == "frame,monotonic_ns\n"
        metadata = (session / "session.txt").read_text(encoding="utf-8")
        assert "loopback_ownership=system\n" in metadata
        assert "video_number=47\n" in metadata
        assert "exposure_ms=123\n" in metadata
        assert "gain=17\n" in metadata
        assert "mode=2\n" in metadata
        bridge_log = log.read_text(encoding="utf-8")
        assert bridge_log.startswith(
            f"--serve-existing\n{resolved_session / 'first-device.raw'}\n47\n123\n17\n2\n"
        )
        assert f"timestamps={resolved_session / 'reader-timestamps.csv'}\n" in bridge_log

        existing_count = len(allocated)
        conflict = subprocess.run(
            ["sh", str(wrapper), "--serve-existing", str(sessions)],
            env={**environment, "TCA_TIMESTAMPS": str(root / "other.csv")},
            capture_output=True,
            text=True,
        )
        assert conflict.returncode == 64
        assert len(list(sessions.iterdir())) == existing_count

    unit_source = unit.read_text(encoding="utf-8")
    assert "--serve-existing" in unit_source
    assert "Restart=no" in unit_source
    assert "PrivateTmp=yes" in unit_source
    assert "WantedBy=default.target" in unit_source
    for forbidden in ("modprobe", "sudo", "--serve "):
        assert forbidden not in unit_source
    environment_source = environment_example.read_text(encoding="utf-8")
    for name in ("TCA_VIDEO_NUMBER", "TCA_EXPOSURE_MS", "TCA_GAIN", "TCA_MODE"):
        assert f"{name}=" in environment_source

    print("TCA V4L2 service-session checks: PASS")


if __name__ == "__main__":
    main()
