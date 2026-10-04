# User-space flat-field and V4L2 preflight

Date: 2026-10-04

## Result

Public commit [`1dc096b`](https://github.com/la3lma/tucsen-tca-camera/commit/1dc096b)
adds `tca-flat-field`, a portable C17 dark/flat calibrator and streaming Bayer
corrector. It stores explicit image geometry and Bayer phase with a fixed-point
per-pixel mean dark level and gain. R, G1, G2, and B use separate median
references, so correction removes spatial shading without silently performing
white balance. The optional `TCA_FLAT_FIELD` path inserts it before FFmpeg in
the existing user-space V4L2 bridge.

The complete native test suite passed on Apple Silicon and Raspberry Pi 5.
AddressSanitizer plus UndefinedBehaviorSanitizer also passed the deterministic
calibration/application test on Apple Silicon (with leak detection disabled
because the host sanitizer runtime aborted before the test itself).

## Raspberry Pi application-boundary preflight

The token-gated harness created full 1280x960 GRBG streams with two dark frames
at value 10, two flat frames at value 110, and six input frames at value 60.
Calibration and streaming application produced six uniformly corrected Bayer
frames at the expected value 50. FFmpeg converted those frames to YUYV and a
separate `v4l2-ctl` process consumed all six from a temporary `/dev/video43`.
The YUYV evidence was exactly 14,745,600 bytes. The harness then removed the
device and module that it had loaded.

```text
calibration_bytes=4915264
corrected_bayer_bytes=7372800
v4l2_yuyv_bytes=14745600
corrected_frames=6
v4l2_frames=6
status=ok
```

The retained evidence bundle is under
`work/pi-flat-field-v4l2-preflight/`. Its manifest verifies the calibration,
source streams, corrected stream, V4L2 output, and logs.

## Performance and scope

Applying the calibration to 60 preview frames (73,728,000 input bytes) took
0.267 seconds on the Pi, approximately 225 frames/s. The filter is therefore
not a practical bottleneck at the camera's observed rate.

This run verifies deterministic calibration math, complete-frame streaming,
performance, Bayer conversion, the generic Linux application boundary, and
cleanup. It does **not** establish a physical optical correction: the real dark
and flat series still need to be captured with the camera on the microscope,
using fixed optical and camera settings.

## Reproduction

From the public repository on ARM64 Linux, after installing FFmpeg,
`v4l2loopback`, and `v4l-utils`:

```sh
make clean all test
sudo tools/run_flat_field_v4l2_preflight.sh --run-flat-field-v4l2-preflight
```

The explicit token prevents an accidental root/module operation. The harness
refuses a pre-existing target device and removes only the loopback module it
loaded itself.
