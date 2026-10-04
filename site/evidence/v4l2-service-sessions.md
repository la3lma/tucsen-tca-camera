# Restart-safe system-managed V4L2 service sessions

Date: 2026-10-04

Issue [#44](https://github.com/la3lma/tucsen-tca-camera/issues/44) and
[PR #45](https://github.com/la3lma/tucsen-tca-camera/pull/45), merged as
public main `4c3b2ad98d713e404b40a28c14918d91b3662024`, close the
operational gap between a safe system-owned loopback and repeated unattended
starts. The earlier bridge correctly refused to overwrite its raw/timestamp
evidence, but that required a service manager to invent new paths every time.

## Session contract

The new `tca-v4l2-session` helper:

- accepts only `--serve-existing`, never the bridge-owned lifecycle;
- requires an existing writable output root;
- atomically creates a private mode-0700 directory for every start;
- records UTC start time, bridge path, video number, exposure, gain, mode,
  flat-field state, and exact evidence paths;
- reserves a unique `first-device.raw` and `reader-timestamps.csv`; and
- replaces itself with `tca-v4l2 --serve-existing`, preserving the bridge's
  signal and exit semantics.

The wrapper contains no `sudo`, `modprobe`, ownership change, USB transfer,
or loopback cleanup. A disabled systemd user-unit example is packaged only
under the documentation tree. It uses `Restart=no`; installation cannot
enable or start it.

## Exact-main verification

Hosted Ubuntu/macOS CI
[run 37225269501](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37225269501)
passed. Complete Apple Silicon and Raspberry Pi AArch64 suites passed on exact
merged main. The Pi integrations then used the USB-inert synthetic reader,
real FFmpeg, real `v4l2loopback`, and ordinary `v4l2-ctl` consumers through
the new session wrapper:

| Result | Preview mode 2 | Full-resolution mode 0 |
|---|---:|---:|
| Geometry | 1280x960 | 3664x2748 |
| Managed normal + delayed frames | 4 + 8 | 2 + 3 |
| Service-session consumer frames | 4 | 2 |
| Warm-baseline RSS growth | 0 KiB | 9,824 KiB |
| Private session allocation | Pass | Pass |
| Pre-created device survived bridge TERM | Pass | Pass |
| Pre-created module survived bridge TERM | Pass | Pass |
| Harness-owned final cleanup | Pass | Pass |
| USB transfers | None | None |

The exact-main preview manifest-file SHA-256 is
`0caeeac066168a06f9c800fef782a2c640e66b7e415e1b2108a200ebd8705755`.
The exact-main full-resolution manifest-file SHA-256 is
`63d125ae2bef71db487f4ce9b3a982c19413bc0c878834aae4d5943961e8b146`.
Each manifest contains the hashes of all generated integration artifacts.
Final checks found neither test video node nor a loaded loopback module.

## Package and service-manager verification

The reproducible exact-main AArch64 package has internal version
`0.2.0~alpha13-1` and SHA-256:

```text
1befeec59685d5bc3cc27362bb22b2ff819cba9999ff0bc86f07d859eefc56d1  tucsen-tca-camera_0.2.0~alpha13-1_arm64.deb
```

It installs all eight userspace programs plus the systemd examples under
`/usr/share/doc/tucsen-tca-camera/examples/systemd/`. The package upgraded
the camera-free Pi cleanly; `dpkg -V` reports no changes, the CLI reports
alpha 13, `tca-camera list` reports zero and opens no device, and the
installed session diagnostic resolves its installed sibling bridge while
sending no USB transfer or making a system change. The unit passes
`systemd-analyze --user verify`. No service unit is installed, enabled, or
active.

## Scope

This proves restart-safe evidence allocation, service-manager syntax,
application delivery, system-owned loopback survival, and final ownership
boundaries without a camera. It advances Linux operational readiness but does
not substitute for direct-camera Pi V4L2 delivery, cable reconnect, true
dark/blank-field calibration, known-target color/Bayer validation, or owner
acceptance.
