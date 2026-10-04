# Offline TCA frame-core verification

Verification performed 2026-09-27. These tests contain no USB transport code
and did not access the camera.

## Implemented slice

`src/tca_frame.c` and `src/tca_frame.h` provide two bounded, portable pieces
needed by the eventual reader:

1. the five fixed TSView7 TCA mode geometries and the recovered bulk-chunk
   scheduler; and
2. a caller-owned frame assembler that accepts arbitrary transfer fragments,
   emits completion only at the exact expected byte count, reports an
   incomplete frame, and rejects overflow without silently truncating data.

The implementation allocates no memory and owns no USB handle. The caller
supplies both the destination buffer and its capacity.

## Test coverage

`tests/test_tca_frame.c` verifies:

- all five fixed dimensions, frame byte counts, chunk sizes, remainder sizes,
  and scheduled-read counts against the independently recovered constants;
- assembly using the vendor scheduler for every mode, including the
  10,068,672-byte full-sensor frame;
- byte-for-byte preservation across arbitrary fragments including 1, 7, 511,
  512, 513, 4093, and 16384-byte boundaries;
- invalid arguments and undersized destination capacity;
- incomplete-frame reporting; and
- overflow rejection before a partial overrun can be copied.

Host build and run:

```text
clang -O2 -std=c17 -Wall -Wextra -Werror -pedantic -Isrc \
  src/tca_frame.c tests/test_tca_frame.c -o work/test_tca_frame
./work/test_tca_frame
tca frame tests: PASS
```

Apple Clang AddressSanitizer plus UndefinedBehaviorSanitizer, with leak
detection disabled because Darwin's ASan runtime reports it unsupported:

```text
/usr/bin/clang ... -fsanitize=address,undefined ...
ASAN_OPTIONS=detect_leaks=0:abort_on_error=1 ./work/test_tca_frame_apple_san
tca frame tests: PASS
```

The same sources were copied to `rpios-17`, compiled natively with GCC as an
AArch64 PIE, and passed there:

```text
/home/rmz/microscope-window-sensor-probe/reader/test_tca_frame:
  ELF 64-bit LSB pie executable, ARM aarch64
tca frame tests: PASS
```

The macOS undefined-symbol audit contains only assertion, stack-protection,
allocation, `memcpy`, and output functions. The Pi binary links only libc.
Neither binary imports libusb or another device-access library.

## Boundary

This is an offline core slice, not evidence that a physical frame has been
captured or decoded. It can accept a future bulk transfer without changing
the byte-count contract, but D40/D50 must still establish the camera's working
state-entry and initialization sequence before the transport calls it.

