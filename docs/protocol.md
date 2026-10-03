# Observed protocol for USB `0547:c003`

This document describes behavior verified against one AmScope-branded Tucsen
TCA camera. It is an interoperability record, not vendor documentation.

## USB topology

- USB 2.0 high speed, bus powered
- vendor-specific interface 0
- bulk-IN endpoint `0x82`, maximum packet size 512 bytes
- commands travel through endpoint zero
- no UVC interface and no bulk-OUT endpoint

## Cold initialization: mode 2

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

## Frame transport

One device frame is read from endpoint `0x82` as:

```text
524288 + 524288 + 180736 = 1229312 bytes
```

The application image is 1280×960 Bayer8, or 1,228,800 bytes. The device/DLL
contract rounds the transfer allocation one extra 512-byte packet beyond an
already aligned image size, leaving 512 surplus bytes after the image.

A ten-byte run of `0x88` begins at offsets 0, 524288, and 1048576. The legacy
application replaces each marker with the following ten pixel bytes. The
reader first validates all markers, preserves the untouched first device frame
separately, performs that repair in its application buffer, and emits only the
1,228,800 image bytes.

The present FFmpeg/V4L2 path uses `bayer_grbg8`. That phase matches recovered
application memory conventions but still needs optical confirmation because
the sensor was covered during protocol work.

## Controls

Request `0xb7` writes the supplied 16-bit value to the register in `wIndex`.
Like initialization, its ten-byte IN data stage stalls after the setup side
effect.

- Exposure uses coarse-integration register `0x3012`. Mode 2 has a recovered
  120 µs row time; `lines = ceil(milliseconds × 1000 / 120)`, bounded to
  1–4000 lines (public range 1–480 ms).
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

- only fixed mode 2 (1280×960) is enabled;
- typical observed rate is about 2 fps;
- no automatic exposure, white balance, or host color correction;
- no full 3664×2740/10 MP capture yet;
- no hotplug daemon or multi-camera selection;
- direct macOS live capture is not yet physically verified; and
- optical Bayer phase, color response, exposure scale, and gain response await
  the intended microscope and an uncovered sensor.
