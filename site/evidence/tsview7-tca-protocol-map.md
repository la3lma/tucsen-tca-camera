# TSView7 TCA-10.0N protocol map

Static inspection performed 2026-09-27. No extracted Windows executable was
run and this analysis, by itself, sent no request to the camera.

## Source lineage

The official Tucsen discontinued-camera matrix maps USB identity `0547:c003`
to both the older TCA-10.0N and later IS1000 names. Crucially, it assigns the
TCA model to TSView6 or TSView7, whereas IS1000 is assigned to ISCapture 3.6.8.
The camera's purchase period and the exact identity therefore make the TCA
software a necessary protocol source rather than an optional comparison.

Downloaded official archives and hashes:

| Archive | SHA-256 |
|---|---|
| `work/vendor-zips/TSview6.2.3.3-eng-Setup.zip` | `d6a0302832894531085fb58d15cfb694fca777efc48888e269f8a5393771b6d8` |
| `work/vendor-zips/TSView-7.3.1.8-En-Setup.zip` | `1afb0f263127c12c9add1b09fcc720900163a210d3c6ef1374f22b09b5b0144b` |

The TSView7 installer contains the 32-bit DLL
`work/vendor-extracted/tsview7/inno/app/TS1000.dll`, linked 2010-06-29, with
SHA-256
`ee9c8ec6a680404c375a6bf0c44ded0486c6e7557cdee379a5f332eb9a8d12ac`.
It opens the TCA device path literal `\\.\tca000-0`. This is not the same
binary as the later ISCapture `TS1000.dll` whose hash begins `8262ee47`.

## Matched transport

This DLL and the 2011 TCA driver agree on IOCTL `0x222059`. The driver's TCA
handler hard-codes `bmRequestType=0xc0` and copies record offsets 4, 6, and 8
to `bRequest`, `wValue`, and `wIndex`. The direct-I/O output-buffer size becomes
the USB control response length.

The TCA DLL uses a substantially different request family from the later
ISCapture DLL. Confirmed TCA requests include:

| Request | Direction/length | Observed role |
|---:|---:|---|
| `0x02` | `0xc0`, zero bytes | Called during open/initialization with `wIndex=0x000f` |
| `0x03` | `0xc0`, zero bytes | Paired state command with `wIndex=0x000e` |
| `0x09` | `0xc0`, variable | Two wrappers associated with device state |
| `0x0a` | `0xc0`, one byte | Sensor-register write with one-byte acknowledgement |
| `0x10` | `0xc0`, one byte | Register write with acknowledgement `0x08` |
| `0x11` | `0xc0`, three bytes | Register read: two-byte big-endian value plus `0x08` acknowledgement |

Although the transfer direction is IN, requests `0x0a` and `0x10` are
device-changing writes. Direction alone is not a safety classification.

## Evidence-backed read candidate

The wrapper at `0x10009590` constructs:

```text
bmRequestType = 0xc0
bRequest      = 0x11
wValue        = 0x0000
wIndex        = register address
wLength       = 3
```

This field order is confirmed independently at both sides of the ABI. The DLL
stores its register argument at input-record offset 8; the 2011 driver copies
offset 8 to `wIndex` and offset 6 to `wValue`. The earlier interpretation put
the register in `wValue` and was incorrect.

It requires response byte 2 to equal `0x08`, then interprets bytes 0 and 1 as
a big-endian 16-bit register value. The caller at `0x10008780` uses the fixed
register address `0x3ff0`; another caller writes and reads that address back as
a verification pair. The standalone read is therefore the first concrete,
non-mutating, nonzero-response candidate for a bounded Linux experiment.

`tools/tca_register_probe.c` encodes only that fixed tuple. It accepts no
arbitrary request fields, performs no bulk read or reset, has a one-second
timeout, and is inert without an exact opt-in token.

## Required open prefix

A standalone `0x11` read may still depend on the DLL's open state. In the
successful-open path at `0x10008e3d`, the DLL first sends request `0x02` with
`wIndex=0x000f`, then performs a driver-local IOCTL, and only then begins the
sensor-register validation reads. On close, `0x10008ea0` sends request `0x03`
with `wIndex=0x000e`.

The request values depend on a product-string flag. The DLL compares
`manufacturer + "-" + product` with the de-obfuscated literal
`DO3THINK-10M USBCam`. The observed camera strings (`123456789` and
`10MP CMOS Camera `) do not match, selecting value zero for both the open and
close requests. The resulting fixed prefix is:

```text
c0 02 0000 000f length 0
c0 11 0000 3ff0 length 3, final byte expected 08
c0 03 0000 000e length 0
```

`tools/tca_open_read_probe.c` version 2 implements exactly this bounded prefix.
It records an open timeout but still attempts the one fixed read, matching the
vendor DLL's unchecked open-wrapper result. It then attempts close after the
read. Other open failures remain terminal.

## Consequence for prior trials

The five earlier bounded Linux control-transfer attempts used requests from the
later ISCapture DLL (`b4`, `ba`, or `bb`). Their stalls do not falsify the TCA
protocol. They demonstrate that the two software generations cannot be mixed
merely because both packages claim `0547:c003`.
