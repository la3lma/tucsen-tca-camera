# USB-inert exact-device enumeration preflight

Date: 2026-10-04

Issue [#35](https://github.com/la3lma/tucsen-tca-camera/issues/35)
tracks a safe first diagnostic for every cable move. Candidate commit
`109d4d1854dd6b597a521f02964de070362991a5` adds
`tca-camera list`, which enumerates only the exact supported USB identity
`0547:c003` and reports its bus, address, and negotiated USB speed.

## Safety boundary

The command initializes libusb, obtains the device list, and reads cached
device descriptors. Its command branch returns before the capture path and
never calls the program's device-open, interface-claim, control-transfer, or
bulk-transfer functions. It ends with an explicit
`NO DEVICE OPENED OR TRANSFER SUBMITTED.` status. Zero matches are a successful
enumeration result rather than a capture attempt or protocol failure.

The command deliberately does not read string descriptors, detach a driver,
reset a device, change a configuration, upload firmware, or select between
multiple cameras for capture.

## Apple Silicon exact-device result

The candidate passed the complete Apple Silicon suite with a scoped native
ARM64 libusb. With the camera connected directly to the workstation, the new
command returned:

```text
target=0547:c003
camera=0 bus=8 address=24 speed=high
camera-count=1
NO DEVICE OPENED OR TRANSFER SUBMITTED.
```

This proves that the preflight recognizes the physical unit without taking
ownership from another application. Bus and address identify this attachment
instance only and are not stable camera serial numbers.

## Raspberry Pi AArch64 result

A fresh shallow checkout of the exact candidate on `rpios-17` built and passed
the complete suite, including the Linux-only reproducible Debian-package test.
The extracted package reader executed both `--version` and `list`. With the
camera still attached to the Mac, the candidate Pi binary returned:

```text
tca-camera 0.2.0-alpha.12
target=0547:c003
camera-count=0
NO DEVICE OPENED OR TRANSFER SUBMITTED.
```

The zero result is the expected baseline before the cable move. When the
camera is moved to the Pi, changing that count from zero to one will prove
enumeration independently of permissions, initialization, frame transport,
V4L2 conversion, or optical calibration.

## Scope

This preflight narrows the first physical Linux diagnosis and makes absence
unambiguous. It does not close the direct-camera Linux V4L2 acceptance,
disconnect/reconnect, true dark/flat, known-target color, or owner-acceptance
gates.
