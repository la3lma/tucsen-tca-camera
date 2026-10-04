# Existing Linux driver candidates after protocol recovery

Search date: 2026-10-03

## New local evidence used to narrow the search

The candidate search was repeated after obtaining a complete, successful
Windows-reference trace and reproducing its useful subset on Raspberry Pi
Linux.  The search is no longer based only on the `0547:c003` identity:

- the device has one vendor-specific interface (`ff/00/00`), endpoint zero for
  commands, and one bulk-IN endpoint (`0x82`), so it is not a UVC device;
- the reference session contains 191 vendor-control operations and 528 bulk-IN
  operations, with no bulk-OUT traffic or pairing gaps;
- the recovered command families are `b3`, `b4`, `b5`, `b7`, and `bb`;
- the `b7` writes address sensor registers including coarse exposure at
  `0x3012` and gain at `0x305e`;
- the mode table contains a 3664-by-2748 Bayer8 mode, and the live Linux reader
  has captured a continuous 1280-by-960 Bayer8 stream; and
- exposure and gain writes have been transport-validated on the physical
  camera, and the resulting live stream has been consumed through a temporary
  V4L2 loopback device.

The register vocabulary and exact full-mode geometry strongly identify the
imager as MT9J001-compatible.  This is a high-confidence engineering
identification, not a visual chip-marking observation: the enclosure has not
been opened.

## Candidate results

### Linux `uvcvideo`

Not compatible.  The camera exposes a vendor-specific interface and neither a
VideoControl nor VideoStreaming interface.  It also has no isochronous
endpoint.  Adding the VID/PID to a UVC quirk table would not supply the missing
vendor initialization protocol.

### In-tree `gspca_touptek`

Source inspected at Linux commit
`25d576ed11108470d0999054265108400db1b881`:

<https://github.com/torvalds/linux/blob/25d576ed11108470d0999054265108400db1b881/drivers/media/usb/gspca/touptek.c>

The driver is for ToupTek UCMOS/AmScope MU cameras and is therefore the closest
in-tree relative.  It binds only `0547:6801`; `0547:c003` is absent.  Its bridge
protocol is also different: it uses request `0x16` for a key exchange and
request `0x0b` for sensor-register writes, with 16 KiB bulk chunks.  The C003
trace instead uses the `b3`/`b4`/`b5`/`b7`/`bb` family and different frame
chunking.  Binding C003 to this driver without a new protocol implementation
would therefore be unsafe and ineffective.

The source remains valuable prior art.  It demonstrates a working GSPCA/V4L2
shape for a related vendor family and uses the same Aptina/Micron register
vocabulary, including exposure register `0x3012`, Bayer gains at
`0x3056`--`0x305c`, PLL, crop, and output-size registers.  Those similarities
support the sensor-family inference but do not establish USB compatibility.

A bounded GitHub code search of `drivers/media/usb` at that commit found vendor
`0x0547` only in `gspca/touptek.c` and `gspca/dtcs033.c`; no USB ID table entry
claims product `0xc003`.

### Official ToupCam SDK and Python binding

The owner-supplied lead that many AmScope cameras are rebadged ToupTek units is
valid for part of the product line, but it does not establish that this unit is
an MU1000.  The exact device identity remains Tucsen TCA-10.0N/IS1000
`0547:c003`, as established by the official Tucsen matrix and the recovered
matching INF.  ToupTek's official download centre was therefore checked using
the product ID rather than the AmScope enclosure label.

Two official SDK packages were downloaded project-locally and inspected
without executing their native libraries:

| Package | SDK version | SHA-256 | Explicit Windows USB pairs | `0547:c003` |
|---|---:|---|---:|---|
| Current stable `toupcamsdk.20260519.zip` | `60.31488.20260519` | `3c2326923b8f1b908f210a1309d8f40e9bb80bc401a1a255aa468d954ff24433` | 1,768 | absent |
| Official legacy `toupcamsdk.20250120.zip` | `57.27567.20250120` | `c54f428abd0ecd213ffa2b0d387e64569781b457e2c311e61322b78b9e86b46e` | 1,600 | absent |

Both explicit INF tables include related ToupTek IDs such as `0547:6801`,
`0547:6010`, and `0547:c010`, which shows that the negative result is not a
failure to find vendor `0547`.  Neither package contains the strings `C003`,
`IS1000`, `TCA-10`, or `MU1000` in the inspected native Linux/macOS libraries.
The latter string search is supporting evidence only; the explicit INF device
tables are the stronger compatibility boundary.

The Linux udev file grants access to every USB device with vendor `0547` (and
`04b4`).  That vendor-wide permission rule is not a supported-device list and
must not be read as a claim that the SDK recognizes C003.  Similarly, the
shipped `toupcam.py` states that it is a thin `ctypes` wrapper around the
proprietary `toupcam.dll`, `libtoupcam.so`, or `libtoupcam.dylib`.  It contains
no independent Python USB transport to transplant into this project.

Consequently the current or official legacy ToupCam SDK is not a demonstrated
drop-in backend for this camera.  It is still useful inspiration at two safe
layers: its public C/Python API demonstrates a mature callback, frame-metadata,
ROI, exposure, and gain surface; and the related open Linux
`gspca_touptek` source demonstrates V4L2/GSPCA packaging and overlapping sensor
register vocabulary.  Neither source should replace the trace-proven C003
transport.  A substantially older SDK that explicitly lists `0547:c003` would
be a new candidate, but only its documented enumeration path should be tested
before any capture or control operation.

### Current Tucsen Linux SDK configuration

Tucsen's official download page advertises a Linux SDK, but access is gated by
the vendor site.  A current Linux SDK deployment preserved in the public Squid
project was inspected at commit
`e1ad4cc6378e69d3315438d6d8839a1e43d573b1`:

<https://github.com/Cephla-Lab/Squid/blob/e1ad4cc6378e69d3315438d6d8839a1e43d573b1/software/drivers%20and%20libraries/tucsen/sdk/tuusb.conf>

Its supported-device configuration contains modern `5453:*` devices and two
`0547:*` devices (`0547:a008` and `0547:e004`), but not `0547:c003`.  This does
not prove that every build of the proprietary SDK rejects the camera, but it is
direct evidence that this published current configuration does not claim the
legacy unit.  It is not a reason to run an unrelated proprietary library
against the device.

### Current Micro-Manager TUCam adapter

Source inspected at Micro-Manager commit
`e28c50d10c522c4f2329d3a6a9ac74cb7b7c190e`:

<https://github.com/micro-manager/mmCoreAndDevices/tree/e28c50d10c522c4f2329d3a6a9ac74cb7b7c190e/DeviceAdapters/TUCam>

This is an application adapter, not a USB driver.  Its project is Windows x64,
includes Windows-only headers, and links the proprietary `TUCam.lib` from the
2024 TUCam SDK.  It could become useful above a compatible vendor SDK, but it
does not offer an independent Linux transport and does not establish C003
support.

### Historical `uvscopetek`

The historical inventory explicitly lists the IS1000 10 MP `0547:c003` and
records that the author possessed one.  Its implemented driver nevertheless
targets `0547:4d88`, not C003.  The now-observed C003 command families also
confirm that the 4D88 requests must not be replayed against this camera.

Repository and inspected historical commit:

<https://github.com/JohnDMcMaster/uvscopetek/tree/db9681b64353c899fff74be28105e6ea19373b53>

The project is useful architectural history—endpoint-zero sensor control plus
bulk-IN Bayer frames—but not a drop-in driver.

### ArduCAM MT9J001 support

ArduCAM's open repository contains Linux/Raspberry Pi configurations for the
MT9J001, including an exact 3664-by-2748 mode.  A representative USB 2.0
configuration at commit `23ac88bcbadf2f2652b78a5991980dc11ba6fbf8`
programs output size `0x034c=0x0e50` and `0x034e=0x0abc`, and exposure register
`0x3012`:

<https://github.com/ArduCAM/ArduCAM_USB_Camera_Shield/blob/23ac88bcbadf2f2652b78a5991980dc11ba6fbf8/Config/USB2.0_UC-391_Rev.D/DVP/MT9J001/MT9J001_MONO_8b_3664x2748_4fps.cfg>

These files target ArduCAM controller boards, so their USB bridge protocol is
not compatible with the Tucsen C003 bridge.  They are nevertheless the most
promising open source for checking full-resolution sensor timing, crop, PLL,
and exposure plans before those plans are translated into the already-proven
C003 `b7` register-write transport.  Register plans must be compared and
tested incrementally; they must not be replayed wholesale.

## Decision

No maintained, drop-in Linux driver was found for `0547:c003`.  The project
should keep the camera-specific transport in user space:

1. stabilize the trace-derived libusb reader and its exposure/gain controls;
2. expose the proven 1280-by-960 stream through the existing V4L2 loopback
   bridge for ordinary Linux applications;
3. use the ArduCAM MT9J001 configurations and the ToupTek GSPCA driver only as
   reviewed sensor/V4L2 prior art while adding full-resolution modes; and
4. consider a native kernel GSPCA driver only later, if a user-space bridge
   proves inadequate for latency, throughput, or deployment.

The current userspace reader is therefore not a fallback after failing to find
an obscure package.  It is the only direct Linux path in this search that has
actually initialized the physical camera, applied controls, captured a live
stream, and delivered it to an application-facing video interface.
