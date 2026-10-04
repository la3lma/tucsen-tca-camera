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

The implementation accepts this expected stall or a complete ten-byte data
stage. Direct Apple Silicon testing additionally found an intermittent
one-byte response whose byte exactly echoed the request (`b4`, `b5`, or `b7`):
10 of 140 bounded startup controls produced this signature, with no arbitrary
values. The reader therefore also accepts exactly one byte equal to the
request. Every other short response remains fatal. It does not retry a
command.

Mode 0 uses the same fixed sequence with only step 1 changed to selector
`0x00c0`. The recovered mode table maps it to 3664×2748, and the physical
camera completed full-record capture in that mode. Mode 2 remains the default
because it is better suited to preview and the V4L2 adapter.

## Frame transport

One device record must be requested from endpoint `0x82` in one bulk API call.
Mode 2 requests 1,229,312 bytes and mode 0 requests 10,068,992 bytes. A request
split into separate 524,288-byte calls does not continue the same record: each
call restarts at a new record origin. Concatenating those calls therefore
creates repeated image regions and a sharp false seam even though the byte
count is correct.

The beginning of each record has ten `0x88` marker bytes. Preview frames fit
wholly after a 512-byte prefix. Full-resolution frames cross a record boundary:
record N holds the first 10,068,480 pixels after offset 512, and bytes 320–511
of record N+1 hold the remaining 192 pixels. Bytes 512 onward in record N+1
simultaneously begin the next frame, so the reader retains that record as its
look-ahead buffer.

| Mode | Record bytes | Frame assembly |
|---:|---:|---|
| 2 | 1,229,312 | record N `[512,1229312)` = 1,228,800 pixels |
| 0 | 10,068,992 | record N `[512,10068992)` + record N+1 `[320,512)` = 10,068,672 pixels |

The recovered capture routine expresses that rule exactly as
`((width * height >> 9) + 1) << 9`: select the next 512-byte boundary,
including one extra packet when the pixel count is already aligned. Applied to
the 3664×2748 mode, this gives 10,068,992 device bytes. Initially treating the
formula's 320-byte surplus as a simple mode-0 prefix put the previous frame's
192-pixel continuation at the left of the next frame. That produced a false
purple strip. A longer diagnostic request exposed the next `0x88` marker at
exactly byte 10,068,992, proving the boundary and the look-ahead layout above.
Three consecutive look-ahead-assembled frames were then captured with unique
hashes and no strip. The reader preserves the untouched first device record
separately and validates every consumed record marker.

Earlier relay traces appeared as 524,288-byte pieces and were initially
interpreted as application-level read boundaries. Optical autocorrelation and
single-request probes disproved that interpretation. Historical byte-count
and endurance results remain useful for USB stability, but images assembled
from several independent bulk calls are not spatially valid.

After a VirtualHere macOS-to-Linux ownership handoff, one physical run returned
a complete-size initial device record whose leading marker was absent. The
next open produced a normal record. The
reader therefore permits a bounded initial resynchronization window: before
delivering its first application frame, it may discard at most two
prefix-invalid warm-up frames. The first untouched device record is still
written once for diagnosis. Prefix loss after delivery begins, or exhaustion
of the two-frame limit, remains fatal; command transfers are never retried.

The present FFmpeg/V4L2 path uses provisional `bayer_grbg8`. Microscope imagery
is spatially coherent with that interpretation, but a known color target is
still needed to distinguish the four Bayer phases conclusively.

The dependency-free `tca-white-balance` helper can use a neutral slide region
to estimate red, green, and blue multipliers. On the current tungsten-lit
microscope it independently produced approximately red 0.87, green 1.0, and
blue 1.98–2.0 in both modes. That is an in-situ white balance, not a Bayer-phase
proof or a calibrated illuminant measurement.

The separate `tca-flat-field` user-space tool implements residual spatial
shading correction without changing this USB protocol. It averages complete
dark and flat Bayer streams, derives independent median-normalized R/G1/G2/B
gain maps, stores explicit geometry and fixed-point calibration records, and
can filter concatenated Bayer frames before demosaic or V4L2 output. Raw frames
remain the authoritative capture.

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

Both bounded controls were issued on the physical camera and followed by
complete frames. The device has one record already buffered under its preceding
settings, so the reader consumes one record after a control write before it
publishes frame zero. A microscope-mounted 100-ms sweep then showed mean raw
intensity increasing from 14.67 at gain 0 to 154.88 at gain 320. Gain 256 gave
mean 83.23 with only about 0.0005% saturated pixels. Absolute response still
needs calibration against a known target and controlled illumination.

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
- no automatic exposure or continuously adaptive host color correction;
- no hotplug daemon or multi-camera selection;
- Apple Silicon live capture is verified both through a one-device Pi relay
  and over a direct native cable; AVFoundation integration is not yet
  implemented;
- final Bayer phase, absolute color response, exposure scale, and gain response await a
  known optical target and controlled calibration.
