# Full-resolution Linux V4L2 application path

Date: 2026-10-04

## Result

Candidate public commit `a93f538610937ddf3e68a1f4c332af5272792882`
extends the optional Linux V4L2 bridge from the established 1280x960 preview
mode to the reader's complete 3664x2748 full-resolution mode. Existing bridge
invocations remain mode 2; an explicit final `0` selects mode 0.

The exact commit passed the complete native suite on Apple Silicon and in a
detached Raspberry Pi AArch64 worktree, plus Ubuntu and macOS CI
[run 37202391321](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37202391321).
Token-gated, USB-inert executions then exercised both geometries through the
real flat-field corrector, FFmpeg conversion, `v4l2loopback` device, and
ordinary `v4l2-ctl` consumers.

## Application-boundary proof

Mode 0 exposed `/dev/video45` as 3664x2748 YUYV with a declared image size
of 20,137,344 bytes. A first consumer captured two frames, exactly 40,274,688
bytes. It detached; a second consumer attached with a 350-ms delay after every
buffer and captured three frames, exactly 60,412,032 bytes. Frame-digest
validation accepted all five frames.

The bridge remained live after the slow consumer. Its process-tree RSS was
406,912 KiB cold, 515,088 KiB after the first consumer had warmed the complete
pipeline, and 544,592 KiB during reattached slow consumption. The relevant
warm-baseline growth was 29,504 KiB, below the unchanged 65,536-KiB ceiling.
This distinction was added after an earlier exact-commit trial correctly
exposed that a cold baseline counted one-time full-resolution FFmpeg buffer
allocation as if it were queue growth.

TERM returned the declared status 143. The bridge removed the temporary video
node and the `v4l2loopback` module it had loaded. The exact mode-0 evidence
manifest verifies byte-for-byte, and its digest is:

```text
d8ed4f9a706725c68a9a0ee2a5504bbe9a21570c9c74f9d4583b3bbc4275013d
```

## Preview regression proof

The same commit retained the mode-2 path. `/dev/video44` reported 1280x960
YUYV and a 2,457,600-byte image size. Consumers received four normal and eight
delayed frames across detach/reattach. Warm-baseline RSS growth was zero,
producer timing analysis accepted 94 synthetic frames at 19.6574 frames/s,
and signal/device/module cleanup passed. The mode-2 manifest digest is:

```text
b18a7e22aa312e3e9c67dbed2f8266fd5d8d8b8c8799988fbab0c51381eb2129
```

The synthetic source cadence is only a pipeline test parameter, not a physical
camera performance claim.

## Reproduction and safety

Running the harness without arguments is inert. The explicit full-resolution
test is:

```sh
sudo tools/run_v4l2_bridge_synthetic_acceptance.sh \
  --run-v4l2-bridge-synthetic-acceptance OUTPUT_DIRECTORY 45 0
```

The mode-2 regression run uses final argument `2`. The harness refuses dirty
source, existing output, an already-loaded loopback module, or an occupied
device number. Its test double contains no USB interface implementation and
the harness statically rejects camera-reader binaries, libusb transfers, USB
resets, reauthorization, configuration changes, and firmware-like operations.
The physical camera remained attached to the Mac throughout these Pi runs.

Complete integration artifacts remain private under
`work/pi-synthetic-v4l2-full-resolution-a93f538/`. Both nested manifests
were independently checked after retrieval. Only derived facts and digests
are published.

## Scope and remaining gate

This proves that ordinary Linux V4L2 applications can consume the software
pipeline at both supported reader geometries, including complete 10 MP frames,
without a camera-specific kernel driver. It also proves consumer
detach/reattach, bounded post-warm-up memory growth, deterministic shutdown,
and scoped compatibility-layer cleanup.

It does not prove the physical camera's Linux V4L2 cadence, a valid optical
dark/flat map, final Bayer phase/color, or cable reconnect. Those remain
operator-assisted acceptance gates. The exact-token
`tools/run_linux_v4l2_acceptance.sh` now accepts mode 0 as its final argument
for a later physical run.

## Planning provenance

The Development Evidence service contract expected at
`127.0.0.1:18080/openapi.json` returned HTTP 404 during this work. The
validated Docstack, exact Git commit, Pi evidence manifests, and hosted CI are
therefore the authoritative fallback. No Development Evidence service state is
claimed.

