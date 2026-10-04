# Public prerelease v0.2.0-alpha.10

Date: 2026-10-04

## Result

The annotated public tag `v0.2.0-alpha.10` resolves to exact commit
`d0bbdd23fecbe4fc046e3e4e0f1fa064a81eb1e8` and is published as a GitHub
prerelease:

<https://github.com/la3lma/tucsen-tca-camera/releases/tag/v0.2.0-alpha.10>

Alpha 10 makes the Linux-first reader directly installable on 64-bit
Raspberry Pi OS and Debian. The release attaches the 51,056-byte development
package `tucsen-tca-camera_0.2.0.alpha10-1_arm64.deb`; GitHub normalizes the
Debian-version tilde in the build filename to a dot, while the package's
internal version remains `0.2.0~alpha10-1`.

The package installs the seven public userspace tools, exact `0547:c003` udev
rule, and public documentation. It supplies no camera-specific kernel driver.
Its maintainer hooks reload udev rules only and perform no USB open, reset, or
transfer. The release remains Apache-2.0 licensed.

## Exact tag, archive, and CI verification

- Exact main `d0bbdd2` passed Ubuntu/macOS CI in
  [run 37218067546](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37218067546),
  and its Pages deployment passed in
  [run 37218067547](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37218067547).
- The annotated tag independently passed Ubuntu/macOS CI in
  [run 37218214078](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37218214078).
- The exact tag passed the complete Raspberry Pi AArch64 suite with no camera
  attached. The Linux package test built twice and required byte identity,
  inspected metadata and contents, exercised extracted installed-helper
  diagnostics, and verified collision refusal.
- The downloaded tag source archive was extracted outside a Git checkout and
  passed the complete suite on both Apple Silicon and Raspberry Pi AArch64.
  Its SHA-256 is:

```text
1e1254bb1105a3ab3034ada3716402f76ec64ff0758aafc4fb000a83a15fb738  tucsen-tca-camera-v0.2.0-alpha.10.tar.gz
```

- The exact-tag Raspberry Pi build reproduced the earlier package byte for
  byte. The release asset was downloaded back into the private project and
  passed the published checksum:

```text
269eb45f5c5bc6988bc9a59b73247a48f1c389fb1035121b78b0a22a7a9efdd2  tucsen-tca-camera_0.2.0.alpha10-1_arm64.deb
```

- The release asset reports architecture `arm64`, package version
  `0.2.0~alpha10-1`, dependencies on `libc6`, `libusb-1.0-0`, and `python3`,
  and recommendations for FFmpeg and the ordinary V4L2 application stack.
- The exact tag, source archive, package, and public history pass the permanent
  publication boundary: no raw frame, vendor binary, disassembly, firmware,
  packet capture, VM disk, credential, or private work is included.

## Native package lifecycle

The same package passed the following camera-free lifecycle on `rpios-17`:

1. package database reported `install ok installed`, version
   `0.2.0~alpha10-1`, architecture `arm64`;
2. `dpkg --remove` cleared all seven helpers, the exact-model udev rule, and
   package documentation;
3. reinstallation of the same hash-pinned archive restored the installed
   state and `dpkg -V` returned no modified file;
4. both installed diagnostics resolved all sibling tools and reported
   `NO USB TRANSFER SENT`; and
5. a local-file `apt-get install --reinstall` completed without downloading
   another package or adding a dependency, after which integrity and both
   diagnostics still passed.

The Pi is deliberately left with the package installed and the camera remains
on the Mac.

## Carried physical-camera evidence

Alpha 10 contains the same reader and helper already proved by alpha 9 against
the Mac-attached microscope. The downloaded alpha-9 archive recorded 30
complete 1280x960 frames at 9.508016 measured fps; independent H.264 decoding
returned 30 distinct frames, and a fresh process immediately reopened the
camera. Alpha 8 remains the 30-minute endurance authority: 17,200 distinct
preview frames passed through independent FFmpeg with bounded memory and
immediate reopen.

This carried proof establishes package contents and the application-facing
reader behavior, not physical USB transport from the newly attached ARM64
package on the Pi.

## Explicit residual gates

This is a development prerelease, not final acceptance. The remaining physical
work is unchanged:

1. move the camera to the Raspberry Pi and execute the prepared uncorrected
   preview and full-resolution V4L2 application gates;
2. acquire true blocked-light dark and translated/defocused blank-field flat
   sets at locked settings, then repeat the physical Linux gate with the
   accepted map;
3. confirm Bayer phase, orientation, color response, and focus behavior with a
   known target; and
4. complete the physical cable disconnect/reconnect acceptance case.

AVFoundation/system-wide macOS camera discovery remains a non-blocking
deferral. The portable reader and packaged FFplay/H.264 path work on macOS
without it.
