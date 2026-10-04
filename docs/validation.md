# Physical validation record

This page records tests run against the original AmScope-branded
`0547:c003` camera. The earlier runs used a covered sensor and validate USB
stability, controls, lifecycle, and application integration. The final section
records the later microscope-mounted optical correction and supersedes the old
multi-request interpretation of frame assembly.

## Test bench

- Raspberry Pi 5, AArch64
- Linux 6.18.39+rpt-rpi-2712
- libusb 1.0.28
- GCC 14.2.0
- FFmpeg 7.1.3
- physical USB identity: `0547:c003 Anchor Chips, Inc. 10MP CMOS Camera`

## USB-inert exact-device enumeration — 2026-10-04

Public main `b726322`, merged through
[PR #36](https://github.com/la3lma/tucsen-tca-camera/pull/36), adds
`tca-camera list` as the safe first command after a cable move. It initializes
libusb and reads the library's device list and cached descriptors, but its
command branch never opens a device, claims an interface, or submits a control
or bulk transfer. With the camera attached directly to Apple Silicon macOS,
the command reported exactly one high-speed match:

```text
target=0547:c003
camera=0 bus=8 address=24 speed=high
camera-count=1
NO DEVICE OPENED OR TRANSFER SUBMITTED.
```

The bus and address are enumeration-instance diagnostics rather than stable
camera identifiers. The same command must report zero matches on the Pi before
the physical cable move; capture remains the separate, explicitly mutating
operation.

The checkout's tracked worktree and index matched commit
`607d1dcd2b678583e181fffc3fc923adb86c81dd` during the mode-2 capture,
reopen, and endurance baselines below. Native `make test` passed first. Later
sections identify the hardening commit or candidate source used for their own
physical checks.

## User-space flat-field and V4L2 preflight — 2026-10-04

The candidate user-space flat-field implementation passed its complete native
test suite on both Apple Silicon and the Raspberry Pi. A synthetic Raspberry
Pi preflight used two constant dark frames at value 10, two constant flat
frames at value 110, and six input frames at value 60. Calibration and
streaming correction produced six uniform Bayer frames at the expected value
50. FFmpeg converted those corrected frames to YUYV and a separate
`v4l2-ctl` process consumed all six through a temporary `/dev/video43`
loopback device. The resulting YUYV evidence was exactly 14,745,600 bytes.
The harness hashed its calibration, input, corrected output, V4L2 output, and
logs, then removed the device and module it had loaded.

Filtering 60 preview frames (73,728,000 input bytes) took 0.267 seconds on the
Pi, approximately 225 frames/s and therefore far above this camera's observed
rate. This is a deterministic software and application-boundary validation,
not evidence that a physical optical flat has yet been calibrated. Reproduce
the destructive, root-only loopback portion explicitly with:

```text
sudo tools/run_flat_field_v4l2_preflight.sh --run-flat-field-v4l2-preflight
```

The map format now binds calibration provenance to the camera controls. Public
commit `6eb68a7` stores the calibration exposure and normalized camera gain in
previously reserved `TCAFF01` header bytes. Old maps remain readable and can be
applied directly, but inspect with `null` settings and are deliberately refused
by `tca-v4l2`. A repeated Pi preflight recorded a 100-ms/gain-20 map and again
delivered all six corrected frames through `/dev/video43`. A deliberate
101-ms/gain-20 request exited 65 before creating a raw file or device node,
loading `v4l2loopback`, or opening the camera. Native tests on the Mac and Pi,
plus hosted Ubuntu/macOS CI, pass the change.

## Camera-free V4L2 bridge lifecycle — 2026-10-04

Candidate commit `eb8acd3` exercised the real `tca-v4l2` bridge on the Pi with
a USB-inert deterministic reader. The run retained real flat-field filtering,
FFmpeg Bayer-to-YUYV conversion, the generic loopback module, ordinary V4L2
consumers, timing analysis, signal handling, and scoped cleanup.

A first consumer received four exact frames, detached, and an eight-frame
consumer reattached with a 350-ms sleep after every buffer. The bridge stayed
alive across both lifecycles. Its complete process-tree RSS changed by only
1,184 KiB during the slow-consumer interval. The synthetic producer delivered
93 frames at 19.6613 frames/s; this is test-source cadence, not a camera claim.
TERM returned status 143 and both `/dev/video44` and the module loaded by the
bridge were absent afterward. The integration-manifest digest is
`1f6390e603b4a21fe18a19a3884243fa97c7e9256acd33d0ac3d73a5671680f5`.

The first candidate trial exposed and preserved two harness defects: zero-
based synthetic timestamp numbering and an unstable signal-exit status. The
corrected exact commit passed the complete Pi suite, the token-gated lifecycle
test, and Ubuntu/macOS CI. See the [rendered evidence
record](https://la3lma.github.io/tucsen-tca-camera/evidence/v4l2-bridge-synthetic-lifecycle.html).
This validates bridge backpressure and lifecycle behavior without USB access;
the corrected physical-camera consumer run remains open.

## Full-resolution V4L2 application path — 2026-10-04

Candidate commit `a93f538` retains the preview bridge and adds explicit mode-0
output. A USB-inert Pi run exposed a 3664x2748 YUYV `/dev/video45` node with a
20,137,344-byte image size. One ordinary consumer received two exact frames,
detached, and a delayed consumer reattached and received three exact frames.
Warm-pipeline process-tree RSS grew by 29,504 KiB under the unchanged
65,536-KiB bound; TERM status, device cleanup, module cleanup, frame digests,
and the evidence manifest all passed. The same commit repeated the complete
mode-2 lifecycle with four plus eight frames and zero warm-baseline RSS growth.

The exact commit passed the full Pi AArch64 suite and hosted Ubuntu/macOS CI.
See the [full-resolution Linux V4L2 evidence
record](https://la3lma.github.io/tucsen-tca-camera/evidence/linux-v4l2-full-resolution-application.html).
This proves both application-facing geometries without USB access. Physical
camera cadence, optical calibration, and the post-fix Linux camera run remain
open.

## Capture and reopen checks

One invocation captured 30 frames with 400-ms exposure and normalized gain 20
in 16 seconds. It exited zero with `frames=30 status=ok`.

```text
de70bb774c3b276fd3c9af897afe42f34336c16f71044c37b045886576d21954  first untouched device frame
c672509091c69fa77041847423043cb0fc9b7ef4ed09a2b3e4e2877c035ce205  30-frame Bayer stream
```

Ten additional independent processes each opened the device, applied cold
initialization, captured ten frames, released the interface, and closed the
handle. All ten succeeded: 100/100 frames in 26 seconds. This verifies
process-level release and reopen; it is not a substitute for a physical
disconnect or reboot test.

## Application boundary

The live bridge created a temporary 1280×960 YUYV V4L2 loopback device.
`v4l2-ctl` reported the expected format, and FFmpeg consumed three physical
camera frames into a lossless recording. The bridge then removed the device it
had created. This demonstrates an ordinary Linux application boundary without
a camera-specific kernel driver.

## Endurance

A 14,400-frame run at 100-ms exposure and normalized gain 20 began at
`2026-10-03T18:07:21Z` and completed 2,410 seconds later. The reader exited
zero with `frames=14400 status=ok`; its resident set remained 4,784 KiB during
observations throughout the run. The preserved 1,229,312-byte first device
frame is:

```text
49562e8cebd975f9fbbb6a9f455191fbdf22d27abdfc32fd4dc05485fa7a0020
```

## Full-resolution mode and recovery

A separately audited, one-frame-only probe changed the first initialization
selector from mode 2's `b4/c2` to the recovered mode-0 selector `b4/c0`. It
received exactly 10,068,992 bytes as nineteen 524,288-byte reads plus one
107,520-byte read. All twenty predicted ten-byte `0x88` markers passed. The
untouched device frame hash is:

```text
3fa7a539b2141b653af305a721c793be297f4ac8e40c6c1ac051f669ebcd57e4
```

An unconditional recovery command then reselected mode 2 and captured three
frames successfully. After promoting the validated geometry into the reader,
candidate source
`b909ca28564139a3bf328f7a62b7fcd873ed4fe99629316a3134e88f2cc85f93`
captured three consecutive frames in each mode. Mode 0 emitted 30,206,016
Bayer bytes (3 × 10,068,672), mode 2 emitted 3,686,400 Bayer bytes
(3 × 1,228,800), and both invocations exited zero.

The Pi then fast-forwarded to exact commit
`f35dad144d9333fc5692a31d3d310ec285a705ea` and tag
`v0.2.0-alpha.1`, rebuilt, and passed `make test`. One tagged mode-0 capture
emitted exactly 10,068,992 raw and 10,068,672 Bayer bytes; a following tagged
mode-2 capture emitted exactly 1,229,312 raw and 1,228,800 Bayer bytes. Both
processes exited zero.

## Abrupt process death and reopen

The exact tagged mode-2 reader was observed active with its complete
1,229,312-byte first-frame evidence file and then terminated with `SIGKILL`.
The shell recorded the expected status 137. Without resetting or power-cycling
the device, a new process immediately opened it and captured three frames with
`frames=3 status=ok` and exit zero. This checks host-process crash recovery.

## Host reboot and cold reopen

The Pi checkout was fast-forwarded to public commit
`71fdae1d93afe0d2cfc06a7fc3d850d0bef8c12e`, rebuilt, and passed `make test`.
With the camera connected and no reader process active, the Pi was rebooted.
The Linux boot ID changed from `d588bee0-fe1b-4dc4-a2ba-eea7b3803168` to
`77a640be-2c3b-43ce-bdeb-c1fd06bbd181`; the camera re-enumerated as a fresh USB
instance with the same `0547:c003` identity. The rebuilt reader then applied
gain 20 and 100-ms exposure and captured three preview frames with exit zero
and `frames=3 status=ok`.

```text
b30eccf5fd2e1a220c5657bf37a63ed987658fa63c2e80415f257b3f747456af  1,229,312-byte first device frame
a35f96f7beb6c4184433aaf391aaf9940d72800961a3d57e2fab0157e0247bf0  3,686,400-byte three-frame Bayer stream
```

This verifies connected-camera host-reboot recovery. Physical cable
disconnect/reconnect remains a separate hands-on test.

## Apple Silicon physical reader through a Pi relay

Public commit `c5fa44ca59256ba5f423e616a7b37f3e91fb5d02` built and passed its
tests on the Apple Silicon workstation. VirtualHere Server 4.8.8 on the Pi and
Client 6.0.3 on macOS exposed the physical `0547:c003` camera through an SSH
forward on VirtualHere's default trial port. macOS registered the device under
`AppleUSBUserHCI` at 480 Mbit/s with the expected vendor/product identity. The
public reader cold-initialized it, applied gain 20 and 100-ms exposure, and
captured three mode-2 frames with exit zero:

```text
1c0256f291ef24c0fef702b2c56d6e8b514d9c1c0e8c5687898281d2dd80b5e2  1,229,312-byte first device frame
7fb92d416b0e7718299fa4ea59ed85948bc7274de85d03ebb5e6382603a2bc29  3,686,400-byte three-frame Bayer stream
```

This proved the userspace reader's physical Apple Silicon path before direct
cable access was available. It does not provide an AVFoundation camera surface.

## Apple Silicon native-cable reader

Exact public tag `v0.2.0-alpha.3` at commit `3c16d2a` was rebuilt and passed
its complete tests on the Apple Silicon workstation. With the camera connected
directly to the Mac, IOKit reported `0547:c003` at 480 Mbit/s. The unmodified
reader applied gain 20 and 100-ms exposure, then completed:

- three 1280×960 preview frames;
- one 3664×2748 full-resolution frame; and
- a fresh-process return to one 1280×960 preview frame.

Each successful run reported exact device and Bayer byte counts and exited
with `status=ok`. The Bayer payload hashes were:

```text
af771bca314f99f542e77f982f6da494abe054b8d7b4f594d6a9c1f841f0a330  three preview frames
80bd0f98e4a485bc1fd903e5350581cc70aa804cfb4a639518f0f1c8ba88626a  one full-resolution frame
d5215e655d0a09ec5d91c942b1a7bc7baa6a3149760a48b7c9a0411224a1273c  reopened preview frame
```

The first direct invocation failed closed before capture because `b5/a2`
returned positive length 1 where the reference predicts a stalled data stage.
A bounded pass of only the seven known controls and all later reader processes
received the expected stall for every step. This one self-clearing cold-attach
transient is preserved as a reliability observation rather than hidden by
accepting arbitrary short responses or adding a broad retry. The sensor was
covered, so this validates direct transport in both modes rather than optics.

## Bounded recovery after relay handoff

After macOS released the camera, the first direct Pi invocation received a
complete 1,229,312-byte device frame with the first marker absent and later
markers aligned; it failed closed. A second invocation immediately succeeded.
Candidate source then added a two-frame maximum initial resynchronization
window. Repeating the macOS capture and hand-back reproduced the invalid first
warm-up frame, but the same Pi process logged exactly one discard, delivered
three valid frames, and exited zero. The preserved first raw file remained
exactly one device frame rather than being appended:

```text
initial frame marker validation failed; discarding bounded warm-up frame 1/2
frames=3 status=ok
f76c7f61495388b20fc2ea6e04d61dae60a80c8aef0b074d88ef735cc2a8f827  1,229,312-byte first device frame
bf525b75678133fffeb77a96ba084349787304df68d8e6a0eb208162c2fc5887  3,686,400-byte three-frame Bayer stream
```

The bounded discard applies only before frame zero. Marker loss after delivery
begins still terminates the reader, so recovery cannot conceal stream damage.

Because the sensor was covered, the repaired mode-0 pixels provide a useful
dark-frame sanity check rather than an optical validation: median 12, mean
11.893, and 99th percentile 13 on an 8-bit scale.

## Evidence durability fix

During the endurance run the first raw file showed that libc could retain its
final 512 bytes in userspace buffering until process exit. Stream delivery was
unaffected, but an interrupted test could lose that packet from the evidence
file. Commit `c1ac14714c1ea91291c3800777114022f3f06d29` flushes the untouched
first device frame immediately and checks the partial-evidence write path.
Ubuntu and macOS CI both pass that change; a live interruption-observation test
on the Pi found the complete 1,229,312-byte raw file while the 100-frame reader
process was still active. That run subsequently completed 100/100 frames and
exited zero. Its first-frame hash is
`b72ce36fe4dfccb2fa82f37de6a376a4bb072e59763be650051e300705a9fb54`.

## Optical correction: one request is one complete physical record

With the camera mounted on its microscope, the old reader produced repeated
scene regions, a sharp horizontal seam, and an apparently black lower region.
The 1,228,800-byte output had 0.983 autocorrelation at an exact 524,288-byte
lag. A diagnostic probe then requested the entire record with one libusb bulk
call instead of several 524,288-byte calls.

The probe established the first corrected record behavior:

- mode 2: 1,229,312-byte record, 512-byte prefix, then 1,228,800 Bayer bytes;
- mode 0: 10,068,992-byte physical records, with frame bytes crossing the
  record boundary as refined below;
- the first ten prefix bytes are `0x88`; and
- neither record contains another transport marker.

Every separate bulk request begins at a new record origin. The marker runs
previously reported at 524,288-byte intervals were therefore the starts of
new records that had been concatenated, not internal boundaries in one frame.
Earlier endurance and byte-count results still establish repeated USB delivery,
but their reconstructed Bayer images are not spatially valid.

Candidate alpha.4 source using one request per record then completed eight
consecutive mode-2 frames and one mode-0 frame over a direct Apple Silicon
connection. Both produced microscope imagery without the former horizontal
seam or repeated quadrants. The alpha.4 mode-0 interpretation still placed a
192-pixel continuation from the preceding frame at the left edge.

```text
60d7ca28b68045a5e1fede848d5d78348b18bf3fca021e7b5d2590fbc0095028  eight mode-2 Bayer frames
d18ca2e26417c6bc5b47eb0cd04f0e8a3006a2a571cd45720c67507fee8a873f  one mode-0 Bayer frame
a8c62e7f782500c748f47d502539d78bbc237923460ebd2fd3632c1767feabec  eight-frame 640x480 H.264 proof clip
```

The eight Bayer frames were also rendered as 1280×960, 800×600, and 640×480
stills. The proof clip contains eight frames with a chosen 4 fps playback time
base; because raw Bayer carries no timestamps, that value is not a measured
camera frame-rate specification. A known color target is still required before
the provisional `bayer_grbg8` phase can be declared final.

## Full-resolution record-boundary assembly

A diagnostic mode-0 request of 10,069,504 bytes exposed a second ten-byte
`0x88` marker at byte 10,068,992. This proves that 10,068,992 is the physical
record interval. The same request showed that the visually clean raster begins
at offset 512, while only 10,068,480 bytes remain in that record. The missing
192 pixels are bytes 320–511 of the following record; bytes 512 onward in that
following record begin the next frame.

The reader now assembles each 3664×2748 frame as:

```text
record N   [512, 10068992)  = 10,068,480 bytes
record N+1 [320, 512)       =        192 bytes
total                         10,068,672 bytes
```

It retains record N+1 as the head of the following frame. A direct native-cable
test captured three consecutive assembled mode-0 frames and a separate
three-frame mode-2 regression sequence at 100 ms and gain 256. All six frame
hashes were distinct, both commands exited zero, and the full-resolution PNG
has no left strip:

```text
9ba66e3839516d540500790924f35f671abd0fe6455a7329e786e5115d5ede8d  mode-0 frame 1
58fca6aa409e785d297851ace0f045af9224219f0695d254ca52640802bab58e  mode-0 frame 2
88d31e27174d56e6b33d7423c42bcfd1a018d587190f6cbcb8df745ea748e8fc  mode-0 frame 3
ee419b1405d4c84e308ff701482822fe208d9155decc90d02f71c627f815baab  mode-2 frame 1
87c8de3d100797a6d8dee7f3709ec982627c965240d9bf50ed06cea283028785  mode-2 frame 2
77b25eecdf3d051b50677236f9737e9f8c60b4735ec353e5a08088000640c26f  mode-2 frame 3
```

## Neutral-background white balance

The blank illuminated slide was treated as neutral. Robust Bayer-plane medians
from clean regions independently produced red/green/blue multipliers of
`0.8788/1.0/1.9773` at 3664×2748 and `0.8624/1.0/2.0` at 1280×960. Applying
those gains removed the tungsten/sensor yellow-green cast and made the chosen
background neutral gray. This validates the `tca-white-balance` estimator and
the use of the actual optical path as an in-situ reference; it does not replace
a known color target for final Bayer-phase and colorimetric calibration.

## Optical exposure/gain response and brighter motion sequence

The first record delivered after a control write retained the preceding
settings. In paired six-frame captures, frame zero had mean 34.75 for both
gain 0 and gain 320, while frames one through five stabilized near 14.67 and
154.76 respectively at 100 ms. The reader now consumes exactly that one stale
record before publishing frame zero and preserves it as `--raw-first`.

After this correction, single-frame captures at 100 ms produced a monotonic
gain response:

| Gain | Mean | Median | p99 | Saturated fraction |
|---:|---:|---:|---:|---:|
| 0 | 14.67 | 15 | 17 | 0 |
| 64 | 19.27 | 20 | 25 | 0 |
| 128 | 28.28 | 30 | 39 | 0 |
| 160 | 37.44 | 40 | 53 | 0.0000008 |
| 192 | 46.47 | 50 | 67 | 0.0000024 |
| 224 | 64.77 | 70 | 96 | 0.0000041 |
| 256 | 83.23 | 91 | 125 | 0.0000049 |
| 320 | 154.88 | 169 | 237 | 0.0014640 |

A subsequent 100-ms/gain-256 run captured 16 distinct coherent frames; all 16
had unique SHA-256 hashes. Capture, including cold initialization and the one
settling record, completed in 2.03 seconds. The frames were encoded as a
640×480 H.264 proof clip with a chosen 6 fps playback time base:

```text
15811e333e8fe0a4656d3f22b460402ce9bb4a12b3818cf6dfe1201be4d3e3f3  16-frame Bayer stream
73c11d81e151b8da6004bd0057cdd09c791d22df360e03f71972bf6abec7bb31  640x480 H.264 proof clip
919a0b98e1b8fca71e65741e1b007e68dd1dd33d2a18ff82f5e947f785e53f4e  1280x960 PNG still
```

The first corrected frame had mean 83.30, median 91, p99 125, eight saturated
pixels out of 1,228,800, and no zero pixels. This setting is a useful starting
point for the present microscope, not a calibrated default for other lighting.

## Physical-size flat-field pipeline diagnostic

With the camera still mounted on the microscope and directly connected to the
Apple Silicon workstation, the public reader captured 24 exact preview frames
at 250-ms exposure and gain 0: 29,491,200 Bayer bytes, with
`frames=24 status=ok`. The first 16 frames were intentionally used as a
self-flat and the final eight as inputs. A separate 16-frame run at 1-ms/gain
0, with illumination still on, served only as a low-exposure proxy for a dark.
It had mean 10.684 and is explicitly not a blocked-light dark reference.

Applying the full-size map corrected all eight frames. In the first frame, the
ratio between the brightest and darkest equal-area cells of a 3x3 intensity
grid fell from 1.336910 to 1.001023. The near-uniform result is the expected
failure mode of a self-flat: it divides away the specimen scene together with
the illumination envelope. The run therefore validates exact physical frame
plumbing and per-pixel correction, not optical calibration. A valid map still
requires same-settings blocked-light darks and translated or defocused blank
fields, followed by validation against a fresh blank and a real specimen.

Selected retained hashes are:

```text
3717fdb97304b7de23370bd33033689986bbdbaeeaad3ab481b79672a4237f03  first untouched device record
22226d313db179cb8a5fdd0353a6a028fd8e345a2204b9b259ce01435d285e96  24 physical Bayer frames
b88eb92558bbda82e1ab8481db0413212a99bd694bd3f1e57aff118447dcee63  diagnostic proxy-dark calibration
2bfafe86a522607882ff108f7a5c7b2353082cd0579afd2927903ea7eb2665d8  eight corrected physical frames
```

## Guided physical calibration harness

`tools/run_flat_field_capture_session.sh` now turns the remaining hands-on
calibration into one fail-closed session. Without its exact execution token it
returns zero after stating that no USB transfer or file/system change was made.
Before live capture it validates all ranges and dependencies and refuses an
existing output directory. The explicit path then locks one preview-mode
exposure, gain, and Bayer phase while prompting in order for:

1. physically blocked illumination;
2. multiple translated or defocused flat-field batches;
3. a fresh blank that was not held stationary during calibration; and
4. a real specimen.

It checks every raw and Bayer byte count, creates and inspects a settings-bound
map, corrects the fresh blank and specimen, records statistics, renders four
PNGs, and hashes every completed artifact. Any interrupted or failed session is
marked `SESSION-INCOMPLETE.txt`. A USB-free dynamic test substitutes a fake
camera while exercising the real flat-field builder and frame analyzer; it
checks exact sizes, settings metadata, corrected pixel values, PNG production,
manifest integrity, inert behavior, and pre-output validation. The full native
suite passes on Apple Silicon; physical dark/flat execution remains the next
operator-assisted gate.

## Measured delivered-frame cadence

The alpha-7 reader can write a `frame,monotonic_ns` CSV row after each complete
Bayer frame has been accepted by the output stream. `tca-timing-stats` validates
the header, consecutive frame numbers, and strictly increasing timestamps, then
reports interval and delivered-frame-rate statistics. This measures the reader
and selected output path; it is not a sensor exposure-time measurement or an
FFmpeg playback time base.

Three direct Apple Silicon runs against the physical microscope camera used
the final alpha-7 implementation. Every command exited zero, every sidecar had
exactly one row per frame, byte counts were exact, and all frames within each
run had distinct SHA-256 hashes:

| Mode and requested controls | Frames | Measured span | Delivered fps | Interval p50 / p95 / max |
|---|---:|---:|---:|---:|
| 1280×960, 1 ms, gain 0 | 60 | 3.401246 s | 17.3466 | 55.782 / 68.478 / 101.744 ms |
| 1280×960, 250 ms, gain 0 | 30 | 3.050803 s | 9.5057 | 105.179 / 105.799 / 105.973 ms |
| 3664×2748, 250 ms, gain 0 | 12 | 3.941140 s | 2.7911 | 357.589 / 363.621 / 363.621 ms |

The control labels remain the nominal values derived from the recovered row-
time mapping. The timing result does not independently prove the true sensor
integration time, and the 1-ms preview run includes a small number of longer
intervals. It does establish realistic application-facing cadence for both
recovered modes without inventing timestamps inside the headerless Bayer data.

## Post-V4L2-merge Apple Silicon optical regression

The exact public commit `72964bb608102fa82232a8de966189219ec4309c` was
rebuilt and physically exercised after the full-resolution V4L2 change was
merged. At 250 ms and gain 0, three 1280x960 frames arrived at 9.51334 fps and
two complete 3664x2748 frames arrived at 2.75318 fps. Every command exited
zero, every byte count and timestamp-row count was exact, all five frame hashes
were distinct, and neither first frame contained zero or saturated pixels.

Lossless provisional-GRBG renders showed the same coherent dust field in both
modes. Full resolution covered the entire sensor raster, visibly carried more
scene detail, and had neither a half-frame black boundary nor an edge strip.
Public display derivatives, hashes, detailed statistics, and the bounded scope
of the result are in the [rendered evidence
record](../site/evidence/current-main-macos-optical-regression.html).

The build also exposed an independent host configuration problem: the default
`/usr/local/bin/pkg-config` selected Intel-only libusb on an ARM64 host. The
Makefile now accepts a scoped `LIBUSB_PKG_CONFIG_PATH` override and tests its
use, while the README documents the dual-Homebrew recovery path. Physical
Linux V4L2 application acceptance remains open and requires moving the cable.

## Uncorrected physical Linux acceptance preparation

Candidate commit `5670678` removes an unnecessary dependency between two
separate gates. The live Linux V4L2 harness now accepts `-` instead of a map to
run an explicitly uncorrected USB-to-application test, while a supplied map
retains the existing strict geometry, Bayer-phase, exposure, and gain checks.
Both paths record `calibration_mode`, producer and consumer timing, bounded
YUYV output, a mode/settings-derived consumer deadline and exit status, frame
digests, cleanup, immediate reader reopen, and a manifest.
An uncorrected pass cannot satisfy optical flat-field acceptance.

Follow-up candidate `5b297b5` adds the missing wall-clock bound around the
ordinary FFmpeg consumer. The deadline is derived from requested exposure and
frame count with a generous fixed and per-frame margin; the v4 evidence record
stores both the deadline and consumer exit status. A stalled consumer is
terminated, the bridge cleanup trap runs, and partial evidence is hashed.

The exact candidate passed the complete Apple Silicon and Raspberry Pi AArch64
suites. On the Pi, installing the standard Debian `time` package closed a
previously latent consumer-timing dependency. A token-gated invocation with
the uncorrected `-` argument then advanced through dependency checks and failed
closed on the expected zero-camera condition with status 69. The count of
acceptance evidence directories remained zero before and after, so no bridge,
loopback device, or partial evidence session was created. See the [rendered
preparation record](../site/evidence/linux-v4l2-uncorrected-acceptance-preparation.html).
