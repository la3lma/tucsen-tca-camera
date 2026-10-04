# Exact alpha-8 30-minute live application endurance

Date: 2026-10-04

## Result

The downloaded public `v0.2.0-alpha.8` archive at commit
`2dd0b395e033d0a68410ac03e5b549ea534caeac` drove the physical `0547:c003`
camera on Apple Silicon for 17,200 mode-2 frames at requested 250 ms exposure
and gain 0. Its Bayer stdout was consumed live by independent FFmpeg, which
computed a checksum for every input frame while simultaneously encoding H.264.

The run had a 2,200-second process-group deadline. Reader, FFmpeg, and
supervisor all exited zero; the deadline did not fire.

| Property | Measured result |
|---|---:|
| Reader result | `frames=17200 status=ok` |
| Measured producer duration | 1,809.739289 s |
| Measured producer cadence | 9.5035788 fps |
| Input frames/checksums | 17,200 / 17,200 |
| Distinct frame checksums | 17,200 |
| Bayer bytes consumed | 21,135,360,000 |
| Interval p50 / p95 | 105.211 / 105.801 ms |
| Interval mean / standard deviation | 105.224 / 1.843 ms |
| Maximum interval | 302.854 ms before frame 204 |
| Decoded H.264 frames | 17,200 |
| H.264 geometry and duration | 1280x960; 1,810.114753 s |
| H.264 file size | 184,420,285 bytes |

FFmpeg emitted no diagnostics. Sixty 30-second memory samples showed the
project reader between 9,872 and 9,904 KiB RSS, ending at 9,888 KiB. FFmpeg
began at 186,248 KiB and peaked and ended at 217,096 KiB. Its complete observed
growth was 30,848 KiB; from the five-minute sample onward it grew 12,304 KiB.
Both values remain below the existing 65,536-KiB application-pipeline bound.

Immediately afterward, a fresh exact alpha-8 process reopened the same camera
and captured one exact-size mode-2 frame with the same controls. It returned
`frames=1 status=ok`; the frame had mean 178.597, p01 78, p99 221, and no zero
or saturated pixels.

## Visual sample across the run

The following compact derivative selects one frame every 300 source frames,
yielding 58 samples across the complete recording. Its 9.577-second playback
is a time-lapse, not the authoritative timing record.

<video controls preload="metadata" poster="images/alpha8-endurance-midpoint.jpg" width="100%">
  <source src="videos/alpha8-endurance-timelapse.mp4" type="video/mp4">
  <a href="videos/alpha8-endurance-timelapse.mp4">Download the endurance time-lapse.</a>
</video>

[Download the compact time-lapse](videos/alpha8-endurance-timelapse.mp4) or
[open the midpoint frame](images/alpha8-endurance-midpoint.jpg).

## Integrity

```text
7f45b6c99aa78b86ea324df2b474a9021a4c123dfcea644229689ced42fc6384  retained full 30-minute H.264 recording
ffe4c123862bdbb6c36cde9b1f01d0d035f776c6989c722b33821fdc3923d2ee  retained 17,200-row frame checksum ledger
29701e3f07812e9c353345cfa2a2184a8f0ebe886c9d177b5732799d5069ff59  retained reader timestamp CSV
736a9cec21a064a199023ab32955c66f07fb9a021cd6f3c3e1cc1ae8ed8c1582  published 58-sample time-lapse
a4fd8c02248d5f68cd632dc8a6bc27f029742f9fd76205e8dc1138a05ac4651d  published midpoint JPEG
```

The private evidence bundle retains the full recording, timestamp and frame
checksum ledgers, 60-sample process-memory series, before/after USB inventory,
immediate-reopen raw frame and analysis, command logs, and a verified SHA-256
manifest.

## Acceptance effect and limits

This closes a corrected-era 30-minute endurance and ordinary-application
consumption proof for the exact public alpha-8 reader on Apple Silicon, plus
immediate reuse after the long session. The result demonstrates bounded memory
for this run; it does not claim constant-memory behavior for arbitrarily long
MP4 files. Provisional GRBG/color treatment remains illustrative. The pending
physical Linux V4L2 camera run, true dark/blank-flat session, and known-target
Bayer/color acceptance remain open.
