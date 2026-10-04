# Working Windows reference and direct host capture

Executed 2026-09-29 with the taped sensor, so a nearly black image was the
expected optical result.

## Reference-stack result

The isolated Windows 10 x86-64 guest ran in test-signing mode with the official
2011 Tucsen driver. Windows reported the physical instance
`USB\VID_0547&PID_C003` as `Started`. TSView7 7.3.1.8 opened its camera child
window and reached `Ready`, exposing resolution, snapshot, record, white
balance, exposure, crop, properties, and crosshair controls. This is a working
reference path, not merely successful device enumeration.

The installed binaries copied from that guest match the already analyzed TCA
evidence exactly:

```text
ee9c8ec6a680404c375a6bf0c44ded0486c6e7557cdee379a5f332eb9a8d12ac  TS1000.dll
01c8fdc3b34c0d13cf67c550968d7ae0236e633cb66154a67c04bd10e9326987  Tucsen64.sys
```

`TS1000.dll` opens `\\.\tca000-N`; the driver INF names `0547:c003` as
`Tucsen TCA-10.0-N Camera`. This removes the remaining ambiguity about which
of TSView7's many model DLLs and protocol generations belongs to this camera.

## USBPcap limitation

All eight USBPcap roots were armed before the reference run. Only root 8
contained packets: 525 USBPcap records over 142.878672 seconds. Its only
descriptor identities were three QEMU virtual HID devices, all `0627:0001`.
No `0547:c003` URB was present and the vendor-control extractor emitted no row.

This is explained by UTM's architecture. The camera travels through a
CocoaSPICE usbredir channel rather than a Windows emulated root hub, so the
Windows USBPcap filter never owns that traffic. The pcap is preserved as
negative instrumentation evidence:

```text
6d713d85f3a778c44dea03029ff229719f1ba1eb0f7b1c40f47d016f94c4e8e0  testmode-allroot8.pcap
```

The UTM debug log independently records `usbredir-9:2: connecting device
0547:c003` and large usbredir writes, including 1,048,602 and 180,762 bytes,
but logs lengths rather than payload bytes.

## Direct macOS bulk capture

After TSView reached `Ready`, the disposable VM was hard-stopped while idle.
That closed the usbredir channel without removing camera power. A read-only
libusb probe immediately claimed interface 0 and received a complete
81,920-byte bulk transfer from endpoint `0x82`. It began with ten `0x88` bytes,
the observed transport marker, followed by dark-frame samples concentrated
around values 10--12.

The project-local `tools/tca_stream_read.c` then held one libusb handle and
captured the exact reconstructed mode-4 geometry:

```text
read 0: requested 81920, received 81920
read 1: requested 81920, received 81920
read 2: requested 81920, received 81920
read 3: requested 61440, received 61440
total:  307200 bytes = 640 x 480 Bayer8
```

The ten-byte `0x88` marker occurs at offsets 0, 81,920, 163,840, and 245,760,
exactly one per scheduled block. The final raw-frame hash is:

```text
97ec45e81302f66e1f17e472b769f538c3bc33cb70b23cc726200b31647dd7df  mode4-final-short-request.raw
```

The exact read-only probe source and the x86-64 macOS binary used for the
verified schedule are pinned as:

```text
043a736b570dcbc95234dc241273a8424651c1042de8c690c3f24b2ff77e229e  tools/tca_stream_read.c
a557899c50b9bd9a8046f47767441a18049b85cc8b93749b7d85e98e60076e1d  work/tca_stream_read-macos
```

The fixed GRBG/BGR24 converter produced valid 640x480 grayscale and color
derivatives. The grayscale image is nearly black as predicted by the tape;
the four bright ten-pixel runs at the left edge are the unstripped block
markers. Raw samples have minimum 9, maximum 136, and mean approximately
11.06. The complete private evidence bundle and manifest are under
`work/live-host-capture-20260929T080041Z/`.

## What this proves and what remains

This is the first live non-Windows frame acquisition. It proves the endpoint,
four-block mode-4 geometry, exact byte count, marker placement, Bayer replay
path, and direct libusb readability. The data plane is no longer speculative.

It does **not** yet prove cold-start initialization from Linux or macOS. Direct
`0xc0/0x02` startup attempts still stall or return `PIPE` outside the Windows
driver path. The next protocol experiment should therefore route the camera
through a Linux USB/IP host to the working Windows guest while Linux `usbmon`
records the physical URBs. That route observes the successful initialization
without guessing another request and is independent of USBPcap's usbredir
blind spot.
