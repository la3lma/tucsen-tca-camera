# VirtualHere fallback trace bench

Prepared 2026-09-29 after the Linux USB/IP to `usbip-win2` 0.9.8.0 path
failed during Windows enumeration.

## Why the fallback is justified

Windows successfully listed `0547:c003` and reported `successfully attached to
port 1`. Linux `usbmon3` captured 26 URBs. The Windows attach began at frame
15: it read the 18-byte device descriptor twice, the complete 25-byte
configuration descriptor, language ID `0409`, and the 36-byte product string
`10MP CMOS Camera`. It did not issue `SET_CONFIGURATION` or any vendor request.
Its next 18-byte device-descriptor request remained pending for 5.004272
seconds and completed as `-ECONNRESET`.

This establishes a transport/enumeration incompatibility before the Tucsen
driver or TSView protocol can run. It is consistent with open usbip-win2
reports in which a device works directly but the UDE client fails during
descriptor/endpoint setup:

- <https://github.com/vadimgrn/usbip-win2/issues/144>
- <https://github.com/vadimgrn/usbip-win2/issues/114>

The immutable capture is:

```text
ff33d5e7ab7ffbd9dcf1b0771ad5baba288c364dfea7497aa6daccd8f57ca11c  work/trace-captures/usbip-session-local-vm-20260929T1507Z/known-good-init.pcapng
```

The historical filename records the intended test, not its outcome; this is
an accepted negative USB/IP-enumeration trace, not a known-good initialization.

## Prepared alternative

VirtualHere keeps Linux `usbmon` below the forwarding transport but uses its
own userspace server and Windows virtual USB client. The vendor documents that
the generic server trial shares one device without a time limit. Version 4.8.8
of the generic ARM64 server and version 6.0.2 of the Windows x86-64 client were
downloaded into `work/virtualhere-bench/downloads`; both SHA-1 values match the
vendor checksum files:

```text
f000ef0aa8306d62a109a235e7830f7d9b52f214  vhusbdarm64
f90867a86c18b217543a2f8407a48333a7960623  vhui64.exe
```

Primary documentation:

- <https://www.virtualhere.com/usb_server_software>
- <https://www.virtualhere.com/usb_client_software>
- <https://www.virtualhere.com/configuration_faq>

The server at `192.168.65.5:7575` is running with `AllowedDevices=547/c003`,
`UseAVAHI=0`, `AutoAttachToKernel=0`, and `ClaimPorts=1`. Its log identifies
only the expected high-speed `0547:c003` product at address 33. `usbmon3` was
armed before server start in the verified active session
`work/virtualhere-session-local-vm-20260929T140811Z` inside the Linux guest.
Its live capture is `/tmp/virtualhere-20260929T140811Z.pcapng`; before any
Windows client use it contained 14 preflight packets and was still recording.

The project-local Windows client ISO is:

```text
d93df14f79c595842eb2e1f660ff21b10a8eca1d342b4a68093552db38a5b17a  work/virtualhere-bench/virtualhere-client.iso
```

## Reboot recovery and exact-device automation

After the macOS reboot on 2026-10-03, the iSCSI volume was present but UTM's
library no longer contained the two externally stored VM bundles.  Opening the
bundles in place re-registered and started them without copying their disks.
The shared network was recreated as `192.168.64.0/24`: the Linux bench is
`192.168.64.4` (MAC `52:54:00:4d:4c:42`) and the Windows trace VM is
`192.168.64.5` (MAC `52:54:00:54:43:41`).  The SSH key was reloaded from the
macOS keychain; Linux SSH and `usbmon1` through `usbmon4` were verified.

The original ISO was retained as
`Microscope TCA Trace.utm/Data/virtualhere-client-v1.iso`.  The VM's active
`virtualhere-client.iso` is now byte-identical to the v3 project image:

```text
55c301dd0e9a8fcf17c77898d3928930f4c87b829db875c2a31993771a237901  work/virtualhere-bench/virtualhere-client-v3.iso
950caf1dd32bd2bd3415b7d9f49c4cf57e6dcd33747efbf29bfed1297aeba587  work/virtualhere-bench/iso-root/DISCONNECT-CAMERA.cmd
```

Those scripts parse the one `10MP CMOS Camera` line returned by the official
client API, strip the surrounding parentheses, and issue `USE` or `STOP USING`
only for that exact address.  The pre-reboot listing established the address
as `microscope-linux.33`; the scripts do not hard-code it.

After moving the physical host to the Pi, v4 media removed the last stale
server address from the source script.  `CONNECT-CAMERA.cmd` now accepts an
optional `server:port` argument and defaults to the UTM host gateway relay at
`192.168.64.1:7575`; its exact-device parsing and `USE` behavior are unchanged.
The ISO was rebuilt and its embedded script and README were verified directly
with `bsdtar`:

```text
29311e3b6c1f5c2e82c7905879e516e071405a66f82afba5030b84bdfa56450f  work/virtualhere-bench/virtualhere-client-v4.iso
edaafb7a268eca14284120f9974b1de36dcb134b2e6f292ae26c53a7496cf59c  work/virtualhere-bench/iso-root/CONNECT-CAMERA.cmd
a2782b9d5732f76cb074c7009dc8a6d50688b1362c7711b6c14674f05e838702  work/virtualhere-bench/iso-root/README.txt
```

The camera remained visible to macOS as exactly one `0547:c003`, but UTM's
first post-reboot redirection attempt reported `disconnected (fatal IO
error)`.  `ioreg` showed the device active, configured, and `busy 0`.
`tools/usb_reset_exact.c` was therefore added as a narrowly token-gated
recovery operation.  Its source and unresolved binary imports are statically
audited: the live path contains one `libusb_reset_device` call and no control,
bulk, interrupt, configuration, alternate-setting, or firmware operation.
Both the inert run and the explicit reset succeeded against one match.  A
subsequent UTM attachment and Windows trace remain pending; this section is
recovery evidence, not a successful initialization claim.

The pinned server and configuration were also restored to the Linux guest and
verified against the project copies before any new capture was armed:

```text
09deced5586ed37b8b3db7a6187d84029f65d487c3c2b24a949b993b3d582077  vhusbdarm64
2417600d331a9c582562d7f0fd974f85a8449ca50250a28c6b56479cc997e481  config.ini
```

`tools/virtualhere_capture.sh` now makes the Linux side reproducible and
fail-closed.  It requires one exact sysfs match and the token
`--record-exact-virtualhere-init`, verifies both hashes above and every
exact-only configuration line, refuses a second server, and starts `dumpcap`
on the physical camera bus before starting VirtualHere.  Stop uses only the
recorded process IDs and writes a session manifest.  Its shell/static audit is
part of `make test-core` and passes.  Deployment to the restored ARM64 guest
also reached the expected pre-attachment refusal:

```text
expected exactly one 0547:c003 device; found 0
```

That result proves the staged guest harness sees no unintended match while UTM
has not attached the camera; it is not a device failure.

Run only the portable client, add the live Linux-bench address (`192.168.64.4`
after the 2026-10-03 reboot), select only `10MP CMOS Camera`, and start TSView
once. Do not change controls or invoke any firmware operation. A successful
run must contain configuration, the first vendor response, and mode-4 bulk
data, then pass the usual descriptor and claim/release post-check.

## Direct-QEMU result and Raspberry Pi handoff

Repeated post-reboot CocoaSPICE attachment attempts failed with the same fatal
I/O disconnect after a physical reconnect, an exact-device libusb reset, a
Linux-guest restart, and a full UTM/application restart.  A second UTM path was
then tested using QEMU's bundled libusb `usb-host` backend instead of the USB
menu.  UTM's scripting API stored these two arguments on the stopped Linux VM:

```text
-device
usb-host,bus=usb-controller-0.0,vendorid=0x0547,productid=0xc003
```

The launched QEMU command line contained the exact argument, but Linux exposed
no `0547:c003` device while macOS continued to enumerate the camera normally.
The custom arguments were removed again before the VM was left stopped.  This
closes both UTM-hosted attachment branches for the present macOS/UTM build; it
does not implicate the camera or the Linux reader.

The physical trace host has therefore moved to `rpios-17`, a Raspberry Pi 5 on
wired link-local IPv6 `fe80::9afe:54ff:fe1d:dcff%en0`.  Key-only SSH and
passwordless sudo were verified.  Debian's `tshark`, `wireshark-common`,
`libusb-1.0-0-dev`, `pkg-config`, and `usbutils` are installed, `usbmon` is
loaded, and root `dumpcap -D` lists `usbmon0` through `usbmon4`.  The exact
server, configuration, and capture harness were copied to
`/home/rmz/microscope-window-sensor` and re-hashed on the Pi:

```text
08c698427d805a03a38327df888542be0b9c3d898b8a9f3a16693608e7951675  tools/virtualhere_capture.sh
2417600d331a9c582562d7f0fd974f85a8449ca50250a28c6b56479cc997e481  work/virtualhere-bench/config.ini
09deced5586ed37b8b3db7a6187d84029f65d487c3c2b24a949b993b3d582077  work/virtualhere-bench/downloads/vhusbdarm64
```

Current ARM64 warm-reader, warm-control, exact-reset, and inert bulk-reader
binaries were built in the Ubuntu ARM64 bench, copied through the project-local
`work/pi-stage` directory, and verified byte-for-byte on the Pi.  The camera is
not yet attached there, so no capture or vendor transaction has been started.
