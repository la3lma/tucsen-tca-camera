# Linux V4L2 producer-timing preparation

Date: 2026-10-04

## Result

Public main commit `a60ecac38e328fd83c2a780d4bf57ddc538d48b8`
adds an opt-in `TCA_TIMESTAMPS` path to the Linux V4L2 bridge. The bridge now
passes that path to the reader's already-validated `--timestamps` option while
leaving the Bayer/YUYV stream and default behavior unchanged.

This closes an instrumentation gap in the pending Linux application test. A
normal V4L2 consumer can record its own frame count and timing while the reader
preserves a flushed `CLOCK_MONOTONIC` producer sidecar. The two records must be
reported separately: reader delivery cadence is not a claim about application
display cadence, and a count difference can include bounded pipeline frames as
well as consumer loss.

Public main commit `470b3d9099b7a43f2dd7d9966c9dea2322f46bab`
then packages the entire pending physical check as
`tools/run_linux_v4l2_acceptance.sh`. With no arguments it is inert. Its live
path requires an exact token, a clean built worktree, a valid matching
calibration, exactly one attached camera, an unused loopback slot, an existing
evidence parent, and pre-primed sudo credentials. It composes corrected V4L2
streaming, a bounded ordinary FFmpeg consumer, full YUYV preservation,
per-frame digests, producer/consumer summaries, clean teardown, immediate
reader reuse, and a complete SHA-256 manifest.

## Safety and validation

- With no arguments, `scripts/tca-v4l2` remains inert and prints
  `NO USB TRANSFER SENT`.
- `TCA_TIMESTAMPS` is optional. When supplied, it must be a distinct,
  nonexistent regular-file path; `-`, an existing path, and the raw-evidence
  path are rejected before Linux, camera, or loopback checks.
- The bridge still exposes no arbitrary USB request, reset, configuration,
  alternate-setting, firmware, or kernel-camera-driver operation.
- The full suite passed locally on Apple Silicon.
- A detached exact-commit worktree at
  `/home/rmz/tucsen-tca-camera-v4l2-timing-a60ecac` passed
  `make clean all test` on Raspberry Pi AArch64. This run was USB-inert because
  the camera remained connected to the Mac.
- GitHub CI run
  [37199753354](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37199753354)
  passed on Ubuntu and macOS. Pages run
  [37199753340](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37199753340)
  also passed.
- Exact harness commit `470b3d9` passed `make clean all test` and the inert
  harness invocation in a separate detached Raspberry Pi AArch64 worktree.
  GitHub CI run
  [37200208874](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37200208874)
  passed on Ubuntu and macOS; Pages run
  [37200208867](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37200208867)
  passed as well.
- The current-tree and full-history public/private publication audit passed in
  the full local checkout. The Pi's shallow source repository correctly
  skipped only the history portion while passing the current-tree policy.

## Pending physical acceptance

After a valid same-settings dark/flat calibration exists and the camera moves
to Linux, execute `tools/run_linux_v4l2_acceptance.sh` with its exact token.
The harness runs the corrected bridge with both `TCA_FLAT_FIELD` and
`TCA_TIMESTAMPS`, while a separate ordinary V4L2 application consumes a
bounded run and preserves its frame count, elapsed time, and logs. Acceptance
requires:

1. a valid producer timestamp report from `tca-timing-stats`;
2. exact consumer frame size and the requested bounded frame count;
3. distinct consumer-frame hashes or a lossless frame digest record;
4. an explicit producer-versus-consumer count/cadence comparison that does not
   mislabel bounded pipeline frames as proven drops;
5. clean bridge shutdown, loopback removal, and immediate reader reuse; and
6. a SHA-256 manifest for the complete session directory.

No physical claim is made by this preparation record.

## Planning provenance

The local Development Evidence skill currently documents an OpenAPI endpoint
at `127.0.0.1:18080`; its `/openapi.json` path returned HTTP 404 during this
work. The Agency console at `127.0.0.1:18116` was healthy, and its live
Docstack forum retained the single-start/single-exit DAG, evidence-gate, and
clickable-navigation conventions already enforced by this repository's local
validator. The validated repository plan and GitHub state were therefore used
as the authoritative fallback. No Development Evidence service record is
claimed or implied by this note.
