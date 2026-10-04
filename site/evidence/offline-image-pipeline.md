# Offline Bayer and application-pipeline verification

Verification performed 2026-09-27. All input frames in this note are
synthetic; no USB request or camera capture was performed.

## Vendor memory convention

The matching TSView7 DLL's default bilinear routine at `0x10005250` was called
inside the offline Unicorn environment with a four-phase 8x8 mosaic. Distinct
values were assigned to each position of a 2x2 tile. The routine's interior
output was uniformly `30 25 20`, establishing:

```text
raw phase at memory origin:  G R
                             B G    (GRBG)

DLL 24-bit byte order:       B G R  (Windows BGR24)
```

The deterministic check is part of `tests/test_emulate_tca_init.py`. It does
not establish physical microscope orientation or prove that a live crop begins
on the same phase; those require a captured target.

## Portable decoder

`src/tca_image.c` and `src/tca_image.h` implement a bounded bilinear Bayer8
decoder. All four phase conventions are explicit (`RGGB`, `BGGR`, `GRBG`, and
`GBRG`) and callers choose RGB24 or BGR24 output. The implementation accepts
strides, validates source/destination capacities and multiplication bounds,
allocates no memory, and handles edges using only available neighbours.

This is a conventional portable bilinear decoder, not a claim of byte-for-byte
equivalence with every proprietary TSView interpolation mode. Keeping phase
and byte order explicit lets a live color target correct either convention
without changing transport or frame assembly.

`tests/test_tca_image.c` verifies constant color planes for all four Bayer
patterns and both output orders, padded strides, unchanged padding, and error
boundaries. Strict C17, Apple AddressSanitizer/UndefinedBehaviorSanitizer, and
native Pi AArch64 runs pass. The Pi test binary SHA-256 is:

```text
56b333b2aa6dfd5bf15c087b5e0b7dfb9388b1e23db86c082186a39055b804bb  test_tca_image
```

## Replay and standard-media handoff

`tools/tca_raw_convert.c` consumes one or more exact fixed-mode frames from a
file or standard input. It emits Bayer8, PGM, RGB24, BGR24, or PPM to a file or
standard output. A short trailing frame is a hard error and is never padded or
silently emitted. The binary links only the portable frame and image modules;
it has no USB import.

`tests/test_tca_raw_convert.py` exercises a 640x480 synthetic GRBG frame,
Netpbm headers, RGB values at both image corners, two-frame streaming through
stdin/stdout, a short-frame failure, and argument refusal. It passes on macOS
and natively on the Pi. The Pi converter hash is:

```text
e56f68eb54c5d8de0098d72063557aea644a469dc690045c0dcc2245ad0e1f7f  tca_raw_convert
```

An application-path smoke test streamed three synthetic mode-4 frames through
the converter into FFmpeg 8.1.1 as `rgb24` raw video. FFmpeg accepted 640x480
at 5 fps and produced `work/tca-replay-smoke.mkv` using lossless FFV1. Its
SHA-256 is:

```text
3d5ffde27625901b41f69b2225f19a3bf2b80727a13ff77ead797e23cffa8e35  work/tca-replay-smoke.mkv
```

Example handoff once a raw stream exists:

```sh
work/tca_raw_convert --mode 4 --pattern grbg --format rgb24 - - \
  | ffmpeg -f rawvideo -pixel_format rgb24 -video_size 640x480 \
      -framerate 5 -i - output.mkv
```

## Boundary

This proves deterministic decode, framing refusal, portability, and a standard
media handoff using synthetic inputs. D50/D60 remain incomplete until the
camera accepts initialization, returns authoritative bulk bytes, and a physical
target confirms frame phase, orientation, crop, and color. The raw capture
must remain the authoritative artifact even after decoding.
