#!/usr/bin/env python3
"""Camera-free checks for the cross-platform FFmpeg view/record helper."""

from __future__ import annotations

import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import textwrap


def executable(path: pathlib.Path, source: str) -> None:
    path.write_text(textwrap.dedent(source).lstrip(), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} SCRIPT")
    script = pathlib.Path(sys.argv[1]).resolve()
    source = script.read_text(encoding="utf-8")
    subprocess.run(["sh", "-n", str(script)], check=True)
    assert "bayer_grbg8" in source
    assert "--diagnose-install" in source
    assert "libusb_control_transfer" not in source

    inert = subprocess.run([str(script)], capture_output=True, text=True)
    assert inert.returncode == 0
    assert "NO USB TRANSFER SENT" in inert.stderr

    with tempfile.TemporaryDirectory(prefix="tca-ffmpeg-") as directory:
        root = pathlib.Path(directory)
        fake_reader = root / "fake-reader.py"
        fake_ffmpeg = root / "fake-ffmpeg.py"
        failing_ffmpeg = root / "failing-ffmpeg.py"
        fake_ffplay = root / "fake-ffplay.py"
        executable(
            fake_reader,
            r"""
            #!/usr/bin/env python3
            import pathlib
            import sys

            args = sys.argv[1:]
            assert args[0] == "capture"
            def option(name):
                return args[args.index(name) + 1]
            frames = int(option("--frames"))
            mode = int(option("--mode"))
            raw = pathlib.Path(option("--raw-first"))
            raw.write_bytes(b"untouched-device-record")
            if "--timestamps" in args:
                timestamps = pathlib.Path(option("--timestamps"))
                count = frames if frames else 1
                rows = ["frame,monotonic_ns"]
                rows.extend(f"{index},{1000000000 + index * 100000000}" for index in range(count))
                timestamps.write_text("\n".join(rows) + "\n", encoding="utf-8")
            frame_bytes = 10068672 if mode == 0 else 1228800
            count = frames if frames else 1
            sys.stdout.buffer.write(bytes([128]) * frame_bytes * count)
            """,
        )
        executable(
            fake_ffmpeg,
            r"""
            #!/usr/bin/env python3
            import pathlib
            import sys

            args = sys.argv[1:]
            source = pathlib.Path(args[args.index("-i") + 1])
            output = pathlib.Path(args[-1])
            output.write_text(f"bytes={len(source.read_bytes())}\n", encoding="utf-8")
            """,
        )
        executable(
            fake_ffplay,
            r"""
            #!/usr/bin/env python3
            import pathlib
            import sys

            args = sys.argv[1:]
            source = pathlib.Path(args[args.index("-i") + 1])
            if len(source.read_bytes()) == 0:
                raise SystemExit(1)
            """,
        )
        executable(
            failing_ffmpeg,
            r"""
            #!/usr/bin/env python3
            raise SystemExit(17)
            """,
        )
        environment = {
            **os.environ,
            "TCA_CAMERA_READER": str(fake_reader),
            "TCA_FFMPEG": str(fake_ffmpeg),
            "TCA_FFPLAY": str(fake_ffplay),
        }

        diagnostic = subprocess.run(
            [str(script), "--diagnose-install"],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        assert f"reader={fake_reader} executable=1" in diagnostic.stdout
        assert f"ffmpeg={fake_ffmpeg} executable=1" in diagnostic.stdout
        assert f"ffplay={fake_ffplay} executable=1" in diagnostic.stdout
        assert "NO USB TRANSFER SENT" in diagnostic.stdout

        raw = root / "record.raw"
        video = root / "record.mp4"
        timestamps = root / "record.csv"
        record = subprocess.run(
            [str(script), "--record", str(raw), str(video),
             str(timestamps), "2", "250", "0", "2", "10"],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        assert "frames=2 mode=2 geometry=1280x960 fps=10 status=ok" in record.stdout
        assert raw.read_bytes() == b"untouched-device-record"
        assert video.read_text(encoding="utf-8") == "bytes=2457600\n"
        assert timestamps.read_text(encoding="utf-8").splitlines() == [
            "frame,monotonic_ns", "0,1000000000", "1,1100000000"
        ]

        view_raw = root / "view.raw"
        view = subprocess.run(
            [str(script), "--view", str(view_raw), "250", "0", "2", "10"],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        assert "viewer=closed status=ok" in view.stdout
        assert view_raw.read_bytes() == b"untouched-device-record"

        invalid_raw = root / "invalid.raw"
        invalid = subprocess.run(
            [str(script), "--view", str(invalid_raw), "250", "0", "1"],
            capture_output=True,
            text=True,
            env=environment,
        )
        assert invalid.returncode == 64
        assert "MODE must be 0 or 2" in invalid.stderr
        assert not invalid_raw.exists()

        collision_raw = root / "collision.raw"
        collision_video = root / "collision.mp4"
        collision_video.write_text("keep\n", encoding="utf-8")
        collision = subprocess.run(
            [str(script), "--record", str(collision_raw),
             str(collision_video), str(root / "collision.csv"), "2"],
            capture_output=True,
            text=True,
            env=environment,
        )
        assert collision.returncode == 73
        assert collision_video.read_text(encoding="utf-8") == "keep\n"
        assert not collision_raw.exists()

        failed = subprocess.run(
            [str(script), "--record", str(root / "failed.raw"),
             str(root / "failed.mp4"), str(root / "failed.csv"), "2"],
            capture_output=True,
            text=True,
            timeout=5,
            env={**environment, "TCA_FFMPEG": str(failing_ffmpeg)},
        )
        assert failed.returncode == 17
        assert "FFmpeg recording failed with status 17" in failed.stderr

    print("TCA FFmpeg view/record helper checks: PASS")


if __name__ == "__main__":
    main()
