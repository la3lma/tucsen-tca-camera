# Uncorrected physical Linux V4L2 acceptance preparation

Date: 2026-10-04

Candidate commit `5670678`, merged as public main `caea706`, removes an
unnecessary dependency between physical
Linux application transport acceptance and the separate hands-on optical
dark/flat calibration. The camera cable can now move to Linux and prove the
ordinary-application path immediately, while corrected physical delivery
remains a later, stricter gate.

## Contract change

`tools/run_linux_v4l2_acceptance.sh` now accepts either:

- `-`, meaning an explicitly uncorrected transport/application run; or
- a calibration path, retaining strict geometry, Bayer-phase, exposure, and
  gain validation before the camera or loopback setup is touched.

The evidence profile is now `tca-linux-v4l2-acceptance-v3`. Both paths record
the selected `calibration_mode`, exact release commit, camera and host
identity, reader timestamps, bounded consumer YUYV bytes, per-frame digests,
producer/consumer counts and cadence, bridge exit status, cleanup, immediate
reader reopen, and a SHA-256 manifest. The uncorrected path writes an explicit
JSON marker instead of pretending that a flat-field map was applied.

An uncorrected pass proves physical USB-to-application transport. It cannot
satisfy the optical flat-field acceptance criterion and must not be described
as corrected delivery.

## Cross-platform verification

The exact candidate passed the complete native suite on Apple Silicon,
including inert harness behavior, shell syntax, both supported mode contracts,
the map-backed branch, the uncorrected branch, Pages references, and the
full-history public/private publication boundary.

The Raspberry Pi created a detached exact-commit worktree and passed the same
complete AArch64 suite. The bench initially exposed a real missing dependency:
`/usr/bin/time`, used to measure the ordinary application's elapsed time. The
standard Debian `time` package was installed, and the README dependency list
now includes it.

With the camera still on the Mac, a token-gated uncorrected invocation on the
Pi then produced exactly:

```text
status=69 before=0 after=0
expected exactly one 0547:c003 camera
```

This is the intended fail-closed point. The `-` argument passed calibration
selection and dependency validation, the absent physical camera was detected,
and the acceptance evidence-directory count remained unchanged. No bridge,
loopback device, USB transfer, or partial evidence session was created.

## Remaining gate

Move the camera to the Pi and run mode 2 with the `-` calibration argument.
If that passes, repeat mode 0 uncorrected. After a valid same-settings
blocked-dark and translated/defocused flat map exists, repeat the appropriate
mode with that map to establish corrected physical Linux delivery.
