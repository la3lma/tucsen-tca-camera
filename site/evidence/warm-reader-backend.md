# Warm-state libusb reader backend

Evidence date: 2026-09-29

## Scope

This is the first live transport implementation behind the portable reader
session. It is deliberately limited to the already-verified warm handoff: the
legacy Windows stack must have initialized the still-powered camera in fixed
mode 4 before this backend is used. It does not attempt cold initialization,
controls, reset, configuration, alternate-setting selection, an OUT transfer,
or firmware loading.

Sources:

- `src/tca_libusb_warm.h`
- `src/tca_libusb_warm.c`
- `tools/tca_reader_warm.c`
- `tests/test_tca_warm_static.py`
- `tests/test_tca_libusb_warm.c`

The CLI is inert by default. Only the exact token
`--capture-already-streaming-mode4` enters the USB path. The invalid-token test
also verifies that no output files are created.

## Transport contract

Before claiming interface zero, the backend verifies:

- USB identity `0547:c003`;
- at least one configuration descriptor;
- vendor-specific interface zero; and
- bulk-IN endpoint `0x82` with a 512-byte maximum packet.

It refuses a currently active kernel driver and never detaches one. After a
successful claim it performs the fixed, bounded mode-4 schedule:

```text
81920 + 81920 + 81920 + 61440 = 307200 bytes
```

Every successful read must have exactly the requested length. There is no
retry or continuation after a short read. Complete raw frames are written to
the mandatory raw sink before decode; bytes received before a transfer error or
short completion are also preserved for diagnosis. Exact frames then pass
through the common bounded queue and GRBG-to-RGB24 decoder. The two output
paths must differ so an operator cannot accidentally alias and corrupt them.

## Static call-surface audit

The native ARM64 Linux binary imports exactly these libusb functions:

```text
libusb_bulk_transfer
libusb_claim_interface
libusb_close
libusb_exit
libusb_free_config_descriptor
libusb_get_config_descriptor
libusb_get_device
libusb_get_device_descriptor
libusb_init
libusb_kernel_driver_active
libusb_open_device_with_vid_pid
libusb_release_interface
```

The Apple Silicon binary has the same set with Mach-O symbol prefixes. In
particular, neither binary imports `libusb_control_transfer`,
`libusb_reset_device`, `libusb_set_configuration`,
`libusb_set_interface_alt_setting`, an asynchronous submit API, or a distinct
OUT-transfer API. `libusb_bulk_transfer` is invoked only with the compile-time
endpoint `0x82`.

`tests/test_tca_warm_static.py` compares the binary import set to this exact
allowlist, runs the inert default path, and verifies invalid-token refusal.

The backend's bulk-call boundary is injectable for offline testing while its
production default remains `libusb_bulk_transfer`. The native C test verifies
the exact four-request schedule, endpoint and timeout, complete-frame
preservation, short completion with no retry, transport error with partial raw
preservation, zero-length refusal, raw-sink failure propagation, fixed-mode
guard, and claimed-state guard. It performs no enumeration or USB operation.

## Native builds

Ubuntu ARM64 VM:

- AArch64 PIE linked to `/lib/aarch64-linux-gnu/libusb-1.0.so.0`;
- strict C17 build with `-Wall -Wextra -Werror -pedantic` passes;
- static/inert CLI and fault-injection backend tests pass; and
- binary SHA-256 is
  `fcd8ed392c6653f8b5600f93641cd72db37a150476afdf855815c39838fa8938`.

Apple Silicon macOS:

- native arm64 Mach-O built by Apple clang 21.0.0;
- project-local libusb 1.0.28 avoids the installed Intel Homebrew mismatch;
- the official release archive remains inside the project at
  `work/deps/src/libusb-1.0.28.tar.bz2`, SHA-256
  `966bb0d231f94a474eaae2e67da5ec844d3527a1f386456394ff432580634b29`;
- strict build and static/inert CLI plus fault-injection backend tests pass;
- AddressSanitizer/UndefinedBehaviorSanitizer dry execution and the import
  allowlist test pass; and
- binary SHA-256 is
  `3507192d9ecdfcf84ac4875645d1440137f5c4a2fb136783f7e82727bf79c0ad`.

The archive was downloaded from the upstream libusb 1.0.28 GitHub release;
all downloaded and expanded dependency material is under `work/deps/`.

The full core and replay suites pass on macOS and Ubuntu ARM64. The separate
Windows-PE emulator suite passes on macOS; it was not repeated on Ubuntu
because the project-local emulator virtual environment is not installed there.

## Prepared Linux application bridge

`tools/tca_v4l2_warm.sh` connects the warm reader's RGB24 stream to a temporary
YUYV V4L2 loopback while preserving the Bayer8 stream in an operator-selected
raw file. It is also inert without its own exact
`--camera-already-streaming-mode4` token, refuses an existing raw output, video
node, or loopback setup, and removes only the loopback module it loaded.

Syntax and invalid-token paths pass `sh -n` and inert tests on both macOS and
Ubuntu ARM64. No live bridge run was attempted because the warm-state camera
precondition is not presently satisfied. The already-verified replay bridge
remains the evidence for application-side V4L2 negotiation and consumption.

## Live-execution boundary

No execution-token run was performed in this implementation session because
the connected camera is presently cold, not an already-streaming handoff.
Running this backend now would only test the known-unmet precondition and could
consume or fault the preserved trace setup. The previously captured live frame
already proves the same mode-4 bulk-IN data plane; this change integrates that
operation with the portable reader contract but does not replace the pending
known-good Windows initialization trace.

At the end of verification the camera still enumerated as `0547:c003`, TCP
7575 was listening, the independent `usbmon3` capture remained 1,668 bytes,
and `/dev/video42` was absent.
