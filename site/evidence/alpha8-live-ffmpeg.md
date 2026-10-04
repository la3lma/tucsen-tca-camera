# Exact alpha-8 live FFmpeg application proof

Date: 2026-10-04

## Result

The downloaded public `v0.2.0-alpha.8` archive's native Apple Silicon reader
streamed 60 live mode-2 Bayer frames from the Mac-attached `0547:c003` camera
through a plain standard-output pipe into an independent FFmpeg process:

```text
0547:c003 camera -> exact alpha-8 reader -> Bayer8 stdout -> tee -> FFmpeg -> H.264 MP4
```

The reader requested 250 ms exposure and gain 0. FFmpeg interpreted the stream
as 1280x960 provisional-GRBG Bayer8, applied the previously measured
illustrative neutral-field multipliers, and encoded H.264 with `libx264` into
an MP4 container. Reader, `tee`, and FFmpeg all exited successfully. No
project-specific FFmpeg plugin or kernel camera driver was involved.

## Measured evidence

| Property | Measured result |
|---|---:|
| Reader result | `frames=60 status=ok` |
| Exact Bayer bytes consumed | 73,728,000 |
| Distinct per-frame SHA-256 values | 60 of 60 |
| Reader cadence | 9.50761 fps over 6.205558 s |
| Reader intervals | min 90.488 ms; p50 105.163 ms; p95 106.392 ms; max 118.594 ms |
| Encoded stream | H.264, 1280x960, `yuv420p` |
| Decoded MP4 frames | 60 |
| MP4 duration and size | 6.314354 s; 1,659,870 bytes |
| First Bayer frame | mean 178.549; p01 79; p99 221; zero/saturated 0/0 |

The MP4 input time base was explicitly set to 9.50216 fps. The independently
recorded reader timestamp sidecar, summarized above, is therefore the
authoritative measurement of producer cadence.

<video controls preload="metadata" poster="images/alpha8-live-preview-poster.jpg" width="100%">
  <source src="videos/alpha8-live-preview.mp4" type="video/mp4">
  <a href="videos/alpha8-live-preview.mp4">Download the H.264 proof clip.</a>
</video>

[Download the H.264 proof clip](videos/alpha8-live-preview.mp4) or
[open its poster frame](images/alpha8-live-preview-poster.jpg).

Published artifact hashes are:

```text
17c981d1c2d3cccc40f0e76a2a6590147a4d523a463ee92c5d254fdc45ed1adc  alpha8-live-preview.mp4
ab8d909bcd3fc3a66fe4e4f080c68a51a36b9be76e27ae8a8c6c76a15ebc299e  alpha8-live-preview-poster.jpg
```

## Acceptance effect and limits

This proves that a normal third-party userspace application can consume and
record the exact public release's live camera stream on macOS through a plain
pipe. The clip is direct evidence of the application boundary, not merely a
camera-reader fixture or an offline conversion.

The GRBG phase and color treatment remain provisional, so the displayed color
is illustrative rather than a completed calibration. This result also does
not make the camera enumerate as a system-wide macOS camera, and it does not
replace the pending physical Linux V4L2 application run with the camera moved
to the Raspberry Pi.
