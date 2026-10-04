# Packaged FFmpeg live-view and recording helper

Date: 2026-10-04

## Purpose

The public reader already produced a Bayer8 stdout stream consumable by
FFmpeg, FFplay, GStreamer, or OpenCV. `tca-ffmpeg` makes the most common
ordinary-application paths one command while keeping the camera protocol in
the existing reader and retaining raw provenance.

The helper supports:

- `--view`: an unbounded physical-camera stream in an ordinary FFplay window;
- `--record`: an exact bounded frame count encoded as H.264 by FFmpeg;
- mode 2 at 1280x960 and mode 0 at 3664x2748;
- explicit exposure, normalized gain, and media time base;
- an untouched first device record and a monotonic producer timestamp CSV;
- source-tree and installed sibling-reader discovery; and
- a USB-inert install diagnostic.

It contains no libusb or request tuple and cannot issue arbitrary camera
commands. It rejects overwrite, path conflicts, invalid modes, and invalid
ranges before starting the reader. It terminates the producer if the viewer
closes or the FFmpeg consumer fails.

## Automated verification

Candidate commit `f524560086a51672484c9aaea0cef29839da253a` passed the complete
Apple Silicon suite. Dynamic camera-free tests exercised successful view and
record pipelines, exact byte delivery, timestamp retention, output collision,
invalid mode, install diagnostics, and a failing consumer that exits before
opening the FIFO. The failure case returned the consumer status without
hanging and terminated the blocked reader.

The helper was included in staged install and exact-file removal. The unrelated
sentinel remained after uninstall. Publication-boundary and Pages tests passed.

PR [#20](https://github.com/la3lma/tucsen-tca-camera/pull/20) merged the helper
as public main `f297834bf62a7dc6c7c098926a5b9261abb401e8`. Independent Ubuntu
and macOS pull-request checks and post-merge main checks passed.

## Physical recording

The exact candidate ran against the microscope camera directly attached to the
Apple Silicon workstation. At mode 2, requested 250 ms, gain 0, and a 10-fps
media time base, one command delivered exactly 12 frames to ordinary FFmpeg:

```text
frames=12 status=ok
recording=.../preview.mp4 frames=12 mode=2 geometry=1280x960 fps=10 status=ok
```

Measured producer evidence reported:

- 12 timestamped frames;
- 9.494922 delivered fps over 1.158514 seconds;
- 104.693–106.253-ms intervals, mean 105.319 ms; and
- no missing or non-monotonic rows.

Independent FFprobe inspection reported H.264, 1280x960, `yuv420p`, 10/1
media time base, 1.2 seconds, and exactly 12 decoded frames. A complete FFmpeg
decode exited zero without diagnostics. The MP4 SHA-256 is
`4b73c5738f94679c93d8424626a42910ce88c30482d08a9a3c4f06e0baaa063c`.

A fresh process immediately reopened the camera and captured a complete frame.
Its Bayer SHA-256 is
`003c3a36a63888b82f608f3d27cd22ec6600025dcbd29f456725dd606376377a`;
statistics found min 19, max 239, mean 178.7346, zero zero-valued pixels, and
zero saturated pixels.

The raw record, Bayer reopen frame, MP4, timestamp CSV, decoded PNG, statistics,
and verified manifest remain private under the report project's
`work/tca-ffmpeg-live-f524560/` directory; none is redistributed in the public
source.

## Raspberry Pi portability

After merge, `rpios-17` fast-forwarded to exact public main `f297834`. The
complete AArch64 suite passed, including the dynamic helper tests and staged
installation. The source-tree diagnostic resolved the native AArch64 reader,
FFmpeg, and FFplay and printed `NO USB TRANSFER SENT`. The camera count was
zero because it remained on the Mac.

This proves the packaged helper and failure behavior on Linux but does not
replace the still-open direct-Pi physical V4L2 application run.

## Result

- One-command physical camera to playable H.264 file: **PASS on macOS**
- Exact measured producer sidecar and raw provenance: **PASS**
- Immediate camera reopen: **PASS**
- Ubuntu/macOS CI and Raspberry Pi AArch64 suite: **PASS**
- Discoverable Linux `/dev/video*` with the directly attached camera:
  **still requires the prepared cable move and live V4L2 gate**
