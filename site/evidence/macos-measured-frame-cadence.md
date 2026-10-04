# Apple Silicon measured delivered-frame cadence

Date: 2026-10-04

Public implementation commit:
[`064cf31`](https://github.com/la3lma/tucsen-tca-camera/commit/064cf317bce660a3044e76755b6c3bc93e874b0b)

## Purpose

Replace chosen FFmpeg playback rates and whole-process wall times with one
monotonic timestamp for each complete Bayer frame accepted by the reader's
output stream. This is an application-facing delivery measurement. It is not
an embedded sensor timestamp, a proof of the actual integration time, or a
clock recovered from the camera.

The public reader now accepts an optional `--timestamps FILE.csv` path. It
writes the exact header `frame,monotonic_ns` and, after each successful Bayer
frame write, records one `CLOCK_MONOTONIC` value and flushes the row. The
option does not add a USB request or change the default Bayer stream. It is
rejected before transfer if it is stdout or conflicts with either image path.
The new `tca-timing-stats` command rejects malformed headers, frame-number
gaps, non-monotonic time, fewer than two frames, and output overwrite before
reporting cadence as JSON.

## Physical device and exact code

The camera remained directly connected to the Apple Silicon workstation and
enumerated at high speed as `0547:c003`, product `10MP CMOS Camera`, USB
address 24. No reset, configuration change, firmware action, or new request
tuple was used. Only the previously validated mode selector, exposure, gain,
initialization, and bulk-IN record reads were executed.

The complete local suite passed before capture. Exact build inputs and binary:

```text
3220ed86d5b7aca929ffba66b8d860bbb16145b07edfc851054cdf3844abb033  src/tca_camera.c
98bda4bfe033683bef82108fba5c3088be72b824d406b3921ea00e59747164c4  scripts/tca-timing-stats
c04d9b732ad25612c404ac3737bfe1485afb8fc57ede9e6da48e65dcc9dcba34  build/tca-camera
```

## Results

Each run programmed its requested controls, discarded the one pre-control
buffered record, returned `status=ok`, produced the exact expected Bayer byte
count, and wrote exactly one timestamp row per frame. Frame-by-frame hashing
found 60/60, 30/30, and 12/12 distinct frame hashes respectively.

| Mode and requested controls | Frames | Bayer bytes | Measured span | Delivered fps | Interval p50 / p95 / max |
|---|---:|---:|---:|---:|---:|
| 1280x960, 1 ms, gain 0 | 60 | 73,728,000 | 3.401246 s | 17.3466 | 55.782 / 68.478 / 101.744 ms |
| 1280x960, 250 ms, gain 0 | 30 | 36,864,000 | 3.050803 s | 9.5057 | 105.179 / 105.799 / 105.973 ms |
| 3664x2748, 250 ms, gain 0 | 12 | 120,824,064 | 3.941140 s | 2.7911 | 357.589 / 363.621 / 363.621 ms |

The 1-ms preview run has a stable approximately 55.8-ms base interval plus a
small number of longer intervals. The 250-ms preview and full-resolution runs
are substantially tighter. These figures establish realistic output cadence
for the tested direct-Mac/file-output path. They do not independently validate
the recovered row-time-to-exposure mapping, and Linux V4L2 consumer timing must
still be measured after the next cable move.

## Retained artifacts

The complete private capture bundle is retained under
`work/macos-frame-timing-alpha7-final-20261004/`. It contains the untouched
first device record, concatenated Bayer stream, timestamp CSV, validated JSON
summary, and stderr transcript for each run. Its `hashes.sha256` covers all 15
artifacts and verifies completely. Raw capture files remain private; this
public evidence record contains only measurements, hashes, and independently
written conclusions.

Selected bundle hashes:

```text
45125f930e7fa5e1849b44b41af5d3cd00f6a3c657854eef26eeeb0b25acb53d  mode2-1ms-g0-60.bayer
e8dd2d734551fded685ec02caadfb39693ca3af6a048e164f74569680c697709  mode2-1ms-g0-timing.json
b31ce9e3d4f2913b26ca5e5002a13f406b1a7a27edb8fcfb22915876083910fe  mode2-250ms-g0-30.bayer
fa227a48a47f4ff47535220c72c26b9342ee3fe307ef9dcf08dd910c1aca7818  mode2-250ms-g0-timing.json
5a2d0fac592cb85ef0ed8087474b5e77a00bba3fdc8486abfdd8061090ff5bdf  mode0-250ms-g0-12.bayer
ca45f9a636750ae16c06e980d96c1966972de205f92534f6c60263f15a7d4419  mode0-250ms-g0-timing.json
```

## Remaining boundary

This closes the direct-reader cadence measurement in both recovered modes.
The physical flat-field run, known-target color/Bayer validation, and an
ordinary Linux application's timestamped corrected V4L2 consumption remain
open and deliberately require later operator/cable availability.
