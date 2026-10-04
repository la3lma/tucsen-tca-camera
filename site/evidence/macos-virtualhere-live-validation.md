# Apple Silicon physical capture through the Pi relay

Date: 2026-10-03

## Purpose

Exercise the public userspace reader against the physical `0547:c003` camera
from Apple Silicon macOS without moving the USB cable from the Raspberry Pi,
then return ownership to Linux and verify recovery.

This is a physical macOS libusb test. It is not a native-cable test and does
not create an AVFoundation camera surface.

## Relay setup

- Raspberry Pi: `rpios-17`, camera directly attached as `0547:c003`
- VirtualHere generic ARM64 server: 4.8.8
- macOS client: 6.0.3, universal Intel/Apple Silicon build
- client SHA-1: `ae55db339fa0cd54edcc1de25f879d89292f6973`, matching the
  vendor's published `SHA1SUM`
- client SHA-256:
  `edfbba188187711a3707929aefff68a9b0c260224f28831d1103aa4c325aa437`
- client location:
  `work/virtualhere-bench/downloads/macos-client-6.0.3/`
- transport: IPv6 SSH local forward from macOS loopback port 7575 to the Pi's
  loopback port 7575

The default port matters for the unlicensed one-device server. A first
diagnostic tunnel on port 7576 enumerated the hub but the client correctly
reported that non-default-port use required a license. Moving the temporary
tunnel to the documented default port enabled the one-device trial without a
purchase or license bypass.

Official product and API references:

- <https://www.virtualhere.com/usb_client_software>
- <https://www.virtualhere.com/usb_server_software>
- <https://www.virtualhere.com/client_api>

The downloaded app was a notarized universal Mach-O signed by `VirtualHere
Pty. Ltd. (N8C8ZTN347)`. It was run from the read-only disk image with a
project-local configuration and log. No background service was installed.

## macOS enumeration and capture

VirtualHere listed one device:

```text
Raspberry Hub (rpios-17:7575)
   --> 10MP CMOS Camera  (rpios-17.32) (In-use by you)
```

macOS registered it under `AppleUSBUserHCI` at 480,000,000 bit/s with
`idVendor=1351` (`0x0547`), `idProduct=49155` (`0xc003`), and product string
`10MP CMOS Camera`.

Public commit `c5fa44ca59256ba5f423e616a7b37f3e91fb5d02` built and passed its
tests on Apple Silicon. Its reader cold-initialized the physical camera,
applied normalized gain 20 and 100-ms exposure, captured three mode-2 frames,
and exited zero with `frames=3 status=ok`:

```text
1c0256f291ef24c0fef702b2c56d6e8b514d9c1c0e8c5687898281d2dd80b5e2  1,229,312-byte first device frame
7fb92d416b0e7718299fa4ea59ed85948bc7274de85d03ebb5e6382603a2bc29  3,686,400-byte Bayer stream
```

Evidence is in `work/macos-virtualhere-capture-20261003T1955Z/`.

## Linux hand-back and bounded recovery

The client released the camera cleanly and macOS removed its
`IOUSBHostDevice`. The first direct Pi reader invocation then received one
complete-size frame whose marker at offset zero was absent while the markers
at offsets 524,288 and 1,048,576 remained aligned. It failed closed with
`frames=0 status=error`. A second process immediately captured three frames.

That observation motivated a narrow recovery rule: before delivery of frame
zero only, preserve the first raw device frame, discard at most two
marker-invalid warm-up frames, and then either deliver a fully validated frame
or fail. Never retry marker loss after delivery has begun.

Repeating macOS ownership, one-frame capture, release, and direct Pi capture
reproduced the first invalid warm-up frame. Candidate source, subsequently
published as commit `6fa708f08edc34f826076a6a5802c01eccec0bbb`, recovered in the
same process:

```text
initial frame marker validation failed; discarding bounded warm-up frame 1/2
frames=3 status=ok
f76c7f61495388b20fc2ea6e04d61dae60a80c8aef0b074d88ef735cc2a8f827  1,229,312-byte preserved first device frame
bf525b75678133fffeb77a96ba084349787304df68d8e6a0eb208162c2fc5887  3,686,400-byte Bayer stream
```

The first raw evidence file remained exactly one device frame; the discarded
warm-up frame was not appended or silently repaired. The final alpha-2 source
rebuilt and passed `make test` on both the workstation and Pi. The relay client,
SSH tunnel, server, and disk-image mount were then stopped; the camera remained
enumerated directly on the Pi.

After GitHub CI passed and tag `v0.2.0-alpha.2` was pushed, a fresh detached Pi
worktree checked out exact commit
`6fa708f08edc34f826076a6a5802c01eccec0bbb`, rebuilt, passed `make test`, and
cold-captured three more direct mode-2 frames with exit zero:

```text
22968a3acce34a6fd2d003e8d7d501ccedfdf7b9b1e24c0ce682bc6efd18085d  1,229,312-byte first device frame
546e5c74a3f243abbcb6c1b9e2356f733f0fcae0919407f98a31fc49fb9ed40c  3,686,400-byte Bayer stream
```

That bundle is retained at
`work/public-release-validation-20261003/tagged-live-20261003T2005Z/`.

## Result

- Physical Apple Silicon libusb reader path: **PASS through Pi relay**
- Bounded macOS-to-Linux ownership hand-back: **PASS after one explicit warm-up discard**
- Exact public `v0.2.0-alpha.2` Pi rebuild/test/capture: **PASS**
- Native-cable macOS run: **not tested**
- AVFoundation/Camera Extension surface: **deferred, non-blocking for Linux-first alpha**
