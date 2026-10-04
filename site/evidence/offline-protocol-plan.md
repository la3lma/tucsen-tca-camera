# Offline TCA protocol-plan verification

Verification performed 2026-09-27. The module described here contains no USB
transport code and did not access the camera.

## Implemented slice

`src/tca_protocol.c` and `src/tca_protocol.h` convert the byte-accurate
TSView7 reconstruction into portable, typed protocol records. They provide:

- the corrected open (`c0 02 0000 000f`) and close
  (`c0 03 0000 000e`) records;
- a register read with the address in `wIndex`, zero in `wValue`, a three-byte
  response, and acknowledgement `response[2] == 0x08`;
- request-`0x0a` register writes with both the sensor register and data encoded
  by XOR with `0x17a0`, plus `response[0] == 0x08`;
- all five fixed-mode initialization plans recovered by the offline x86
  emulator, including state requests, calibration reads, and the exact
  300/1/10/200 ms delays; and
- a size-query/capacity API that refuses partial plan output.

The module allocates no memory, imports no USB API, and does not sleep. It only
describes operations for a future checked transport executor. Dynamic ROI mode
5 remains deliberately unsupported.

`tools/tca_plan_dump.c` is an offline renderer. For example,
`make plan-dump MODE=4` prints the 43-step 640x480 plan and labels itself
`offline-only=yes`.

## Golden tests

`tests/test_tca_protocol.c` independently carries the decoded register/value
pairs for every fixed mode. It verifies all 154 writes, plan ordering, both
state records, calibration-read addresses, acknowledgement offsets, delays,
invalid modes, size queries, and insufficient-capacity refusal.

The macOS build uses strict C17 warnings as errors:

```text
cc -O2 -std=c17 -Wall -Wextra -Werror -pedantic -Isrc \
  src/tca_protocol.c tests/test_tca_protocol.c -o work/test_tca_protocol
./work/test_tca_protocol
tca protocol tests: PASS
```

The same sources compiled natively on `rpios-17` as AArch64 and passed. A
dynamic undefined-symbol audit of both the test and plan renderer found no
`usb` or `libusb` symbol. The Pi binary hashes were:

```text
e2e927a3356863bf7f24709bc39a0a9c728887d2ec37cbc828d65d5c87a3d20a  test_tca_protocol
d109e9a24e54011034650c33b9b7e83793bc2c001f4803c93a78f0d834ebfd0d  tca_plan_dump
```

The Python emulator golden test and the existing frame-core test also passed
after this module was added.

## Fail-fast executor

`src/tca_executor.c` and `src/tca_executor.h` add the transport-neutral
execution contract. A caller supplies control-transfer and sleep callbacks;
the executor itself still has no libusb dependency. It performs each step once
with no retry, requires the exact response length, validates the declared
acknowledgement byte, and stops before the next step on any transport, length,
acknowledgement, malformed-plan, or excessive-response error. Its report names
the zero-based failing step, number of completed steps, raw transport status,
and expected/observed response facts.

`tests/test_tca_executor.c` uses only a mock transport. It proves a complete
43-step mode-4 run, injects a transport failure independently at every step,
and verifies that no later operation runs. It also covers short responses, bad
acknowledgements, bad step types, invalid acknowledgement offsets, oversized
responses, and API argument errors. Strict C17 and Apple
AddressSanitizer/UndefinedBehaviorSanitizer runs passed. The same source passed
natively on the Pi with no USB symbols; its AArch64 binary hash was:

```text
fd0f6f9bbe2c8c473191043ef520591e2746ce3d099068ff74a102bf014cc8da  test_tca_executor
```

## Boundary

These plans are derived from emulated vendor code with synthetic read replies.
They prove packet construction and make the future executor reviewable; they
do not prove that the physical camera accepts any mutating initialization
write. D40 still requires the corrected bounded read after a true USB power
cycle. The executor now supplies the length/acknowledgement and stop-on-first-
fault mechanics, but it must not be connected to a live libusb transport for
full initialization until D50. A live adapter must also retain raw evidence.
