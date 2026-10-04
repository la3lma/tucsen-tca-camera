# Public prerelease `v0.2.0-alpha.8`

Date: 2026-10-04

## Result

The annotated public tag `v0.2.0-alpha.8` resolves to commit
`2dd0b395e033d0a68410ac03e5b549ea534caeac` and is published as a GitHub
prerelease:

<https://github.com/la3lma/tucsen-tca-camera/releases/tag/v0.2.0-alpha.8>

This release packages the complete 1280x960 preview and 3664x2748
full-resolution Linux V4L2 application paths, separate producer and consumer
evidence, camera-free lifecycle/backpressure coverage in both geometries, the
independently runnable uncorrected physical transport gate, strict map-backed
corrected delivery, a recorded application deadline with deterministic
cleanup, the post-merge Apple Silicon optical regression, and Docstack 4.2.
The implementation remains Apache-2.0 licensed and entirely in user space.

## Independent verification

- Exact commit `2dd0b39` passed GitHub CI on Ubuntu and macOS before tagging:
  run <https://github.com/la3lma/tucsen-tca-camera/actions/runs/37206136495>.
- The tag itself passed a separate GitHub CI run on Ubuntu and macOS:
  run <https://github.com/la3lma/tucsen-tca-camera/actions/runs/37206242284>.
- A detached exact-commit worktree on Raspberry Pi AArch64 passed
  `make clean && make test`. This run was USB-inert because the camera remained
  attached to the Mac.
- The GitHub tag archive was downloaded inside the private report project,
  extracted outside a Git checkout, and passed the complete Apple Silicon
  suite using the documented scoped native-ARM64 libusb `pkg-config`
  override. Its SHA-256 is
  `9772b437d2e5371857a257c11e0c3b4ff88de0ee9d64c754c8d4fcabb0e40d60`.
- The host's default `pkg-config` still selected a stale Intel Homebrew libusb
  and failed to link for ARM64. Re-running with the release's documented
  `LIBUSB_PKG_CONFIG_PATH` override selected the project-local native library
  and passed. This independently exercises the mixed-Homebrew recovery path.
- The release commit passed the full-history public publication audit. The tag
  and release contain no raw disassembly, decompiler export, Ghidra project,
  vendor binary, firmware, packet capture, VM disk, or private-work artifact.

## Physical evidence included

Exact post-V4L2-merge public main physically captured three distinct coherent
1280x960 frames at 9.51334 frames/s and two distinct complete 3664x2748 frames
at 2.75318 frames/s on Apple Silicon at requested 250 ms/gain 0. Exact byte and
timestamp counts passed, the analyzed first frames contained no zero or
saturated pixels, and the complete raster had neither the historic half-black
boundary nor an edge strip.

Camera-free Raspberry Pi runs exercised the real V4L2 bridge at both
application geometries with consumer detach/reattach, deliberate delayed
consumption, bounded post-warm-up process-tree memory, exact output bytes and
digests, deterministic termination, and complete device/module cleanup.

## Explicit residual gates

This is a useful prerelease, not final acceptance. The remaining physical work
is:

1. move the camera to the Raspberry Pi and execute the explicitly uncorrected
   preview and full-resolution V4L2 application gates;
2. acquire true blocked-light dark and translated/defocused blank-field flat
   sets at locked settings, then repeat the physical V4L2 gate with the
   accepted map;
3. confirm Bayer phase, orientation, and color response with a known target;
   and
4. complete the physical cable disconnect/reconnect acceptance case.

AVFoundation/system-wide macOS camera discovery remains a non-blocking
deferral; the direct portable reader continues to work on macOS.
