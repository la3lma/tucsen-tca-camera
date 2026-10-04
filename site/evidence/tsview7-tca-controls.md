# TSView7 TCA control-surface reconstruction

Verification performed 2026-09-27. This work combined static disassembly,
offline x86 emulation, and portable C tests. No USB transfer was sent to the
physical camera during this work.

## Sources and scope

The matching private reference binary is
`work/vendor-extracted/tsview7/inno/app/TS1000.dll`, SHA-256
`ee9c8ec6a680404c375a6bf0c44ded0486c6e7557cdee379a5f332eb9a8d12ac`.
Its exported camera-control wrappers were traced into the internal camera
object and then executed in the existing Unicorn fixture with the Windows
driver boundary stubbed. The original TSView manual
`work/vendor-extracted/tsview7/inno/app/TSView.pdf` was inspected as a UI-level
cross-check. Manual pages 16–21 describe exposure, gain, automatic white
balance, gamma, contrast, saturation, color enhancement, monochrome, mirrors,
frame speed, and 50/60 Hz illumination selection.

The manual establishes what the application presented to a user. The DLL
establishes which settings become hardware requests and which remain host
image-processing state. Neither source proves that this physical camera
accepts a request; that remains behind the D40/D50 live gates.

## Hardware versus host processing

The emulated driver boundary observed hardware records for only three control
families:

| Control | Hardware operation | Recovered public semantics |
|---|---|---|
| Exposure | one request-`0x0a` write to sensor register `0x3012` | input is milliseconds; register value is `ceil(ms * 1000 / row_time_us)` |
| Analog gain | one request-`0x09`, `wIndex=1`, no response | normalized input `0..320` is encoded piecewise in `wValue` |
| Frame speed | 11 request-`0x0a` register writes with 1 ms and 10 ms delays | internal API accepts four values `0..3`; TSView exposes Normal/High |

Automatic-exposure state and target, automatic white balance, RGB processing
gains, gamma, color enhancement, saturation, contrast, horizontal/vertical
mirror, monochrome, light-frequency choice, and white-balance windows produced
no driver IOCTL in isolated setter calls. They are host algorithm or image
processing settings. Automatic exposure can subsequently drive the hardware
exposure setter, so “host state” does not mean it has no eventual camera-side
effect.

The raw DLL defaults after fixed-mode initialization were AE on, AWB on, AE
target 120, 262 ms exposure, analog gain 20, RGB processing gains 74/64/96,
gamma 100, color enhancement on, saturation 100, contrast 30, mirrors off,
monochrome off, frame speed 0, and light-frequency state 0. TSView labels
gamma, contrast, and saturation as `-20..20`; their exact UI-to-DLL
normalization is not yet recovered, so the portable API must not expose the
internal numbers as user-facing values.

## Exposure capabilities

The sensor maximum is 4000 exposure lines. The recovered row time and
floor-derived maximum public exposure are:

| Fixed mode | Speed 0 | Speed 1 | Speed 2 | Speed 3 |
|---|---:|---:|---:|---:|
| 0 | 309 µs / 1236 ms | 247 µs / 988 ms | 206 µs / 824 ms | 195 µs / 780 ms |
| 1 | 166 µs / 664 ms | 133 µs / 532 ms | 111 µs / 444 ms | 105 µs / 420 ms |
| 2 | 120 µs / 480 ms | 96 µs / 384 ms | 80 µs / 320 ms | 76 µs / 304 ms |
| 3 | 125 µs / 500 ms | 100 µs / 400 ms | 83 µs / 332 ms | 78 µs / 312 ms |
| 4 | 125 µs / 500 ms | 100 µs / 400 ms | 83 µs / 332 ms | 78 µs / 312 ms |

The vendor setter does not safely reject every invalid value. The portable
plan API therefore accepts only `1..maximum_exposure_milliseconds`, computes
the line value with a ceiling, and rejects rather than silently overflowing.

## Analog-gain encoding

For normalized gain `g`, the request-`0x09` value is:

```text
  0.. 63: 0x1040 + g
 64..127: 0x1800 + g
128..191: 0x1bc0 + g
192..255: 0x1c00 + g
256..319: 0x1cc0 + g
320:      0x1dff
```

The vendor code clamps values above 320. The portable plan rejects them so a
caller cannot mistake a coerced value for the requested setting.

## Frame-speed sequence

Each internal speed uses the same guarded PLL sequence. Only registers
`0x0304` and `0x0306` vary:

| Speed | `0x0304` | `0x0306` |
|---:|---:|---:|
| 0 | `0x0002` | `0x0028` |
| 1 | `0x0002` | `0x0032` |
| 2 | `0x0002` | `0x003c` |
| 3 | `0x0001` | `0x0020` |

The complete sequence is `0104=0001`, `0100=0000`, the two variable writes,
`0300=0005`, `0302=0001`, `0308=000a`, `030a=0002`, delay 1 ms,
`301a=90d8`, `0104=0000`, delay 10 ms, and `0100=0100`.

## Portable implementation and verification

`src/tca_controls.c` and `src/tca_controls.h` describe the hardware controls
as transport-neutral plan steps. They allocate no memory, contain no USB
imports, and do not execute delays. `tests/test_tca_controls.c` verifies all 20
mode/speed capability cells, exposure boundaries and line conversion, every
piecewise gain boundary, all four exact frame-speed plans, size queries,
capacity refusal, and invalid inputs. Strict C17 and Apple
AddressSanitizer/UndefinedBehaviorSanitizer runs pass.

The emulator golden test independently invokes the vendor DLL setters. It now
checks the same 20 row-time/maximum-exposure cells, four PLL sequences, an
exposure conversion, and all gain encoding boundaries. `make test-emulator`
passes with no host USB module imported.

The portable sources also compiled and passed natively on `rpios-17` as an
AArch64 executable without accessing the camera:

```text
tca controls tests: PASS
58c0bb8f9ec5ff2fee3f9fd9beaa83454a2884c290e9300c113a186349bafdef  test_tca_controls
```

## Boundary and next gate

This closes the offline packet-construction problem for exposure, analog gain,
and frame speed. It does not authorize sending them to the device. D40 still
requires the single corrected open/read/close prefix immediately after a true
camera USB cold cycle. Only after a stable live read should D50 connect these
plans to the checked executor and validate one conservative setting at a time.
Raw and decoded values must be logged for every live control experiment.
