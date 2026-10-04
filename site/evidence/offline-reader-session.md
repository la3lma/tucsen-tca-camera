# Portable reader session, queue, and CLI

Evidence date: 2026-09-29

## Scope

The first D70 implementation slice is a transport-neutral C17 reader session.
It does not link libusb and cannot send a USB request. A backend callback table
supplies enumeration, claim, configuration, start, exact raw-frame capture,
control, stop, close, and clock operations. The replay backend and mock backend
exercise the same surface intended for the future traced live USB backend.

Sources:

- `src/tca_reader.h`
- `src/tca_reader.c`
- `tools/tca_reader_cli.c`
- `tests/test_tca_reader.c`
- `tests/test_tca_reader_cli.py`

## Lifecycle and fault contract

The implementation enforces:

```text
disconnected -> enumerated -> claimed -> initialized -> acquiring
                                                    -> stopping -> initialized
any active state -> fault -> close -> disconnected
```

Each backend failure records the prior state, operation name, expected and
actual byte length, and backend status. An exact-length failure enters `fault`;
`close` then releases the backend and allows a complete reopen/configure/start
cycle. There are no implicit retries.

## Frame and queue contract

For every accepted raw frame the core:

1. requires the fixed mode's exact `width * height` Bayer8 byte count;
2. decodes using an explicit Bayer pattern and RGB/BGR output order;
3. assigns a monotonic sequence and backend-clock timestamps;
4. snapshots mode, frame speed, exposure, and analog gain; and
5. places the decoded frame in a bounded queue.

`keep-latest` drops the oldest queued frame when full and increments the drop
counter. `lossless` preserves queued frames, rejects the newly acquired frame
with a backpressure result, and increments both backpressure and drop counters.
The caller must explicitly choose the policy.

The control surface accepts exposure milliseconds, normalized analog gain, and
the four recovered frame-speed values. It reuses the existing control planners
for range checking and rejects a faster frame-speed selection if the current
exposure would exceed the new mode/speed limit. The backend remains responsible
for executing the already modeled request plans.

## CLI

The `work/camera-reader` prototype exposes two safe commands:

```sh
work/camera-reader inspect --mode 4
work/camera-reader replay --mode 4 --pattern grbg --order rgb24 \
  INPUT.raw OUTPUT.rgb
```

`inspect` reports geometry, frame/chunk sizes, scheduled reads, row time,
maximum exposure, and gain range. `replay` sends exact Bayer frames through the
reader lifecycle, decoder, queue, pop, diagnostics, stop, and close paths. It
contains no live backend.

`replay` also accepts `--repeat COUNT`; zero means repeat until interrupted.
Only seekable, non-empty, exact-frame files may repeat, and repeating stdin is
refused. This supplies a bounded-memory continuous source to the temporary
V4L2 bridge without weakening short-frame validation.

Using the authoritative live-captured mode-4 frame, the reader emitted 921,600
RGB24 bytes with SHA-256:

```text
7bd81cd2db9c3cf620dfeec3de087bf9b8f884544d7183b4465b63676e97d5c8
```

The output is byte-identical to `tca_raw_convert` for the same input, pattern,
and order. Diagnostics report one captured, queued, and delivered frame with no
drop or backpressure event.

## Verification

Native macOS:

- strict C17 build with `-Wall -Wextra -Werror -pedantic` passes;
- lifecycle, metadata, controls, latest-queue, lossless-backpressure,
  short-frame fault, close/reopen, and backend-failure tests pass;
- CLI inspect, two-frame replay, short trailing-frame failure, diagnostics,
  and argument refusal tests pass;
- AddressSanitizer and UndefinedBehaviorSanitizer execution passes.

Ubuntu ARM64 VM:

- the same strict C17 reader and CLI build natively as AArch64 ELF binaries;
- reader session and CLI black-box tests pass; and
- the captured-frame RGB24 hash matches macOS exactly.

The full project core, raw replay, and TSView emulation suites also pass after
this addition.

## Remaining boundary

This is meaningful D70 code but not D70 completion. The callback surface still
needs a live backend after D40/D50 establish the cold-start sequence, and live
streaming still needs repeated physical-frame timestamps, controls, reconnect,
and endurance proof. The new core deliberately does not guess those operations.
