# Opt-in operable libusb control backend

Evidence date: 2026-09-29

## Scope and separation

`src/tca_libusb_operable.[ch]` composes the read-only warm bulk backend with
the already recovered control planners and fail-fast executor. It is a
separate opt-in module: the existing `camera-reader-warm` binary still links no
control-transfer API. Only a separately named, inert-by-default, one-control
CLI instantiates the operable module. This preserves the reviewed read-only
streaming gate while preparing the control portion of D70 for a known-good
warm handoff.

The operable backend supports only the public reader's three recovered hardware
controls:

- exposure in checked milliseconds, implemented by one acknowledged write to
  sensor register `0x3012`;
- normalized analog gain `0..320`, implemented by one request-`0x09` state
  update; and
- frame-speed value `0..3`, implemented by the exact eleven-write/two-delay
  PLL plan.

No arbitrary request tuple, firmware path, reset, configuration change,
alternate setting, or retry is exposed.

## Composition and diagnostics

The operable object embeds `struct tca_libusb_warm` as its first member. A
compile-time offset assertion protects the callback-context composition. All
descriptor, claim, bulk-read, stop, and close operations therefore remain the
reviewed warm implementation. The added `set_control` callback:

1. requires successful fixed mode-4/speed-0 configuration;
2. asks `tca_controls` to construct a checked fixed plan;
3. executes it through `tca_executor` with a bounded timeout and no retry;
4. retains the complete execution report, including failed step, transport
   status, expected/actual length, and acknowledgement; and
5. updates frame-speed state only after every plan step succeeds.

The production defaults are `libusb_control_transfer` and interrupt-resilient
`nanosleep`. Both boundaries are injectable for offline tests.

## Native fault-injection proof

`tests/test_tca_libusb_operable.c` performs no enumeration and sends no USB
operation. With a dummy shared handle and injected callbacks it verifies:

- the exact exposure tuple for 10 ms in mode 4/speed 0, including 80 sensor
  lines, XOR encoding, one-byte acknowledgement, and 1000 ms timeout;
- the exact normalized-gain tuple at boundary value 64;
- eleven writes and delays of 1 ms and 10 ms for frame speed 2;
- refusal before configuration, of other initial modes/speeds, and of an
  unknown control;
- fail-fast transport timeout, short response, bad acknowledgement, and delay
  failure reports; and
- no frame-speed state update after a partial failed plan.

Strict C17 builds and all tests pass natively on Apple Silicon macOS and the
Ubuntu ARM64 VM. The macOS sanitizer build also passes AddressSanitizer and
UndefinedBehaviorSanitizer.

The resulting test binaries import the same descriptor/open/claim/release and
bulk APIs as the read-only warm backend plus exactly
`libusb_control_transfer`. Their SHA-256 values are:

```text
04da3fa95fabd6f06021e78a06436ca78141f85837ff5cd2d5e5e96d98b7d6b7  work/test_tca_libusb_operable
5c44e25b557935c3eba7ce5e0c2b0b4c6063c8d757d17386c578204e1ead8518  work/test_tca_libusb_operable-linux-arm64
```

## Bounded control CLI

`tools/tca_control_warm.c` is a separately named command that applies exactly
one checked control and exits. With no arguments it is inert. It accepts only
one of three explicit tokens whose names include the already-streaming mode-4
precondition, followed by one decimal value. Exposure, gain, and frame-speed
range validation occurs before libusb initialization or device open; malformed,
negative, and out-of-range values exit 64 while explicitly reporting that no
USB transfer was sent.

An accepted invocation opens and claims the exact device, records fixed mode 4
and speed 0 as the handoff metadata, executes one plan through the reader API,
prints the full step-level diagnostic on failure, then releases the interface.
It never starts acquisition and its source contains no reader start/pump or USB
reset call. Static/inert tests and the exact import allowlist pass on both
architectures. The binaries have SHA-256:

```text
f415131f480cdf4e4b6ff2d9ce226040c5e0fc24b5c3d9087a33508a3fd54e28  work/camera-control-warm
6992db88b7463e7bc536aa0e4ffde758661fd2ceab9f74a7e8419bfdc481da42  work/camera-control-warm-linux-arm64
```

## Remaining live gate

This is verified implementation evidence, not physical-camera control proof.
The command has not been run with an execution token. After the known-good
Windows sequence is traced and a warm handoff is available, it can test one
bounded control at a time while preserving raw frames and usbmon evidence. A
successful warm control session still would not by itself prove cold
initialization, reconnect, or endurance.
