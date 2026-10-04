# TSView7 TCA initialization emulation

Offline reconstruction performed 2026-09-27. No host USB API is imported by
the emulator and no camera device can be opened by it.

## Method and boundary

`tools/emulate_tca_init.py` maps the preserved 32-bit x86 TSView7
`TS1000.dll` (SHA-256
`ee9c8ec6a680404c375a6bf0c44ded0486c6e7557cdee379a5f332eb9a8d12ac`)
into Unicorn. It constructs the DLL's camera object and emulates the fixed-mode
initialization routine. Windows process calls and the driver boundary are
stubbed. Calls to `DeviceIoControl(0x222059)` are recorded as their raw
ten-byte input records.

The private evidence DLL is emulated, not run natively. The emulated device
open is forced successful, and register-read responses are synthetic values
chosen only to keep the recovered control flow moving. Consequently this is
byte-accurate evidence of what this DLL constructs for the driver under those
responses; it is not evidence that the physical camera accepts the sequence.

The project-local environment uses `pefile==2024.8.26` and `unicorn==2.1.4`,
pinned in `tools/requirements-emulation.txt`.

## Corrected record layout

The raw first mode-4 write record is:

```text
01 02 00 10 0a 00 a0 17 a0 16
```

The matching TCA driver maps byte 4 to `bRequest`, bytes 6--7 to `wValue`, and
bytes 8--9 to `wIndex`. Request `0x0a` XOR-obfuscates its fields with `0x17a0`:

```text
wValue ^ 0x17a0 = data value
wIndex ^ 0x17a0 = sensor register
```

The example therefore writes value `0x0000` to register `0x0100`. Request
`0x11` records instead have `wValue=0x0000` and the register in `wIndex`. This
independently corrects the earlier Linux read probe, which had reversed those
fields.

## Fixed-mode result

All five fixed modes return success in the synthetic environment and use the
same sleep schedule: 300, 1, 10, and 200 ms.

| Mode | Decoded `0x0a` writes | Synthetic calibration reads |
|---:|---:|---|
| 0 | 28 | `0x24c0`, `0x24c4`, `0x24c6` |
| 1 | 28 | `0x24c0`, `0x24c8` |
| 2 | 28 | `0x24c0`, `0x24cc` |
| 3 | 35 | `0x24c0`, `0x24d0` |
| 4 | 35 | `0x24c0`, `0x24d4` |

The complete mode-4 decoded write sequence is held as a golden fixture in
`tests/test_emulate_tca_init.py`. It includes the expected window registers,
PLL/timing setup, grouped-parameter holds, stream start (`0x0100=0x0100`), and
final `0x3012=0x0836` write. The dynamic ROI mode 5 is deliberately omitted.

Run the deterministic offline verification with:

```sh
make test-emulator
```

The test checks all mode counts, timing calls, calibration-read addresses,
the raw first IOCTL record, the corrected read field order, the exact mode-4
write list, and the absence of host USB imports.

## Emulated bulk scheduler

The emulator also stubs `ReadFile` and `GetOverlappedResult` and calls the
vendor `GrabFrame` path at `0x100020f0`. For all five fixed modes, the DLL:

- creates and rotates four overlapped lanes in order `0,1,2,3`;
- submits `chunk_bytes` for every read, including the last;
- accepts `chunk_bytes` for each ordinary completion;
- accepts the smaller `final_bytes` remainder for the last completion; and
- copies exactly `width * height` deterministic bytes into the caller buffer.

The golden test verifies every submission, completion, lane, requested length,
actual length, frame offset, and output byte across all modes. This independently
corrected an initial portable-scheduler draft that had requested only the final
remainder directly. The portable implementation now uses four explicit staging
buffers so its submitted lengths match the DLL without risking a write beyond
the output frame.

## Bayer phase and byte order

The same isolated emulator calls the DLL's default bilinear conversion routine
at `0x10005250` with an 8x8 synthetic mosaic whose four 2x2 phases contain
distinct constants. Every interior output pixel becomes `30 25 20`, while the
routine zeros its one-pixel border. The only consistent interpretation is:

```text
raw phase at memory origin:  G R
                             B G    (GRBG)

24-bit output byte order:    B G R  (Windows BGR24)
```

This identifies the DLL's memory convention without claiming how the sensor is
physically rotated in the microscope. Physical orientation and whether a live
frame starts at the same crop phase still require a captured target image.

## Live-use consequence

This extraction narrows future implementation work but does not authorize a
full initialization replay. The next physical action remains the one bounded
v2 open/read/close probe after a genuine camera USB power cycle. If that first
corrected read succeeds, the emulated write sequence can be divided into
small, evidence-backed live prefixes with health checks and recovery between
them.
