# Raspberry Pi Linux enumeration

Captured 2026-09-27 from the Raspberry Pi test bench through a one-time SSH
connection over link-local IPv6. No vendor-specific USB request was sent.

## Test host

- Hostname: `rpios-17`
- Board: Raspberry Pi 5 Model B Rev 1.1
- Architecture: `aarch64`
- OS: Debian GNU/Linux 13 (trixie)
- Kernel: `6.18.39+rpt-rpi-2712`
- Ethernet: `eth0`, `10.0.0.90/24`, MAC `98:fe:54:1d:dc:ff`, link-local IPv6
  `fe80::9afe:54ff:fe1d:dcff/64`
- Wi-Fi: `wlan0`, `10.0.0.91/24`, MAC `98:fe:54:1d:dd:00`, link-local IPv6
  `fe80::9afe:54ff:fe1d:dd00/64`

The OUI `98-FE-54` is registered to Raspberry Pi (Trading) Ltd in the IEEE OUI
registry. IPv4 traffic to the Pi was filtered, while SSH was available on both
link-local IPv6 addresses.

The host presented ED25519 fingerprint
`SHA256:X9aMGsUKGhnI/v9AwCOIIh4KaX4duGlskDg2TtSSYFw`, which differed from the
historical `rpios-16.local` key. Both hardware interfaces presented the same
new fingerprint. The owner explicitly authorized a one-time connection without
changing the workstation's `known_hosts` file.

## Camera identity and topology

`lsusb` reported:

```text
Bus 001 Device 002: ID 0547:c003 Anchor Chips, Inc. 10MP CMOS Camera
```

`lsusb -t` reported:

```text
/:  Bus 001.Port 001: Dev 001, Class=root_hub, Driver=xhci-hcd/2p, 480M
    |__ Port 002: Dev 002, If 0, Class=Vendor Specific Class, Driver=[none], 480M
```

The standard USB descriptors agree with the macOS inventory:

- USB 2.0 high-speed, 480 Mbit/s
- Bus-powered, declared maximum power 100 mA
- Manufacturer string `123456789`
- Product string `10MP CMOS Camera`
- No serial-number string
- One configuration and one interface
- Interface class `0xff` (vendor-specific), subclass/protocol zero
- One non-control endpoint, bulk IN `0x82`
- Endpoint maximum packet size 512 bytes

The kernel log showed the camera enumerating cleanly on path `1-2` about 21
seconds after boot. There were no camera resets, disconnects, or driver errors
in the captured log.

## Driver and media-device state

Sysfs and udev reported:

```text
idVendor=0547
idProduct=c003
speed=480
power/control=on
power/runtime_status=active
interface_driver=none
ID_USB_INTERFACES=:ff0000:
DEVNAME=/dev/bus/usb/001/002
```

No driver was bound to interface `1-2:1.0`. The camera created no V4L2 node.
The existing `/dev/video19` through `/dev/video35` nodes were mapped by
`v4l2-ctl --list-devices` to the Raspberry Pi platform HEVC decoder and PISP
image-processing hardware, not to USB device `0547:c003`. The `uvcvideo` module
was not loaded; loading it would not match the camera's vendor-specific
interface in any case.

## Interpretation

The Linux result independently confirms that the camera hardware is alive,
enumerates reliably, and presents the same vendor-specific bulk-IN topology
seen on macOS. It also rules out accidental UVC/V4L2 support in the current
Raspberry Pi kernel. The next implementation step should be a user-space
libusb fixture, beginning with open/claim/release only and adding
vendor-specific control requests only after static analysis or a Windows USB
trace establishes their exact semantics.
