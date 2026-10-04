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
