# Public prerelease `v0.2.0-alpha.7`

Date: 2026-10-04

## Result

The annotated public tag `v0.2.0-alpha.7` resolves to commit
`72f6e631a75dfe6aceebad30d98d84c17b30d9e8` and is published as a GitHub
prerelease:

<https://github.com/la3lma/tucsen-tca-camera/releases/tag/v0.2.0-alpha.7>

This release packages the settings-bound dark/flat corrector, optional
corrected V4L2 path, inert guided physical-calibration session, monotonic
per-frame timestamp output, timing analyzer, rendered public evidence, and
permanent public/private publication-boundary enforcement. The implementation
remains Apache-2.0 licensed and entirely in user space.

## Independent verification

- The exact commit passed GitHub CI on both Ubuntu and macOS before tagging:
  run `37198751084`.
- The tag itself passed a separate GitHub CI run on Ubuntu and macOS:
  run `37198791200`.
- A detached exact-commit worktree on Raspberry Pi AArch64
  (`rpios-17`, Linux 6.18.39+rpt-rpi-2712) passed `make clean all test`.
  This run was USB-inert and did not access the Mac-connected camera.
- The GitHub tag archive was downloaded inside the private report project,
  extracted outside a Git checkout, and passed `make clean all test` on Apple
  Silicon. Its SHA-256 is
  `921e248caf865cd9a8165475f4d220b70e4ac586da11d9179ca7e7aa5436b03f`.
- The release commit passed the full-history public publication audit. The tag
  and release contain no raw disassembly, decompiler export, Ghidra project,
  vendor binary, firmware, packet capture, VM disk, or private-work artifact.

## Measured hardware evidence included

Direct Apple Silicon capture delivered 17.3466 frames/s for 1280x960 at a
requested 1-ms exposure, 9.5057 frames/s for 1280x960 at 250 ms, and 2.7911
frames/s for 3664x2748 at 250 ms. All frames in the three bounded trials had
distinct hashes. These are host-output cadence measurements, not proof of the
camera's sensor integration interval.

## Explicit residual gates

This is a useful prerelease, not final acceptance. The remaining physical work
is unchanged:

1. acquire true blocked-light dark and blank-field flat sets with the guided
   session at locked settings;
2. confirm Bayer phase and color response with a known target;
3. move the camera to Linux and measure corrected V4L2 consumer cadence and
   drops; and
4. complete the physical cable disconnect/reconnect acceptance case.

AVFoundation remains a non-blocking macOS application-surface deferral.
