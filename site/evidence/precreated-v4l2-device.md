# System-managed V4L2 loopback lifecycle

Date: 2026-10-04

Issue [#38](https://github.com/la3lma/tucsen-tca-camera/issues/38) and
[PR #39](https://github.com/la3lma/tucsen-tca-camera/pull/39), merged as
public main `8d254b7b27e5d4d27d8a06a9e9fdddbb48a6e929`, address an
application-integration limitation: `tca-v4l2` previously refused to run when
`v4l2loopback` was already loaded, because its only mode owned module creation,
device ownership, and teardown.

## Ownership contract

The existing `--serve` operation is unchanged: it requires an unused setup,
creates an exact-labelled temporary loopback, changes that node's ownership,
and removes only the module it loaded. The new explicit `--serve-existing`
operation instead requires:

- a writable character device at the requested `/dev/videoN`;
- the exact sysfs label `TCA Camera 0547:c003`;
- a loaded `v4l2loopback` module; and
- a node resolving to `/sys/devices/virtual/video4linux/videoN`.

That validation does not open the node. The system-owned path never runs
`modprobe`, changes node ownership, removes a device, or unloads the module.
Bridge readiness is detected through the loopback's read-only sysfs `state`
and `format` files, so readiness inspection does not briefly become an
application consumer.

## Preserved failure and correction

The first extended full-resolution candidate consistently failed before its
consumer created an output file. The uncorrected synthetic reader delivered
four frames in candidate `9c06f30`; pacing at the mode-0 nominal ceiling in
`3c3885f` reduced that to three but did not fix the failure. Removing the
pre-writer V4L2 driver ioctl in `08973b1` also left the three-frame failure.
Each failed run reported `unsupported stream type`; scoped cleanup left no
test device or loaded module.

The remaining open/close operation was the bridge and harness readiness probe:
`v4l2-ctl --all` briefly opened and then closed the exclusive capture side
before the real application attached. Candidate `c9a7e6e` replaced that probe
with sysfs state/format checks and made an unexpected successful end of the
unbounded reader an explicit bridge failure. This change fixed the repeatable
mode-0 race instead of masking it with a larger buffer or retrying USB.

## Raspberry Pi AArch64 integration

Exact candidate `c9a7e6e5ecc78bf36b040f829ed0e7446211ba0a` and exact merged
main passed the complete camera-free Raspberry Pi suite, including
reproducible Debian package construction. The token-gated integration then ran
both ownership models from exact merged main in each supported geometry using
the USB-inert synthetic reader, real FFmpeg, real `v4l2loopback`, and ordinary
`v4l2-ctl` consumers.

| Result | Preview mode 2 | Full-resolution mode 0 |
|---|---:|---:|
| Geometry | 1280x960 | 3664x2748 |
| Managed normal + delayed frames | 4 + 8 | 2 + 3 |
| Managed warm-baseline RSS growth | 0 KiB | 0 KiB |
| Pre-created-device consumer frames | 4 | 2 |
| Pre-created device survived bridge TERM | Pass | Pass |
| Pre-created module survived bridge TERM | Pass | Pass |
| Harness-owned final cleanup | Pass | Pass |
| USB transfers | None | None |

The bridge returned deterministic status 143 on TERM. After bridge shutdown,
the pre-created node retained its exact label and the module remained loaded;
only the surrounding root-owned harness then removed them. Final checks found
neither `/dev/video46`/`47` nor `v4l2loopback` loaded.

The retained exact-main preview manifest has SHA-256
`af783cf4201785d9f3492000eaab2b688e8aeb10a5c11e7d07a855342462fffb`.
The retained exact-main full-resolution manifest has SHA-256
`c0bc93e4cd69aa7c3b28ef1725fe090250239b9d1b4453297988df8ca34ff997`.
These are hashes of the manifest files; their entries hash every generated
integration artifact. Hosted Ubuntu/macOS CI and the complete Apple Silicon
suite also pass on exact merged main.

## Scope

This proves ownership isolation, application attachment, deterministic stop,
and scoped cleanup for both geometries without a camera. It makes a
system-managed V4L2 service practical, but it does not substitute for the
still-open direct-camera Linux application run, physical reconnect, or optical
calibration.
