# Offline four-lane capture scheduler

Verification performed 2026-09-27. All transfers in this note use a mock
transport and synthetic frame data. No USB API is linked and no request was
sent to the camera.

## Implemented slice

`src/tca_capture.c` and `src/tca_capture.h` turn the statically recovered
TSView7 bulk scheduler into a portable transport-neutral operation. For one
fixed-mode frame the core:

- obtains the authoritative geometry and chunk lengths from `tca_frame`;
- primes up to four full-chunk reads into caller-supplied lane staging buffers;
- completes and resubmits lanes in the vendor scheduler's round-robin order;
- copies completed staging data into non-overlapping frame offsets;
- requires a full chunk for every ordinary completion and the exact recovered
  remainder for the intentionally short final completion;
- performs no retry;
- cancels every still-active lane after submit, completion, or length failure;
- reports the failed lane, frame offset, requested/expected/actual lengths, raw
  transport status, completed bytes, and cancellation results; and
- returns success only when the accumulated byte count exactly equals
  `width * height`.

The distinction between requested and expected length is essential. The DLL
requests one full `chunk_bytes` transfer every time, including the last read.
The camera is expected to end that last transfer after exactly `final_bytes`.
Any other short or long completion may be a stall, truncation, or frame-boundary
loss. Continuing while later lanes are already queued could silently shift
frames, so the reader preserves an unexpected length as an error rather than
padding, concatenating, or guessing.

The module allocates no memory and knows nothing about libusb, threads, files,
or image decoding. A future Linux adapter will implement the three callbacks:
submit one endpoint-`0x82` read, wait for its completion, and cancel an
outstanding lane. The same core can be used by macOS or a recorded fixture.

## Independent vendor-path confirmation

The Unicorn fixture now stubs `ReadFile` and `GetOverlappedResult` and invokes
the DLL's real `GrabFrame` routine. Across all five modes it independently
confirms every full-chunk request, `0,1,2,3` lane rotation, expected completion
length, resubmission, frame offset, and output byte. This check caught and
rejected an earlier scheduler draft that submitted a reduced final request;
the corrected implementation instead matches the vendor request size while
using staging memory to keep the smaller output frame safe.

## Golden and fault-injection tests

`tests/test_tca_capture.c` runs all five fixed modes with deterministic bytes.
It checks frame contents, all recovered read counts and lane rotations, and a
mode with a fifth read that resubmits lane zero. Every test asserts that all
submissions request a full chunk while the final actual length equals the
mode-specific remainder. It then injects independently:

- a submit failure at every read boundary;
- a completion failure at every read boundary;
- a one-byte-short completion at every read boundary; and
- a cancellation failure while unwinding a primary completion failure.

Every failing case proves that no lane remains active. Argument, unsupported
mode, and capacity boundaries are also covered. Strict C17 and Apple
AddressSanitizer/UndefinedBehaviorSanitizer runs pass.

The same sources compiled and passed natively on `rpios-17` as AArch64. A
dynamic-symbol audit found no USB symbol:

```text
tca capture scheduler tests: PASS
dynamic-usb-symbols=none
28e5c634fb6bc1d23c8662116c454f7af5d4b29e30b8d20f7a1ceef819b7fa66  test_tca_capture
```

## Boundary

This proves scheduler ordering, staged memory safety, the full-request/final-
remainder distinction, unexpected-length refusal, and fail-fast cancellation
using synthetic data. It is not a live capture and does
not establish endpoint behavior, timing, phase, orientation, or sustained
throughput. The module remains disconnected from libusb until D40 provides a
stable control response and D50 validates initialization. D60 must retain the
first raw frames and actual transfer-length trace before changing this policy.
