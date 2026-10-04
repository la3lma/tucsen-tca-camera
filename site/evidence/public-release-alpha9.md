# Public prerelease `v0.2.0-alpha.9`

Date: 2026-10-04

## Result

The annotated public tag `v0.2.0-alpha.9` resolves to exact commit
`a254f53018fc6513200a525c6512bd1a997f7b80` and is published as a GitHub
prerelease:

<https://github.com/la3lma/tucsen-tca-camera/releases/tag/v0.2.0-alpha.9>

Alpha 9 packages the recovered camera as a practical application-facing tool:
`tca-ffmpeg` provides a one-command FFplay live view or exact-count H.264
recording in both recovered geometries while retaining the untouched first
device record and producer timestamps. The helper supervises the existing
reader and contains no duplicate USB protocol or arbitrary request surface.

The release also contains corrected installed-helper discovery, a USB-inert
installation diagnostic, producer/consumer timing, both Linux V4L2
geometries, camera-free application detach/reattach and slow-consumer tests,
the bounded uncorrected physical Linux gate, Docstack 5.0, the 17-page report,
and rendered public evidence. It remains Apache-2.0 licensed and entirely in
user space.

## Independent verification

- [PR #24](https://github.com/la3lma/tucsen-tca-camera/pull/24) prepared the
  release changelog and passed all Ubuntu/macOS pull-request checks.
- Exact main `a254f53` passed independent post-merge Ubuntu/macOS CI in
  [run 37215043641](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37215043641),
  and its Pages deployment passed in
  [run 37215043591](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37215043591).
- The annotated tag independently passed Ubuntu/macOS CI in
  [run 37215098691](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37215098691).
- Exact commit `a254f53` passed `make clean && make test` on Raspberry Pi
  AArch64. The Pi then fetched the annotated tag and proved that it resolves to
  that same tested commit. The camera remained on the Mac, so this run was
  USB-inert.
- GitHub's source archive was downloaded into the private report project,
  extracted outside a Git checkout, and passed the complete suite on Apple
  Silicon and Raspberry Pi AArch64. Both hosts measured the same SHA-256:

```text
97750800e90783aaf606c160fdd33925f60e56b7f7464113077c5524b259ea52  tucsen-tca-camera-v0.2.0-alpha.9.tar.gz
```

- The Apple Silicon host's default `pkg-config` reproduced the known
  mixed-Homebrew failure by selecting Intel libusb. The documented scoped
  `LIBUSB_PKG_CONFIG_PATH` selected the project-local native ARM64 library and
  the complete exact-main and downloaded-archive suites passed.
- The release commit, exact tag, and downloaded archive pass the permanent
  current-tree/full-history publication boundary: no raw frames, vendor
  binaries, disassembly, firmware, packet captures, VM disks, or private work
  are included.

## Exact-release physical application verification

After publication, the downloaded source archive's packaged helper ran against
the directly attached microscope camera in mode 2 at requested 250 ms, gain 0,
and a 10-fps media time base. It recorded exactly 30 complete 1280x960 frames.
Producer timing reported 9.508016 delivered fps over 3.050058 seconds, with
103.798-107.309-ms intervals, mean 105.174 ms, median 105.101 ms, and p95
106.780 ms. The untouched first device record was exactly 1,229,312 bytes.

Independent FFprobe/FFmpeg validation reported H.264, YUV420P, 1280x960,
exactly 30 decoded frames over 3.000 seconds, 30 distinct decoded frame hashes,
and no decoder diagnostics. The MP4 SHA-256 is
`0b26cd5659facee00526a27ab6a3572fe124caf03a2f2dea274e479d2a3b2be9`.

A fresh exact-release process immediately reopened the camera and captured
another complete 1,228,800-byte Bayer frame. Its SHA-256 is
`26aece6a8deb70212852fd01395768b0ef98dfad272462d7946044ba3b17b33e`;
statistics reported min 20, max 241, mean 178.8566, p01 79, p99 221, zero
zero-valued pixels, and zero saturated pixels. Raw, Bayer, timestamp, and video
artifacts plus a verified manifest remain private in the report project.

## Earlier application evidence carried into the release

Candidate `f524560`, merged before the release as public main `f297834`, ran
the packaged helper against the Mac-attached microscope camera at mode 2,
requested 250 ms, gain 0, and a 10-fps media time base. The reader delivered
exactly 12 complete 1280x960 frames at 9.494922 measured fps with
104.693-106.253-ms intervals. Independent FFprobe/FFmpeg validation decoded
exactly 12 H.264 frames without errors, and a fresh process immediately
reopened the camera and captured another complete unclipped Bayer frame.

The earlier exact alpha-8 archive remains the long-duration application
authority: 17,200 distinct preview frames passed through independent FFmpeg
over 1,809.739 seconds with bounded reader/consumer memory, exact decode
counts, no FFmpeg diagnostics, and immediate camera reopen. Alpha 9 packages
the ergonomic wrapper around that already-proven reader/consumer boundary.

## Explicit residual gates

This is a useful prerelease, not final acceptance. The remaining physical work
is unchanged:

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
