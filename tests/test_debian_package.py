#!/usr/bin/env python3
"""Build and inspect the rootless, reproducible Debian binary package."""

from __future__ import annotations

import hashlib
import pathlib
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile


PROGRAMS = (
    "tca-camera",
    "tca-v4l2",
    "tca-v4l2-session",
    "tca-ffmpeg",
    "tca-frame-stats",
    "tca-timing-stats",
    "tca-white-balance",
    "tca-flat-field",
)


def run(*arguments: str, cwd: pathlib.Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def field(package: pathlib.Path, name: str) -> str:
    return run("dpkg-deb", "--field", str(package), name).stdout.strip()


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} REPOSITORY")
    repository = pathlib.Path(sys.argv[1]).resolve()
    if platform.system() != "Linux" or not shutil.which("dpkg-deb"):
        print("TCA Debian package checks: SKIP (requires Linux dpkg-deb)")
        return

    builder = repository / "tools" / "build_deb.sh"
    version = (repository / "packaging" / "debian" / "version").read_text(
        encoding="utf-8"
    ).strip()
    upstream_version = (repository / "VERSION").read_text(
        encoding="utf-8"
    ).strip()
    architecture = run("dpkg", "--print-architecture").stdout.strip()

    with tempfile.TemporaryDirectory(prefix="tca-deb-test-") as directory:
        temporary = pathlib.Path(directory)
        first_output = temporary / "first"
        second_output = temporary / "second"
        first = run(str(builder), str(first_output), cwd=repository)
        second = run(str(builder), str(second_output), cwd=repository)
        assert "NO USB TRANSFER SENT." in first.stdout
        assert "NO USB TRANSFER SENT." in second.stdout

        filename = f"tucsen-tca-camera_{version}_{architecture}.deb"
        first_package = first_output / filename
        second_package = second_output / filename
        assert first_package.is_file()
        assert second_package.is_file()
        assert digest(first_package) == digest(second_package)

        assert field(first_package, "Package") == "tucsen-tca-camera"
        assert field(first_package, "Version") == version
        assert field(first_package, "Architecture") == architecture
        dependencies = {
            item.strip() for item in field(first_package, "Depends").split(",")
        }
        assert dependencies == {"libc6", "libusb-1.0-0", "python3"}
        recommendations = {
            item.strip() for item in field(first_package, "Recommends").split(",")
        }
        assert recommendations == {
            "ffmpeg",
            "kmod",
            "sudo",
            "time",
            "v4l-utils",
            "v4l2loopback-dkms",
        }

        listing = run("dpkg-deb", "--contents", str(first_package)).stdout
        assert " root/root " in listing
        assert "./usr/lib/udev/rules.d/99-tucsen-tca-camera.rules" in listing
        assert "./usr/share/doc/tucsen-tca-camera/copyright" in listing
        assert "./usr/share/doc/tucsen-tca-camera/VERSION" in listing
        assert "./usr/share/doc/tucsen-tca-camera/examples/systemd/tca-v4l2.service.example" in listing
        assert "./usr/share/doc/tucsen-tca-camera/examples/systemd/v4l2.env.example" in listing

        control_directory = temporary / "control"
        run("dpkg-deb", "--control", str(first_package), str(control_directory))
        for maintainer_script in ("postinst", "postrm"):
            script = control_directory / maintainer_script
            assert script.stat().st_mode & stat.S_IXUSR
            script_text = script.read_text(encoding="utf-8")
            assert "udevadm control --reload-rules || true" in script_text

        extracted = temporary / "extracted"
        run("dpkg-deb", "--extract", str(first_package), str(extracted))
        binary_directory = extracted / "usr" / "bin"
        for name in PROGRAMS:
            installed = binary_directory / name
            assert stat.S_ISREG(installed.stat().st_mode)
            assert installed.stat().st_mode & stat.S_IXUSR

        reported_version = run(
            str(binary_directory / "tca-camera"), "--version"
        ).stdout.strip()
        assert reported_version == f"tca-camera {upstream_version}"
        listed = run(str(binary_directory / "tca-camera"), "list").stdout
        assert "target=0547:c003\n" in listed
        assert re.search(r"^camera-count=[0-9]+$", listed, re.MULTILINE)
        assert "NO DEVICE OPENED OR TRANSFER SUBMITTED." in listed
        installed_version = (
            extracted / "usr" / "share" / "doc" / "tucsen-tca-camera" / "VERSION"
        ).read_text(encoding="utf-8").strip()
        assert installed_version == upstream_version

        for helper in ("tca-v4l2", "tca-ffmpeg"):
            diagnostic = run(str(binary_directory / helper), "--diagnose-install")
            assert (
                f"reader={binary_directory / 'tca-camera'} executable=1"
                in diagnostic.stdout
            )
            assert "NO USB TRANSFER SENT." in diagnostic.stdout

        session_diagnostic = run(
            str(binary_directory / "tca-v4l2-session"), "--diagnose-install"
        )
        assert (
            f"bridge={binary_directory / 'tca-v4l2'} executable=1"
            in session_diagnostic.stdout
        )
        assert "policy=pre-created-loopback-only" in session_diagnostic.stdout

        rule = (
            extracted
            / "usr"
            / "lib"
            / "udev"
            / "rules.d"
            / "99-tucsen-tca-camera.rules"
        ).read_text(encoding="utf-8")
        assert 'ATTR{idVendor}=="0547"' in rule
        assert 'ATTR{idProduct}=="c003"' in rule

        collision = subprocess.run(
            [str(builder), str(first_output)],
            cwd=repository,
            capture_output=True,
            text=True,
        )
        assert collision.returncode == 73
        assert "refusing to overwrite existing package" in collision.stderr

    print("TCA Debian package checks: PASS")


if __name__ == "__main__":
    main()
