# Reproducible Debian package and native AArch64 installation

Date: 2026-10-04

Public main commit `30c31e2286127059f7917ca1afccf75703413b55`,
merged through [PR #27](https://github.com/la3lma/tucsen-tca-camera/pull/27),
adds an architecture-native Debian binary-package path for the Linux-first
reader. This closes the gap between a tested staged `make install` and a
package that a Raspberry Pi OS, Debian, or Ubuntu user can inspect, install,
verify, and remove through the normal package database.

## Package boundary

`make deb` invokes a rootless builder. It compiles the existing public
userspace programs, stages them under `/usr/bin`, adds the exact
`0547:c003` udev rule under `/usr/lib/udev/rules.d`, installs the public
protocol, validation, optical, license, notice, changelog, and README
documents, and emits one native `.deb` under the ignored `dist/` directory.

The binary package:

- contains the seven existing independently developed programs;
- depends on `libc6`, `libusb-1.0-0`, and `python3`;
- recommends FFmpeg, V4L2 utilities, `v4l2loopback`, and their ordinary
  system helpers;
- installs no camera-specific kernel code;
- safely reloads udev rules after installation or removal, without resetting
  or opening any USB device;
- uses a pinned `SOURCE_DATE_EPOCH`, root-owned archive metadata, exact-model
  permission matching, and collision refusal; and
- includes a dynamic Linux test that builds twice, requires byte-identical
  packages, inspects control/data archives, extracts all files, executes both
  installed-helper diagnostics, and verifies overwrite refusal.

The builder and both diagnostics explicitly finish with
`NO USB TRANSFER SENT`.

## Exact-main Raspberry Pi proof

The exact merged main commit built and passed the complete suite on AArch64
host `rpios-17`. No `0547:c003` camera was attached. The Linux-only package
test built two temporary packages from the same source/toolchain and required
identical SHA-256 digests before inspecting their contents and executing the
extracted `tca-v4l2 --diagnose-install` and
`tca-ffmpeg --diagnose-install` paths.

A separately retained exact-main package reported:

| Field | Value |
|---|---|
| Package | `tucsen-tca-camera` |
| Version | `0.2.0~alpha10-1` |
| Architecture | `arm64` |
| Size | 51,056 bytes |
| SHA-256 | `269eb45f5c5bc6988bc9a59b73247a48f1c389fb1035121b78b0a22a7a9efdd2` |

The same digest was produced before and after the PR squash merge, demonstrating
that the fixed build inputs do not depend on the Git commit identifier. The
exact-main archive was installed with `dpkg -i`, which reported
`install ok installed`. `dpkg -V tucsen-tca-camera` returned no modified
files. Both installed diagnostics resolved `/usr/bin/tca-camera` plus their
required sibling tools and ended with `NO USB TRANSFER SENT`.

## Native removal and reinstallation lifecycle

The installed package was subsequently exercised through a complete native
package lifecycle on `rpios-17`, again with no `0547:c003` camera attached.
Before mutation, the retained archive was re-hashed to the value above and
the package database reported `install ok installed`, version
`0.2.0~alpha10-1`, architecture `arm64`.

`dpkg --remove tucsen-tca-camera` completed successfully. Debian retained the
normal `deinstall ok config-files` database state, but every delivered helper,
the exact-model udev rule, and `/usr/share/doc/tucsen-tca-camera` were absent.
The same archive was then installed again with `dpkg -i`. The final state was
`install ok installed`; `dpkg -V` was empty, the camera remained absent, and
both installed diagnostics again resolved their sibling tools and ended with
`NO USB TRANSFER SENT`.

The first lifecycle harness expected the package record itself to disappear
after `--remove` and stopped after successful removal. Inspection showed that
the delivered paths were gone and the package database was in Debian's normal
non-installed state. The exact package was restored immediately, and the
corrected lifecycle was then repeated from beginning to end. This records the
test-harness correction rather than hiding it and leaves the Pi in the desired
installed state.

Hosted Ubuntu and macOS CI passed on exact main in
[run 37216640301](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37216640301).
The macOS lane verifies the rest of the portable suite and explicitly skips the
Linux-only `dpkg-deb` test; the Ubuntu and Raspberry Pi lanes execute it.

## Scope and remaining gate

The native package is now installed on `rpios-17`, so the Pi is prepared for
the direct-cable Linux acceptance run when the camera is moved from the Mac.
This evidence proves package construction, contents, installation, removal,
reinstallation, integrity, helper discovery, and udev deployment. It does not
claim camera enumeration, frame transfer, or V4L2 application consumption from
the installed package; the bounded physical Linux gate remains open.

No vendor binary, disassembly, firmware, packet capture, raw camera frame, or
credential is included in the public repository or package.
