# Project-local Linux VM bench

Prepared and first booted 2026-09-29. This is the primary development and
trace host while the camera remains physically connected to the macOS
workstation. The Raspberry Pi remains the independent deployment-validation
target.

## Reproducible image and configuration

The ARM64 Ubuntu 24.04 cloud image and every generated VM artifact are stored
under `work/linux-vm-bench/`; no download used a global downloads directory.

```text
1d6bffe64b848468ac97f821d369a4846d983de1800ccf6b5ec8853e85cefc55  noble-server-cloudimg-arm64.img
b61a6497608cdea66f54968d52d3457365b0645ccb2b1371c8f092ecce806183  SHA256SUMS
0b8d21a6c4a3f4a8eee6e3bc0589161d05481212b893857c7ef898eb68761395  Microscope Linux Bench.utm/config.plist
3bb9b4a218cf7627029f9004d19b7e2f9abb5f970ed43d4b4977a6387ea528db  cloud-init/user-data
70b9c304817dc856d5ab7978b9321d73d7eb5bd44e812c2137394d49b841281a  cloud-init/meta-data
1af04bf867c4cd2d1079743e04bb1cb62a5f9d4ff8350f4b89cee43db9df1871  Microscope Linux Bench.utm/Data/cloud-init.iso
```

The registered VM is `Microscope Linux Bench`, UUID
`6020A011-1F8B-485B-9493-066B54B034DC`: native ARM64/HVF, six vCPUs, 6 GiB
RAM, a sparse 32 GiB project-local QCOW2 disk, shared networking, USB 3
sharing, and MAC `52:54:00:4d:4c:42`. Cloud-init created key-only user `rmz`
with passwordless sudo and installed the build, libusb, USB/IP, usbmon, SSH,
and packet-capture tools.

## Boot and USB proof

The first boot completed with `cloud-init status: done`; SSH and
`qemu-guest-agent` are active. The guest obtained IPv4 `192.168.65.5` and
Ubuntu kernel `6.8.0-142-generic`. The lean cloud image omitted the USB/IP and
usbmon modules, so matching package
`linux-modules-extra-6.8.0-142-generic` was installed. The loaded modules are
`usbmon`, `usbip_core`, and `usbip_host`.

UTM attached the workstation-owned camera to the guest. Linux independently
reported:

```text
Bus 003 Device 002: ID 0547:c003 Anchor Chips, Inc. 10MP CMOS Camera
interface 0: vendor specific, one bulk-IN endpoint 0x82, 512-byte packets
```

The project source was copied without the large VM/vendor artifacts. All six
portable C core test programs passed natively on ARM64. The libusb descriptor
probe opened, claimed, released, and closed interface zero successfully.

## Executed USB/IP path and active fallback

`tools/pi_usbip_capture.sh` is host-neutral despite its historical name. On
this VM it resolved bus ID `3-3`, armed `dumpcap` on `usbmon3`, started
`usbipd` on TCP 3240, and exported only `0547:c003`. The Windows trace VM was
given an emulated Intel E1000 adapter and obtained `192.168.65.6`, placing both
guests on the same UTM shared network. Windows usbip-win2 attached directly to
server `192.168.65.5`, bus ID `3-3`; no host relay was required.

The stopped capture is preserved on the host under
`work/trace-captures/usbip-session-local-vm-20260929T1507Z`. It proved that
usbip-win2 received valid descriptors but failed on a repeated device-
descriptor read before configuration. The active replacement is a one-device
VirtualHere server on `192.168.65.5:7575`, with `usbmon3` recording to
`work/virtualhere-session-local-vm-20260929T140811Z` inside the guest. The
corresponding live capture is `/tmp/virtualhere-20260929T140811Z.pcapng` and
contained 14 preflight packets before client attachment. See the
[fallback evidence](virtualhere-trace-bench.md).
