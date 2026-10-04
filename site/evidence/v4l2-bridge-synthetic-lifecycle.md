+# Camera-free Linux V4L2 bridge lifecycle acceptance

Date: 2026-10-04

## Result

Candidate public commit `eb8acd32cb2b5b1440b378137142a13fdd5420d9`
passed the complete native suite and a token-gated, camera-free execution of
the real `scripts/tca-v4l2` bridge on the Raspberry Pi. The run substituted
only the USB reader with a deterministic Bayer producer; it retained the real
flat-field corrector, FFmpeg conversion, `v4l2loopback` device, ordinary V4L2
consumers, timestamp analyzer, signal handling, and cleanup paths.

The first consumer captured four exact 1280x960 YUYV frames. It detached, the
bridge stayed alive without a consumer, and a second consumer attached and
captured eight exact frames while sleeping 350 ms after every buffer. The
bridge remained alive through that slower-than-producer path. Its process-tree
RSS changed from 114,464 KiB to 115,648 KiB, a bounded increase of 1,184 KiB
against the harness's 65,536-KiB ceiling.

The synthetic reader produced 93 frames over 4.679245186 seconds. The public
timing analyzer accepted its flushed monotonic sidecar and measured 19.6613
frames/s, with 50.861 ms mean interval and 54.960 ms maximum interval. This is
a test-source rate, not a camera performance claim.

A TERM request returned the bridge's declared status 143. The bridge removed
the temporary `/dev/video44` node and the `v4l2loopback` module it had
loaded. Both consumer byte counts, both frame-digest records, the timing
report, process snapshots, calibration, and cleanup result are covered by a
SHA-256 manifest whose own digest is:

```text
1f6390e603b4a21fe18a19a3884243fa97c7e9256acd33d0ac3d73a5671680f5
```

The complete integration bundle remains in the private report workspace at
`work/pi-synthetic-v4l2/tca-v4l2-synthetic-evidence-eb8acd3/`, consistent
with the project's rule that integration artifacts stay out of the source
repository.

## Defect found and corrected

The first exact-commit trial at `f9341d0` intentionally failed its own final
validation. It exposed two test defects rather than a camera or bridge failure:

1. the synthetic reader numbered timestamp rows from zero while the real
   reader and `tca-timing-stats` contract start at one; and
2. TERM cleanup removed the device and module but returned an unstable bridge
   status.

Commit `eb8acd3` aligns the test double with the real sidecar contract and
makes bridge signal shutdown explicit and deterministic. The failed trial's
device and module cleanup were checked before the corrected rerun. No retry
concealed a USB or image-stream failure.

## Reproduction and safety

Running the harness without arguments is inert:

```sh
tools/run_v4l2_bridge_synthetic_acceptance.sh
```

The system-mutating path requires Linux root and the exact token:

```sh
sudo tools/run_v4l2_bridge_synthetic_acceptance.sh \
  --run-v4l2-bridge-synthetic-acceptance OUTPUT_DIRECTORY 44
```

The harness refuses a dirty worktree, an existing output directory, an
existing loopback module, or an occupied device number. Its static test rejects
camera-reader binaries, libusb transfer calls, USB resets, device
deauthorization, configuration changes, and firmware-like operations. The
synthetic reader contains no USB interface implementation. The physical camera
remained connected to the Mac throughout both Pi trials.

The exact candidate passed:

- `make clean all test` in a detached Raspberry Pi AArch64 worktree;
- the USB-inert dry run on that Pi;
- the complete root-only synthetic lifecycle acceptance; and
- GitHub CI run
  [37201191571](https://github.com/la3lma/tucsen-tca-camera/actions/runs/37201191571)
  on Ubuntu and macOS.

## Scope and remaining gate

This result proves the application-facing bridge can survive consumer
detach/reattach and slow consumption without an unbounded queue, preserve
producer timing, perform corrected Bayer-to-YUYV conversion, and clean up its
generic kernel compatibility layer. It does not prove the physical Linux
camera path, optical calibration, final Bayer phase, or consumer behavior at
the camera's actual cadence.

The remaining Linux application gate is still the exact-token
`tools/run_linux_v4l2_acceptance.sh` run with the camera attached to the Pi
and a valid same-settings dark/flat calibration. That run must preserve both
producer and ordinary-application evidence and immediately reopen the physical
reader after bridge teardown.

## Planning provenance

The Development Evidence service contract expected at
`127.0.0.1:18080/openapi.json` again returned HTTP 404. The repository's
validated Docstack, Git branch, CI run, private evidence bundle, and rendered
public evidence record therefore remain the authoritative fallback. No
Development Evidence service state is claimed.

