# Offline TCA startup-signature core

Implemented and verified 2026-09-29. This module has no USB dependency and
cannot access the camera.

## Purpose

The purchase-era TSView7 DLL sends its open wrapper and then validates 80
even-numbered sensor registers from `0x0000` through `0x009e` before applying a
mode plan. The existing portable mode-plan core began after that gate.
`src/tca_startup.c` now represents the missing offline slice.

The module:

- emits exactly 80 `0xc0/0x11` three-byte register-read steps;
- places each even register address in `wIndex` and zero in `wValue`;
- requires the established acknowledgement `0x08` at response byte 2;
- exposes the 80 expected big-endian values recovered by the independent
  extractor; and
- validates decoded values with a deterministic first-mismatch report.

The first entry is register `0x0000 = 0xc247`; the last is register
`0x009e = 0x01d0`.

## Deliberate boundary

The open request is not folded into this read plan. TSView7 ignores its open
wrapper's result, while `tca_execute_plan` is intentionally fail-fast. A live
adapter must model that transition explicitly, based on the accepted D40
trace, rather than weakening the generic executor or silently ignoring a
transport error.

No signature read or other transfer was sent while implementing this module.

## Verification

`tests/test_tca_startup.c` checks:

- size-query and insufficient-capacity behavior;
- every request field for all 80 reads;
- register sequence `0x0000..0x009e`;
- first and last expected values;
- exact-signature success;
- first-mismatch register, expected value, and actual value; and
- invalid pointer/count handling.

Run with:

```sh
make test-startup
```

Result on macOS and the project-local Ubuntu ARM64 VM:
`tca startup signature tests: PASS`. The independent Raspberry Pi was not
reachable during this run, so its earlier core validation was not silently
extended to this new module.

The source values are independently reproducible from the pinned DLL
disassembly using `python3 tools/extract_tca_signature.py`. See
`tsview7-tca-startup-validation.md` and
`ghidra-targeted-decompilation.md` for the two static-analysis paths.
