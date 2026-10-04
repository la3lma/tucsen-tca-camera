# Public prerelease v0.2.0-alpha.12

Date: 2026-10-04

## Result

The annotated public tag `v0.2.0-alpha.12` resolves to exact commit
`a7f5e29ab1f87704e0692bf890f5e5b3ad89a281` and is published as a GitHub
prerelease:

<https://github.com/la3lma/tucsen-tca-camera/releases/tag/v0.2.0-alpha.12>

Alpha 12 packages two Linux usability improvements without changing the
recovered USB initialization, frame assembly, exposure, or gain protocol.
`tca-camera list` provides a USB-inert exact-device cable-move preflight.
`tca-v4l2 --serve-existing` attaches to an explicitly pre-created,
exact-labelled system loopback without loading/unloading its module, changing
node ownership, or removing the node. Non-opening sysfs readiness avoids the
exclusive-capture race preserved during full-resolution development.

## Release assets

The 53,524-byte ARM64 development package has internal Debian version
`0.2.0~alpha12-1`. Its public checksum is:

```text
f4448b0b70a22803e53e85eb66777951a3a7f77d2fe6f1e64de46ff439b41410  tucsen-tca-camera_0.2.0.alpha12-1_arm64.deb
```

The downloaded release asset is byte-identical to the retained tag-built
package. The downloaded `SHA256SUMS` itself has SHA-256
`aae1157fb9acc11784aef59770ccd4ad0be3d24f60d6df9eadb37976e60a6945`.

## Exact tag, archive, and native verification

- Tag object `6d43cb3f6378342f6d152d39eeb41c93122e2ae5` resolves to exact commit
  `a7f5e29ab1f87704e0692bf890f5e5b3ad89a281`.
- Exact-tag Ubuntu/macOS CI passed in
  [run 37223620833](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37223620833).
- The exact tag passed the complete Raspberry Pi AArch64 suite with zero
  cameras attached, including two-build package reproducibility, metadata and
  contents inspection, extracted-program execution, inert helper diagnostics,
  and overwrite refusal.
- The downloaded tag archive passed the complete Apple Silicon and Raspberry
  Pi AArch64 suites outside a Git checkout. Its SHA-256 is:

```text
057567881ecea088260fba39f8f5f690bc6935b3c33cf3c82538dd8d0117246c  tucsen-tca-camera-v0.2.0-alpha.12.tar.gz
```

- Exact merged main had already passed token-gated camera-free Pi integration
  through bridge-owned and pre-created V4L2 devices in both supported
  geometries, using real FFmpeg, `v4l2loopback`, and `v4l2-ctl` consumers.
  Pre-created node/module ownership survived bridge TERM and final cleanup
  remained with the enclosing root-owned harness.
- Direct Apple Silicon enumeration reports one high-speed exact camera; the
  Pi reports zero while the camera remains on the Mac. Both commands state
  that no device was opened and no transfer submitted.
- Current-tree, downloaded-source, package, and full-history privacy checks
  pass; no vendor binary, disassembly, firmware, packet capture, raw camera
  frame, VM disk, credential, or private work is published.

## Installed Raspberry Pi state

The hash-pinned downloaded package upgraded `rpios-17` from alpha 11 to alpha
12 while no camera was attached. The package database reports version
`0.2.0~alpha12-1`; `dpkg -V` is clean; `tca-camera --version` and the installed
marker both report `0.2.0-alpha.12`; and the installed V4L2 and FFmpeg
diagnostics resolve their sibling tools and end with `NO USB TRANSFER SENT`.
The inert list command reports zero matches and explicitly sends no transfer.

This prepares the Pi with the same system-managed V4L2 path verified by the
synthetic application lifecycle. It does not itself prove physical USB frame
delivery from the Pi.

## Explicit residual gates

The physical acceptance scope is unchanged:

1. move the camera to the Pi and execute the prepared uncorrected preview and
   full-resolution V4L2 gates;
2. acquire true blocked-light dark and translated/defocused blank-field sets,
   then repeat the physical Linux gate with the accepted calibration map;
3. confirm Bayer phase, orientation, color response, and focus behavior with a
   known target; and
4. complete the physical cable disconnect/reconnect case.

AVFoundation/system-wide macOS camera discovery remains a non-blocking
deferral. Alpha 12 improves operations and distribution; it is not final
acceptance.
