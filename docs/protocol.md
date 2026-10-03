# Observed protocol for USB `0547:c003`

This document describes behavior verified against one AmScope-branded Tucsen
TCA camera. It is an interoperability record, not vendor documentation.

## USB topology

- USB 2.0 high speed, bus powered
- vendor-specific interface 0
- bulk-IN endpoint `0x82`, maximum packet size 512 bytes
- commands travel through endpoint zero
- no UVC interface and no bulk-OUT endpoint

## Cold initialization and mode selection

The working 1280×960 sequence sends these seven vendor/device/IN setup packets
in order. Each requests ten response bytes:

| Step | Request | Value | Index | Delay after |
|---:|---:|---:|---:|---:|
| 1 | `0xb4` | `0x00c2` | `0x0000` | 500 ms |
| 2 | `0xb5` | `0x00a2` | `0x0000` | 30 ms |
| 3 | `0xb7` | `0x1054` | `0x305e` | 30 ms |
| 4 | `0xb7` | `0x0064` | `0x3012` | 30 ms |
| 5 | `0xb5` | `0x00a1` | `0x0000` | 30 ms |
| 6 | `0xb7` | `0x1054` | `0x305e` | 30 ms |
| 7 | `0xb7` | `0x0d0f` | `0x3012` | 120 ms |

The device accepts the setup packet and applies its side effect, then stalls
the IN data stage. Linux reports `LIBUSB_ERROR_PIPE`; usbmon records `-EPIPE`
with zero response bytes. This exact signature was observed for every legacy
command in the successful Windows trace and reproduced by the native Linux
reader. Treating the stall as a fatal command failure prevents initialization.

The implementation accepts either this expected stall or a complete ten-byte
data stage, but no other result. It does not retry a command.

Mode 0 uses the same fixed sequence with only step 1 changed to selector
`0x00c0`. The recovered mode table maps it to 3664×2748, and the physical
camera completed the resulting twenty-read frame schedule. Mode 2 remains the
default because it is better suited to preview and the V4L2 adapter.

## Frame transport

One device frame is read from endpoint `0x82` as:

```text
524288 + 524288 + 180736 = 1229312 bytes
```

The application image is 1280×960 Bayer8, or 1,228,800 bytes. The device/DLL
contract rounds the transfer allocation one extra 512-byte packet beyond an
already aligned image size, leaving 512 surplus bytes after the image.

The recovered capture routine expresses that rule exactly as
`((width * height >> 9) + 1) << 9`: select the next 512-byte boundary,
including one extra packet when the pixel count is already aligned. Applied to
the 3664×2748 mode, this gives 10,068,992 device bytes (nineteen 524,288-byte
blocks plus 107,520 bytes). A physical one-frame probe validated all twenty
predicted markers; the public reader then captured three consecutive mode-0
frames and returned to mode 2 without a reset.

A ten-byte run of `0x88` begins at each 524,288-byte read boundary: three
markers in mode 2 and twenty in mode 0. The legacy application replaces each
marker with the following ten pixel bytes. The reader first validates every
marker, preserves the untouched first device frame separately, performs that
repair in its application buffer, and emits only the mode's image bytes.

After a VirtualHere macOS-to-Linux ownership handoff, one physical run returned
a complete-size initial device frame whose first marker was absent while the
later markers remained aligned. The next open produced a normal frame. The
reader therefore permits a bounded initial resynchronization window: before
delivering its first application frame, it may discard at most two
marker-invalid warm-up frames. The first untouched device frame is still
written once for diagnosis. Marker loss after delivery begins, or exhaustion
of the two-frame limit, remains fatal; command transfers are never retried.

The present FFmpeg/V4L2 path uses `bayer_grbg8`. That phase matches recovered
application memory conventions but still needs optical confirmation because
the sensor was covered during protocol work.

## Controls

Request `0xb7` writes the supplied 16-bit value to the register in `wIndex`.
Like initialization, its ten-byte IN data stage stalls after the setup side
effect.

- Exposure uses coarse-integration register `0x3012`. Mode 2 has a recovered
  120 µs row time; `lines = ceil(milliseconds × 1000 / 120)`, bounded to
  1–4000 lines (public range 1–480 ms). Mode 0 uses its recovered 309 µs row
  time and a public range of 1–1236 ms.
- Analog gain uses register `0x305e`. Public gain 0–320 uses the piecewise
  encoding recovered from the matching control implementation:

```text
  0.. 63: 0x1040 + gain
 64..127: 0x1800 + gain
128..191: 0x1bc0 + gain
192..255: 0x1c00 + gain
256..319: 0x1cc0 + gain
320:      0x1dff
```

Both bounded controls were issued on the physical camera and followed by three
complete frames. Their optical effect has not yet been calibrated with the
sensor uncovered.

## Evidence lineage

The sequence was captured below a working legacy Windows stack using Linux
usbmon and a one-device USB relay. The physical capture contained 744 paired
operations: 25 standard controls, 191 vendor controls, and 528 bulk-IN
transfers, with no pairing gaps. All 191 vendor command data stages ended in
the same expected `-EPIPE` signature. Direct Linux replay of only the seven
startup setup packets enabled continuous bulk streaming without Windows.

The code is independently written and contains no vendor binary, firmware,
header, or source. Reverse-engineering artifacts and redistributability-
restricted material are deliberately excluded from this repository.

## Known limitations

- only fixed modes 0 (3664×2748) and 2 (1280×960) are enabled;
- frame rate depends on mode and exposure; no formal performance guarantee;
- no automatic exposure, white balance, or host color correction;
- no hotplug daemon or multi-camera selection;
- Apple Silicon live capture is verified through a one-device Pi relay, but a
  native-cable macOS run and AVFoundation integration are not yet verified; and
- optical Bayer phase, color response, exposure scale, and gain response await
  the intended microscope and an uncovered sensor.
