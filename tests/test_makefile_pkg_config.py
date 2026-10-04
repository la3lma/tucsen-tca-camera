#!/usr/bin/env python3
"""Check the scoped libusb pkg-config search-path override."""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} PROJECT_ROOT")
    root = pathlib.Path(sys.argv[1]).resolve()
    expected_path = "/native/lib/pkgconfig"

    with tempfile.TemporaryDirectory(prefix="tca-pkg-config-") as directory:
        temp = pathlib.Path(directory)
        log = temp / "calls.txt"
        fake = temp / "pkg-config"
        fake.write_text(
            "#!/bin/sh\n"
            "printf '%s|%s\\n' \"$PKG_CONFIG_PATH\" \"$*\" >> \"$TCA_FAKE_LOG\"\n"
            "case \"$1\" in\n"
            "  --cflags) printf '%s\\n' '-I/native/include/libusb-1.0' ;;\n"
            "  --libs) printf '%s\\n' '-L/native/lib -lusb-1.0' ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        environment = os.environ.copy()
        environment["TCA_FAKE_LOG"] = str(log)
        result = subprocess.run(
            [
                "make",
                "-n",
                "-B",
                "all",
                f"PKG_CONFIG={fake}",
                f"LIBUSB_PKG_CONFIG_PATH={expected_path}",
            ],
            cwd=root,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        calls = log.read_text(encoding="utf-8").splitlines()
        assert calls == [
            f"{expected_path}|--cflags libusb-1.0",
            f"{expected_path}|--libs libusb-1.0",
        ], calls
        assert "-I/native/include/libusb-1.0" in result.stdout
        assert "-L/native/lib -lusb-1.0" in result.stdout

    print("Scoped libusb pkg-config path check: PASS")


if __name__ == "__main__":
    main()
