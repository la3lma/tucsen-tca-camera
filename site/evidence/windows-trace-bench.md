# Windows trace bench readiness

Prepared: 2026-09-27

The Linux D40 experiments reached a reproducible timeout boundary without
damaging enumeration. The final physical cold-power check also timed out on
open, the corrected register read, and close while both health checks passed.
A targeted Windows trace is therefore the active approved fallback.

## Verified host capabilities

- UTM 4.7.5 is installed on the Apple-silicon host.
- The application bundle contains both i386 and x86-64 QEMU emulation
  backends.
- `utmctl` exposes USB device listing plus attachment by VID/PID.
- Wireshark/TShark is installed on the host for offline extraction.
- With the camera attached directly to the Mac, IOKit reports `10MP CMOS
  Camera`, VID:PID `0547:c003`, USB address 11, and a 480 Mbit/s high-speed
  link. UTM offered to attach it automatically; that prompt was cancelled, so
  the device remains host-owned until capture is armed.

The exact bench procedure is preserved in
`work/windows-trace-bench/README.md`.

## Capture tooling

USBPcap 1.5.4.0 was downloaded from the upstream GitHub release into the
project. Its SHA-256 is:

```text
87a7edf9bbbcf07b5f4373d9a192a6770d2ff3add7aa1e276e82e38582ccb622
```

The value matches the independently published package checksum. The upstream
source checkout is pinned at commit
`477b6edcbd7e99a47f77afc0c4168a9ebee603bb` and confirms that USBPcap can
capture a selected root hub, restrict by device address, inject descriptors,
and preserve the full 65,535-byte snapshot length.

`tools/extract_usbpcap_control.sh` is a deterministic host-side extractor for
vendor control URBs. It emits timestamps, URB pairing identifiers, device and
endpoint identity, status, setup fields, lengths, and captured data.

The project-local guest-transfer image `work/windows-trace-bench/tca-trace-tools.iso`
contains USBPcap, the preserved TCA driver, TSView7, and a checksum/instruction
file. Its SHA-256 is:

```text
0f466cb9143fcfe30a4a11eab4e7372f3b6fa43602a33861174f0cc4760abea8
```

The sensor is physically covered for protection, so an acquired frame is
expected to be black. Frame transport, geometry, timing, and dark-frame byte
statistics are the acceptance signals; recognizable image content is not.

## Guest checkpoint

The official Windows 10 22H2 English x64 ISO was downloaded directly from
Microsoft into the project. Its measured SHA-256,
`a6f470ca6d331eb353b815c043e327a347f594f37ff525f17764738fe812852e`,
matches Microsoft's published value.

UTM guest `Microscope TCA Trace`
(`E480BE84-39B5-4F43-AFB0-63FE12D1DAC6`) is an isolated x86-64 Windows 10 Pro
bench with two emulated CPUs, 4 GiB RAM, a 64 GiB sparse disk, UEFI, TPM, USB
2.0 sharing, and no network adapter. The entire `.utm` package and QCOW2 disk
are on the iSCSI-backed project volume. Windows completed installation and its
first disk boot and offline OOBE. The local account is `Bjorn Remseth`; Norway
and a US keyboard were selected. Location, Find My Device, optional diagnostic
data, inking/typing telemetry, tailored experiences, and the advertising ID
were disabled or reduced to the minimum offered setting. The guest reached the
Windows desktop at 22:47 local time. The VM remains running and host sleep is
inhibited until UTM exits.

The Windows installer ISO was then replaced in the virtual IDE CD/DVD drive by
the project-local `tca-trace-tools.iso`. UTM's drive menu was reopened and
visibly confirmed `CD/DVD (ISO) Image (IDE): tca-trace-tools.iso`.

On 2026-09-28 the three reviewed packages were installed while the camera
remained host-owned:

- USBPcap 1.5.4.0, with the driver, USBPcapCMD, and USB 3 detection components.
  UAC identified verified publisher Tomasz Moń.
- TCA-10.0-N driver version 1.0. UAC and the Windows device-driver prompt both
  identified verified publisher Fuzhou Tucsen Image Technology Co., Ltd. The
  device-driver dialog's default `Always trust software from` checkbox remained
  selected.
- TSView7 7.3.1.8, installed as the full 32-bit application under
  `C:\Program Files (x86)\TSView7`. UAC identified verified publisher Fuzhou
  Xintu Photonics Co., Ltd.

Each installer reached its completion page without a signature exception.
Windows was then restarted normally to activate the capture and camera drivers.
The guest remains network-isolated, and `0547:c003` remains host-owned on
macOS.

## Remaining setup

The driver and vendor application now work in the isolated guest. The remaining
bench task is to arm USBPcap before a fresh redirection, exercise the TSView7
camera window and controls, stop capture cleanly, and preserve the resulting
trace in this project. Do not send another speculative Linux vendor request or
initiate any firmware action while that trace is pending.

## First passthrough and driver-binding result

On 2026-09-28 UTM debug logging was enabled and the camera was attached from
the VM's USB-device menu. The host log identifies physical device `8:14`,
`0547:c003`, attaches it to USB-redirection channel 2, and records bidirectional
descriptor traffic between CocoaSpice and the guest. Windows independently
confirmed the connected PnP instance:

```text
USB\VID_0547&PID_C003\5&1311452c&0&3
```

The matching-driver query selected the intended legacy package and reported:

```text
Device Description: Tucsen TCA-10.0-N Camera
Status:             Problem
Problem Code:       52 (0x34) [CM_PROB_UNSIGNED_DRIVER]
Problem Status:     0xc0000428
Driver Name:        oem2.inf
Original Name:      tucsen.inf
Driver Version:     04/13/2011 0.0.0.0
Matching Device ID: USB\VID_0547&PID_C003
Driver Status:      Best Ranked / Installed
```

Thus USB redirection and PnP matching work; Windows 10 x64 is refusing to load
the 2011 kernel driver under current code-integrity policy. The package's
`tucsenx64.cat` contains the historical Fuzhou Tucsen/VeriSign signing chain,
but that chain is not accepted by this Windows installation. USBPcapCMD's
interactive root listing did not display the redirected device even though
`pnputil` proved it connected, so that listing must not be treated as the
device-presence authority.

A direct QEMU `usb-host` argument was also tested. QEMU accepted the device
object syntactically, but it did not claim the macOS device or expose it to the
guest. The working path is UTM's CocoaSpice USB-redirection channel.

The owner approved enabling Windows test-signing mode. From an elevated
Command Prompt, `bcdedit /set testsigning on` was attempted and Windows
returned:

```text
An error has occurred setting the element data.
The value is protected by Secure Boot policy and cannot be modified or deleted.
```

No code-integrity setting changed in that first attempt.

## Test mode and working vendor stack

On 2026-09-29 the owner explicitly approved disabling Secure Boot in this
offline, disposable VM and continuing. The VM was stopped cleanly, UTM's TPM
device was disabled, and the failed direct-QEMU USB argument was removed. The
running QEMU command line was then verified to use
`edk2-x86_64-code.fd`, with no TPM or direct `usb-host` argument. Windows booted
normally with the same disk and account.

An elevated command prompt then accepted:

```text
bcdedit /set testsigning on
The operation completed successfully.
```

After a normal reboot, the desktop visibly displayed the Windows 10 Pro
`Test Mode` watermark. UTM's CocoaSpice USB-redirection path attached the
camera again. Windows reported the same PnP instance and, critically, the
legacy driver changed from Code 52 to a running state:

```text
Instance ID:         USB\VID_0547&PID_C003\5&1311452c&0&3
Device Description: Tucsen TCA-10.0-N Camera
Manufacturer Name:  @oem2.inf,%Tucsen%
Status:              Started
Driver Name:         oem2.inf
Original Name:       tucsen.inf
Driver Version:      04/13/2011 0.0.0.0
Matching Device ID:  USB\VID_0547&PID_C003
Driver Status:       Best Ranked / Installed
```

TSView7 7.3.1.8 then launched under its verified Fuzhou Xintu Photonics
signature. Its main window showed the `Video` device tile. Opening the camera
window reached `Ready` and exposed the expected controls: resolution, snapshot,
record, white balance, exposure, cut, properties, and crosshair. The image area
was blank, which is not an acquisition failure by itself because the sensor is
deliberately covered. This establishes that USB redirection, driver binding,
user-mode discovery, and the vendor application's camera-control path all work.

USBPcapCMD enumerates eight filter roots. Root 8 contains the VM's three
virtual input devices; roots 4, 5, 1, 6, 2, 7, and 3 were otherwise unlabeled.
As in the Code-52 trial, the redirected camera is not named in this listing, so
PnP remains the presence authority. The first targeted capture will therefore
cover roots 4 and 1, the two candidate virtual USB roots selected during bench
preparation. A project-local `tca-trace-tools-v4.iso` was created with
`start-capture-testmode.cmd`; it writes new `testmode-root4.pcap` and
`testmode-root1.pcap` files without overwriting the earlier header-only files.
The ISO has SHA-256:

```text
82f4283283c6ee8d453525da5dd5c2bf4f1e97587011c2437c4c99cf1340aa6e
```

Mounting that ISO and running the capture remained pending only because the Mac
auto-locked while the VM was running; no additional camera or security blocker
was encountered.

## Completed all-root capture and instrumentation result

After the workstation was unlocked, `tca-trace-tools-v5.iso` was mounted and
USBPcap roots 1 through 8 were armed simultaneously. TSView7 again reached its
camera window's `Ready` state with the device driver `Started`. All capture
processes were then stopped cleanly and the files were exported from the
offline NTFS volume.

Only root 8 contained traffic: 525 packets over 142.878672 seconds, SHA-256
`6d713d85f3a778c44dea03029ff229719f1ba1eb0f7b1c40f47d016f94c4e8e0`.
Its only enumerated devices were three QEMU virtual HIDs, all `0627:0001`.
There was no camera descriptor or vendor-control URB. This conclusively shows
that Windows USBPcap cannot see a CocoaSPICE usbredir device; another root
selection is not warranted.

UTM's host debug log did show `usbredir-9:2` connect `0547:c003` and recorded
large callback sizes during TSView activity. Because that log records lengths
rather than payload bytes, the next successful-control trace should use a
Linux USB/IP host plus `usbmon`, not another USBPcap run.

## Live host handoff result

The same working session produced a stronger data-plane result. With TSView at
`Ready`, the idle disposable VM was hard-stopped to close usbredir without
removing camera power. macOS immediately claimed interface 0 and read endpoint
`0x82` through libusb. Four sequential reads of 81,920, 81,920, 81,920, and
61,440 bytes yielded exactly 307,200 bytes, the recovered 640x480 mode-4 frame
size. Ten `0x88` marker bytes occur at the start of every block. The raw frame
hash is
`97ec45e81302f66e1f17e472b769f538c3bc33cb70b23cc726200b31647dd7df`.

The taped sensor produced the expected dark frame with samples concentrated
around 10--12. Offline GRBG conversion succeeded. Full details and artifact
hashes are in [Working Windows reference and direct host capture](windows-reference-live-capture.md).

## Linux USB/IP relay result

The E1000 path subsequently allowed `usbip-win2` 0.9.8.0 to list the Linux
export and report `0547:c003` attached to virtual port 1. The Windows side did
not reach the Tucsen function driver, however. Linux `usbmon3` captured valid
device, configuration, language, and product-string descriptors followed by a
repeated 18-byte device-descriptor read that timed out after 5.004272 seconds
and completed as `-ECONNRESET`. No `SET_CONFIGURATION`, vendor request, or
bulk transfer occurred.

This closes usbip-win2 as the trace transport for this camera without changing
the known-good direct Windows result above. The prepared replacement is the
one-device [VirtualHere fallback](virtualhere-trace-bench.md), still observed
below the relay by Linux `usbmon`.
