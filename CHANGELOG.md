# Changelog

## Unreleased

- Allow the Linux V4L2 bridge to opt into the reader's monotonic timestamp CSV
  through `TCA_TIMESTAMPS`, preserving producer cadence evidence alongside a
  separately measured ordinary-application consumer run.
- Add an inert-by-default Linux V4L2 acceptance harness that composes a valid
  flat-field map, producer timing, bounded application consumption, frame
  digests, cleanup, immediate reopen, and a complete evidence manifest.

## 0.2.0-alpha.7 — 2026-10-04

- Add optional per-frame `CLOCK_MONOTONIC` timestamp CSV output to the capture
  CLI without changing the USB protocol or default Bayer output format.
- Flush each timestamp row for useful bounded and interrupted-run timing
  evidence, and reject conflicting or stdout timestamp paths before transfer.
- Add `tca-timing-stats` and record direct-Apple-Silicon delivered-frame
  cadence of 17.3466 fps for 1280x960 at requested 1 ms, 9.5057 fps for
  1280x960 at 250 ms, and 2.7911 fps for 3664x2748 at 250 ms. These are
  application-facing output measurements, not sensor-integration claims.
- Document the distinction between measured capture timing and an FFmpeg
  playback time base.
- Add `tca-flat-field`, a dependency-free C17 calibrator and streaming
  corrector for per-pixel dark subtraction and per-Bayer-plane flat-field
  gain correction before demosaicing.
- Allow `tca-v4l2` to insert a validated 1280x960 GRBG flat-field map through
  `TCA_FLAT_FIELD` while leaving the existing uncorrected bridge as the
  default.
- Store optional exposure/gain provenance in the backward-compatible
  calibration header and require an exact settings match for corrected V4L2
  streaming.
- Add a token-gated ARM64 Linux preflight that exercises calibration,
  correction, Bayer conversion, a temporary V4L2 loopback device, application
  consumption, evidence hashing, and cleanup without requiring the camera.
- Add an inert-by-default guided physical-calibration session that keeps dark,
  repositioned-flat, withheld-blank, and specimen captures at locked settings,
  validates exact sizes, renders comparisons, and hashes the completed bundle.
- Render every public evidence record as navigable HTML, link the README,
  Docstack, evidence index, and report to one another, and publish a clickable
  Agency-style task dependency graph plus compact Cockburn/UML use cases.
- Make the public/private boundary permanent with a current-tree and full-Git-
  history denylist for disassembly, decompiler exports, vendor binaries,
  firmware, packet captures, VM disks, and private work artifacts.

## 0.2.0-alpha.6 — 2026-10-04

- Preserve white-balance channel ratios when an estimated multiplier exceeds
  FFmpeg's `colorchannelmixer` limit by scaling all three output multipliers
  together into the accepted range.
- Verify unclipped 10× microscope captures at gain 0 in both 1280×960 preview
  and complete 3664×2748 still modes.

## 0.2.0-alpha.5 — 2026-10-04

- Assemble full-resolution frames across their physical record boundary. Each
  mode-0 frame consists of 10,068,480 bytes after offset 512 in record N plus
  a 192-byte continuation at offset 320 in record N+1. This removes the false
  left strip while retaining every one of the 3664×2748 pixels.
- Add `tca-white-balance`, a dependency-free neutral-background Bayer-channel
  estimator that emits reproducible gains and an FFmpeg filter.
- Verify three consecutive complete 3664×2748 frames and a three-frame
  1280×960 regression sequence over the direct Apple Silicon connection.

## 0.2.0-alpha.4 — 2026-10-04

- Correct frame acquisition to use one bulk request per complete device record.
  Separate 524,288-byte requests restart at the record origin and had produced
  repeated image regions and a false horizontal seam.
- Decode the Bayer raster after the record prefix: 512 bytes in 1280×960 mode
  and 320 bytes in 3664×2748 mode.
- Accept the narrowly observed macOS control response of one byte exactly equal
  to the request, while continuing to reject every other short response.
- Verify optically coherent microscope images, multi-resolution stills, and an
  eight-frame motion sequence over a direct Apple Silicon connection.
- Consume the one pre-control record already buffered by the device so the
  first published frame reflects requested exposure and gain.
- Verify monotonic analog-gain response across 0..320 and capture a brighter,
  16-frame 100-ms/gain-256 motion sequence with 16 distinct frames.

## 0.2.0-alpha.3 — 2026-10-03

- Add a dependency-free Bayer-frame statistics and focus utility.
- Add a reproducible microscope-mounted optical validation procedure covering
  Bayer phase, orientation, exposure, gain, focus, full resolution, and the
  V4L2 application boundary.
- Document and test staged installation and exact-file removal of the reader,
  V4L2 helper, and frame analyzer.

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
