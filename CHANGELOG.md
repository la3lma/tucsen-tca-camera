# Changelog

## Unreleased

- Add a dependency-free Bayer-frame statistics and focus utility.
- Add a reproducible microscope-mounted optical validation procedure covering
  Bayer phase, orientation, exposure, gain, focus, full resolution, and the
  V4L2 application boundary.

## 0.2.0-alpha.2 — 2026-10-03

- Relicense the project from the MIT License to the Apache License 2.0.
- Verify cold capture after a connected-camera Raspberry Pi reboot.
- Verify the Apple Silicon reader against the physical camera through a
  one-device VirtualHere relay, then return ownership to Linux.
- Add an explicit, two-frame maximum initial resynchronization window. This
  recovers a stale leading frame observed after relay handoff while preserving
  the untouched first device frame and never retrying marker loss after the
  first application frame has been delivered.

## 0.2.0-alpha.1 — 2026-10-03

- Add physically verified 3664×2748 Bayer8 capture as explicit `--mode 0`;
  1280×960 mode 2 remains the default.
- Apply each mode's recovered row time to bounded exposure conversion.
- Record a successful 14,400-frame mode-2 endurance run and consecutive
  three-frame captures in both supported modes.
- Flush the untouched first device frame immediately so a later interruption
  cannot leave its final buffered packet absent from the evidence file.
- Correct the documented full-sensor geometry to 3664×2748.

## 0.1.0-alpha.1 — 2026-10-03

- Cold initialization of USB `0547:c003` in 1280×960 mode.
- Continuous Bayer8 capture from endpoint `0x82`.
- Validation and repair of three ten-byte transport markers per frame.
- Preservation of the first untouched 1,229,312-byte device frame.
- Bounded exposure (1–480 ms) and normalized gain (0–320) controls.
- Binary stdout/file stream for FFmpeg, GStreamer, OpenCV, or network use.
- Optional temporary V4L2 adapter using distribution `v4l2loopback`.
- Strict C17 build and inert/static safety tests on Linux and macOS.
