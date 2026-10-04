#!/usr/bin/env python3
"""Inert and USB-free end-to-end checks for the guided calibration session."""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile


FRAME_BYTES = 1_228_800
DEVICE_BYTES = 1_229_312


def make_executable(path: pathlib.Path, source: str) -> None:
    path.write_text(source, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def verify_manifest(output: pathlib.Path) -> None:
    entries = output.joinpath("manifest.sha256").read_text(encoding="utf-8").splitlines()
    assert entries
    for entry in entries:
        digest, relative = entry.split(maxsplit=1)
        relative = relative.lstrip("* ")
        candidate = output / relative
        assert candidate.is_file(), relative
        assert hashlib.sha256(candidate.read_bytes()).hexdigest() == digest


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(f"usage: {sys.argv[0]} SCRIPT FLAT_TOOL STATS_TOOL")
    script = pathlib.Path(sys.argv[1]).resolve()
    flat_tool = pathlib.Path(sys.argv[2]).resolve()
    stats_tool = pathlib.Path(sys.argv[3]).resolve()
    source = script.read_text(encoding="utf-8")

    subprocess.run(["sh", "-n", str(script)], check=True)
    inert = subprocess.run([str(script)], capture_output=True, text=True)
    assert inert.returncode == 0
    assert "NO USB TRANSFER SENT. NO FILE OR SYSTEM CHANGE MADE." in inert.stderr
    assert "--run-flat-field-capture-session" in source
    assert "--exposure-ms" in source and "--camera-gain" in source
    assert "SESSION-INCOMPLETE.txt" in source
    assert "v4l2loopback" not in source
    assert "firmware" not in source.lower()
    assert "reset" not in source.lower()

    with tempfile.TemporaryDirectory(prefix="tca-flat-session-") as temp_name:
        temp = pathlib.Path(temp_name)
        rejected_output = temp / "rejected"
        rejected = subprocess.run(
            [
                str(script),
                "--run-flat-field-capture-session",
                "--output",
                str(rejected_output),
                "--exposure-ms",
                "0",
            ],
            capture_output=True,
            text=True,
        )
        assert rejected.returncode == 64
        assert not rejected_output.exists()
        assert "NO USB TRANSFER SENT" in rejected.stderr

        fake_camera = temp / "fake-camera.py"
        make_executable(
            fake_camera,
            f"""#!/usr/bin/env python3
import pathlib
import sys

args = sys.argv[1:]
assert args[0] == "capture"
def value(option):
    return args[args.index(option) + 1]
frames = int(value("--frames"))
raw = pathlib.Path(value("--raw-first"))
bayer = pathlib.Path(value("--bayer"))
name = bayer.name
if name == "darks.bayer":
    pixel = 10
elif name.startswith("flat-batch-"):
    pixel = 110
elif name == "validation-blank.bayer":
    pixel = 80
else:
    pixel = 60
raw.write_bytes(b"\\x88" * 10 + b"\\x00" * ({DEVICE_BYTES} - 10))
bayer.write_bytes(bytes([pixel]) * ({FRAME_BYTES} * frames))
print(f"frames={{frames}} status=ok", file=sys.stderr)
""",
        )

        fake_ffmpeg = temp / "fake-ffmpeg.py"
        make_executable(
            fake_ffmpeg,
            """#!/usr/bin/env python3
import pathlib
import sys
pathlib.Path(sys.argv[-1]).write_bytes(b"\\x89PNG\\r\\n\\x1a\\nFAKE")
""",
        )

        output = temp / "session"
        env = dict(os.environ)
        env.update(
            {
                "TCA_CAMERA": str(fake_camera),
                "TCA_FLAT_FIELD_TOOL": str(flat_tool),
                "TCA_FRAME_STATS_TOOL": str(stats_tool),
                "TCA_FFMPEG": str(fake_ffmpeg),
            }
        )
        cancelled_output = temp / "cancelled"
        cancelled = subprocess.run(
            [
                str(script),
                "--run-flat-field-capture-session",
                "--output",
                str(cancelled_output),
                "--dark-frames",
                "1",
                "--flat-batches",
                "1",
                "--flat-frames-per-batch",
                "1",
            ],
            input="",
            capture_output=True,
            text=True,
            env=env,
        )
        assert cancelled.returncode != 0
        assert cancelled_output.joinpath("SESSION-INCOMPLETE.txt").is_file()
        assert not cancelled_output.joinpath("darks.bayer").exists()

        run = subprocess.run(
            [
                str(script),
                "--run-flat-field-capture-session",
                "--output",
                str(output),
                "--exposure-ms",
                "100",
                "--gain",
                "20",
                "--phase",
                "grbg",
                "--dark-frames",
                "2",
                "--flat-batches",
                "2",
                "--flat-frames-per-batch",
                "1",
            ],
            input="\n" * 5,
            capture_output=True,
            text=True,
            env=env,
        )
        if run.returncode != 0:
            raise AssertionError(f"session failed\nstdout:\n{run.stdout}\nstderr:\n{run.stderr}")
        assert "dark_frames=2 flat_frames=2" in run.stdout
        assert "status=ok" in run.stdout
        assert not output.joinpath("SESSION-INCOMPLETE.txt").exists()
        assert output.joinpath("darks.bayer").stat().st_size == FRAME_BYTES * 2
        assert output.joinpath("flats.bayer").stat().st_size == FRAME_BYTES * 2
        assert output.joinpath("validation-blank.bayer").stat().st_size == FRAME_BYTES
        assert output.joinpath("validation-blank-corrected.bayer").stat().st_size == FRAME_BYTES
        assert output.joinpath("validation-blank-corrected.bayer").read_bytes()[0] == 70
        assert output.joinpath("validation-specimen-corrected.bayer").read_bytes()[0] == 50

        calibration = json.loads(output.joinpath("calibration.json").read_text())
        assert calibration["width"] == 1280 and calibration["height"] == 960
        assert calibration["phase"] == "grbg"
        assert calibration["dark_frames"] == 2 and calibration["flat_frames"] == 2
        assert calibration["exposure_ms"] == 100
        assert calibration["camera_gain"] == 20
        for name in (
            "validation-blank.png",
            "validation-blank-corrected.png",
            "validation-specimen.png",
            "validation-specimen-corrected.png",
        ):
            assert output.joinpath(name).read_bytes().startswith(b"\x89PNG")
        verify_manifest(output)

    print("TCA guided flat-field capture session checks: PASS")


if __name__ == "__main__":
    main()
