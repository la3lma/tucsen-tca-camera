# Guarded full-resolution probe

Prepared and physically completed 2026-10-03. This note separates the facts
available before the test from the result that resolved its one transport
inference.

## Evidence already established

1. Static analysis of the purchase-era DLL maps fixed mode 0 to 3664 by 2748
   Bayer8 pixels, or 10,068,672 application bytes. The same mode table maps its
   later-lineage selector to request `b4`, value `0x00c0`.
2. The selector was already issued once in a bounded control-only Linux trial.
   It produced the same `PIPE` data-stage result seen in the successful Windows
   trace, and subsequent health checks passed. That trial did not attempt a
   frame.
3. The successful mode-2 Windows trace and direct Linux reader establish that
   the active later-lineage transport requests 524,288-byte blocks, uses the
   next 512-byte boundary, and begins every requested block with ten
   bytes of `0x88`. At `0x1001aa51`--`0x1001aa5d`, the capture function
   computes `((width * height >> 9) + 1) << 9`. This gives an extra packet when
   the pixel count is already aligned and ordinary round-up otherwise. A
   separate `width * height + 0x200` buffer allocation provides headroom but
   is not the requested transfer length.
4. Mode 2 therefore transports 1,229,312 device bytes for 1,228,800 pixels:
   two 524,288-byte reads and one 180,736-byte read. The public reader has
   reproduced that schedule across hundreds of physical frames.

## Explicit inference under test

Applying the observed mode-2 transport rule to mode 0 gives:

```text
pixel bytes       = 3664 * 2748             = 10,068,672
device bytes      = ((pixels >> 9) + 1) << 9 = 10,068,992
full reads        = 19 * 524,288             =  9,961,472
final read        = device - full reads      =    107,520
expected markers  = one per read             =         20
```

The mode selector and geometry came from recovered vendor code, while the
padding/chunk rule came from a successful mode-2 physical trace. Their
combination was the single proposition tested below.

The older TCA DLL's four-lane scheduler is useful corroborating geometry but
is not treated as the transfer schedule for this later-lineage command family.

## Bounded implementation

`tools/tca_mode0_frame_probe.c`:

- is inert without the exact token `--probe-inferred-mode0-once`;
- changes only the first tuple of the seven-command successful mode-2 startup,
  from `b4/c2` to recovered mode-0 selector `b4/c0`;
- captures at most one 10,068,992-byte device frame;
- requests exactly nineteen 524,288-byte blocks and one 107,520-byte block;
- requires ten `0x88` bytes at every block boundary;
- preserves every received raw byte, including a bounded partial result after
  a later failure;
- has no reset, firmware, configuration, alternate-setting, arbitrary-request,
  retry, loop, or teardown path.

Two C17 static assertions independently require the recovered next-packet
formula and the twenty-read sum to equal the fixed device-frame ceiling, so a
future constant edit cannot silently desynchronize allocation and transport.

`make mode0-frame-probe` builds the binary, runs only its dry profile, audits
its libusb import surface, and verifies that a wrong token creates no output.
The complete project core tests and this new test pass on Apple Silicon. The
same source builds warning-free and dry-runs on ARM64 Linux; its Pi source and
binary hashes are:

```text
573fc512bc769d0c19b5c0d4df1bda9f84d0018f67249732edd44a9666684872  source
1195ff665b7ec779ecbda053ce0db573b6b6de73ef0158d08cec78d8510f9f57  Pi binary
```

## Physical result

The live one-frame run was sequenced after the successful mode-2 endurance
test so a mode change could not invalidate that baseline. It exited zero after
receiving all 10,068,992 bytes in the predicted twenty reads. All twenty
markers passed at offsets `n * 524288`, for `n = 0..19`. The untouched frame
SHA-256 is:

```text
3fa7a539b2141b653af305a721c793be297f4ac8e40c6c1ac051f669ebcd57e4
```

The 10,068,672-byte repaired pixel plane has minimum 8, median 12, mean 11.893,
99th percentile 13, and maximum 222. This is consistent with the covered
sensor and is a transport sanity check, not optical validation. The remaining
320 bytes are the exact next-packet alignment surplus predicted by the
recovered formula.

An unconditional recovery command reselected mode 2 and captured three frames
with exit zero. The verified profile was then promoted into the public reader
behind explicit option `--mode 0`; that implementation captured three
consecutive mode-0 frames followed by three mode-2 frames. The inference is
therefore resolved for this camera. Raw evidence and logs are preserved under
`work/public-release-validation-20261003/mode0-probe-20261003T204800Z/`.
# Superseding optical note (2026-10-04)

The exact physical-record byte count in this historical probe remains valid,
but the twenty-read/marker and simple-prefix interpretations do not. Optical
testing proved a 10,068,992-byte record interval. A complete frame is record N
`[512,10068992)` followed by the 192-byte continuation at record N+1
`[320,512)`. Separate 524,288-byte requests restart at new record origins. See
`first-optical-capture.md`.
