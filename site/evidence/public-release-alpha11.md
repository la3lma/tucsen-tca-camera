# Public prerelease v0.2.0-alpha.11

Date: 2026-10-04

## Result

The annotated public tag `v0.2.0-alpha.11` resolves to exact commit
`6e12046b437da7a16945d7275e663df59b0abd57` and is published as a GitHub
prerelease:

<https://github.com/la3lma/tucsen-tca-camera/releases/tag/v0.2.0-alpha.11>

Alpha 11 corrects a release-provenance defect found during the camera-free
acceptance audit. The alpha-10 Debian metadata identified alpha 10 correctly,
but its embedded `tca-camera --version` still reported alpha 7. Alpha 11 makes
the repository `VERSION` file authoritative at build time, requires the CLI,
upstream marker, and Debian version to correspond, installs the marker with
the package, and executes the extracted packaged reader during native package
tests. USB protocol, frame assembly, controls, and application bridges are
unchanged.

## Release assets

The 51,452-byte ARM64 development package has internal Debian version
`0.2.0~alpha11-1`; GitHub uses a dot instead of the tilde in its downloadable
filename. The published checksum is:

```text
d42b85472010e06af0c811e99e723a1ed7fd45a5b76b76e11bd6cc5d8e084210  tucsen-tca-camera_0.2.0.alpha11-1_arm64.deb
```

The downloaded release asset is byte-identical to the retained tag-built
package. The downloaded `SHA256SUMS` itself has SHA-256
`4029bb44fd1ec6d3472148096b16cd57bc0a7c41bf4884f57b682d561e44a6a4`.

## Exact tag, archive, and native verification

- Tag object `d2ddb0ea9eb8d3719e8fc434b494a1c6e261e6ff` resolves to exact commit
  `6e12046b437da7a16945d7275e663df59b0abd57`.
- Exact-tag Ubuntu/macOS CI passed in
  [run 37219639595](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37219639595).
- Exact merged main and the downloaded tag archive passed the complete
  Raspberry Pi AArch64 suite with zero cameras attached. The Linux package
  test builds twice and requires byte identity, inspects package contents and
  metadata, runs both extracted installed-helper diagnostics, executes the
  extracted `tca-camera --version`, and verifies overwrite refusal.
- The downloaded tag archive passed the complete Apple Silicon suite outside
  a Git checkout with the documented scoped native-libusb path. The archive
  SHA-256 is:

```text
54676230bd063d37cb26e4f4d71d2e90f2674aa58446d80aed40c81b7ab4ed0d  tucsen-tca-camera-v0.2.0-alpha.11.tar.gz
```

- The exact package reports architecture `arm64`, Debian version
  `0.2.0~alpha11-1`, reader version `0.2.0-alpha.11`, and installs the same
  upstream marker under `/usr/share/doc/tucsen-tca-camera/VERSION`.
- Current-tree, source-archive, package, and full-history privacy checks pass;
  no vendor binary, disassembly, firmware, packet capture, raw camera frame,
  VM disk, credential, or private work is published.

## Installed Raspberry Pi state

The hash-pinned package upgraded `rpios-17` from alpha 10 to alpha 11 while no
camera was attached. The package database reports `install ok installed`,
version `0.2.0~alpha11-1`, architecture `arm64`. `dpkg -V` is clean;
`tca-camera --version` and the installed marker both report alpha 11; and the
installed V4L2 and FFmpeg diagnostics resolve their sibling tools and end with
`NO USB TRANSFER SENT`.

This gives the next physical Linux run an unambiguous executable identity. It
does not itself prove USB enumeration or frame delivery from the Pi.

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
deferral. Alpha 11 is a truthful provenance correction, not final acceptance.
