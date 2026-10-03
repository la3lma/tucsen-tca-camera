# Physical validation record

This page records tests run against the original AmScope-branded
`0547:c003` camera. The sensor was covered, so these runs validate transport,
framing, controls, lifecycle, and application integration—not optical quality.

## Test bench

- Raspberry Pi 5, AArch64
- Linux 6.18.39+rpt-rpi-2712
- libusb 1.0.28
- GCC 14.2.0
- FFmpeg 7.1.3
- physical USB identity: `0547:c003 Anchor Chips, Inc. 10MP CMOS Camera`

The checkout's tracked worktree and index matched commit
`607d1dcd2b678583e181fffc3fc923adb86c81dd` during the mode-2 capture,
reopen, and endurance baselines below. Native `make test` passed first. Later
sections identify the hardening commit or candidate source used for their own
physical checks.

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
