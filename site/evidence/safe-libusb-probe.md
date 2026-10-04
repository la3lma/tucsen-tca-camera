# Descriptor-only libusb probe

Captured 2026-09-27 on `rpios-17`, a Raspberry Pi 5 running 64-bit Debian 13.

## Safety boundary

The source is `tools/usb_descriptor_probe.c`, SHA-256
`c3556b79131ed411c33e8c651212ae1a2334ed379e9815a67174a523546ca8c3`.
The program contains no USB control, bulk, interrupt, asynchronous, reset, or
configuration-changing transfer call. Its dynamically imported libusb symbols
were inspected on the Pi and consist only of initialization, enumeration,
descriptor access, open/close, and interface claim/release functions.

No vendor-specific request and no endpoint data transfer was sent.

## Build

The Pi already had the libusb 1.0.28 runtime but not its development headers.
The matching upstream header was preserved inside the report project at
`work/deps/libusb-1.0.28/libusb.h`, SHA-256
`05f07e806e561b794d170590872789e420cebe481a21a3739e39c55684276e8e`.
It was retrieved from the tagged libusb source:

- https://raw.githubusercontent.com/libusb/libusb/v1.0.28/libusb/libusb.h

The source and header were copied to
`/home/rmz/microscope-window-sensor-probe/` on the Pi and compiled natively for
AArch64 against the installed `/lib/aarch64-linux-gnu/libusb-1.0.so.0`. The
resulting ELF binary had SHA-256
`1de715c1dc1bffef58c27353ae537b8bdaf3de2c827287b691b6bfa9cdb14c64`.

## Narrow device permission

The first run enumerated the descriptors but `libusb_open()` returned
`LIBUSB_ERROR_ACCESS`. The owner then installed the project rule
`tools/70-amscope-tucsen-0547-c003.rules`, which applies only to USB device
`0547:c003` and grants the `plugdev` group read/write access. The camera's
usbfs node became:

```text
/dev/bus/usb/001/002
mode=crw-rw---- numeric=660 owner=root group=plugdev
```

## Successful run

The probe was run with `--claim` and reported:

```text
Safety mode: standard USB descriptors only; no vendor-specific requests and no data transfers.
device 0547:c003 at bus 1 address 2
  USB release    2.00
  device release 0.00
  class          0x00 / 0x00 / 0x00
  speed          high (480 Mbit/s)
  configurations 1
configuration 1: total_length=25 interfaces=1 attributes=0x80 max_power=100 mA
  interface 0 alt 0: class=0xff subclass=0x00 protocol=0x00 endpoints=1
    endpoint 0x82: IN bulk max_packet=512 interval=0
open: success
  manufacturer   123456789
  product        10MP CMOS Camera
  serial         <absent>
claim interface 0: success
release interface 0: success
```

Exit status was zero. After release, `lsusb` still reported the camera and
sysfs still showed no kernel driver bound to interface `1-2:1.0`.

## Interpretation

Gate 1 is complete beyond passive enumeration: an unprivileged AArch64 libusb
program can open the device and exclusively claim and release its only
interface. This removes build, architecture, usbfs permission, and interface
ownership as blockers. The remaining blocker is the vendor protocol itself.
