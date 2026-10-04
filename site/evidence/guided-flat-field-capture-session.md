# Guided physical flat-field capture session

Date: 2026-10-04

Public implementation: `tucsen-tca-camera` commit
`176ef90152cf4acabb7fddbee5439c732c2e9741`.

## Purpose

The remaining valid flat-field gate requires coordinated physical actions that
software cannot infer: illumination must actually be blocked for darks, the
blank must be translated or defocused between flat groups, a fresh blank must
be withheld from calibration, and a real specimen must verify that correction
does not erase structure. Manual command sequences made it too easy to reuse a
scene as its own flat, mix exposure/gain settings, overwrite earlier evidence,
or accept a partial session.

`tools/run_flat_field_capture_session.sh` turns that gate into one explicit,
fail-closed workflow. With no argument it prints its usage and:

```text
NO USB TRANSFER SENT. NO FILE OR SYSTEM CHANGE MADE.
```

Only the exact `--run-flat-field-capture-session` token enables the interactive
path. Before creating its output directory it validates every option and
dependency, requires canonical integer ranges, and refuses any existing
destination.

## Locked session

The helper supports preview mode 2 and records one exposure, normalized gain,
and Bayer phase for the entire session. Its default sequence is:

1. prompt for physically blocked illumination and capture 16 dark frames;
2. prompt for four separately translated or defocused blank positions and
   capture four frames at each position;
3. build and inspect a `TCAFF01` map carrying the same exposure and gain;
4. prompt for a fresh blank not held stationary during calibration, preserve
   its device/Bayer bytes, correct it, analyze both frames, and render both;
5. prompt for a real specimen, preserve/correct/analyze/render it identically;
   and
6. hash every completed artifact.

Every capture must contain an exact 1,229,312-byte first device record and the
requested number of exact 1,228,800-byte Bayer frames. Any error, EOF, signal,
short artifact, tool failure, or interrupted operator prompt leaves
`SESSION-INCOMPLETE.txt`. A successful session removes the exit trap instead
and prints one `status=ok` summary. The helper never loads a kernel module,
creates a V4L2 node, resets the camera, or exposes arbitrary USB operations.

## USB-free end-to-end validation

`tests/test_flat_field_capture_session.py` first verifies inert behavior and
pre-output rejection of an invalid exposure. It then substitutes a fake camera
that emits exact-size deterministic dark, flat, blank, and specimen frames,
while using the real public `tca-flat-field` binary and
`scripts/tca-frame-stats`. A fake renderer isolates FFmpeg availability from
the session semantics.

The test checks:

- EOF at the first prompt sends no capture and creates an incomplete marker;
- two dark and two separately batched flat frames have exact stream sizes;
- calibration metadata records 1280x960 GRBG, 100-ms exposure, gain 20, and
  the exact frame counts;
- a synthetic 80-count blank becomes 70 after a 10-count dark is subtracted;
- a synthetic 60-count specimen becomes 50;
- four PNG derivatives are produced; and
- every manifest entry exists and matches its SHA-256 digest.

The complete native suite passed on Apple Silicon using the project-local
ARM64 libusb. A clean shallow clone of exact public commit `176ef90` at
`/home/rmz/tucsen-tca-camera-guided-176ef90` then built and passed the complete
suite on Raspberry Pi AArch64 Linux 6.18.39. The Pi had no camera attached, and
the dynamic test used only the fake camera, so no physical USB transfer was
sent.

## Exact Pi artifacts

```text
be752cb44596532bd08142f3bb69fabd667419f7dd4c1921c0f5149b1749429b  tools/run_flat_field_capture_session.sh
30b5b7ca2b6141d7c3dda041dff5f08bd4c12b2aa6846d9a8739b9cea9d6b316  tests/test_flat_field_capture_session.py
83bf700be8efad320b7f1c55ddafedab2e2e40eb87b0d9545446822240f1b05f  build/tca-flat-field
65f9f7e73a22128549755871e9d445ff308d7409b3f3cd59bea7387ee2367f9a  scripts/tca-frame-stats
```

## Remaining gate

This evidence proves workflow safety, portability, exact artifact handling, and
calibration composition. It does not prove optical calibration. The next
operator-assisted action is to run the public helper with the camera still on
the Mac optical bench, follow each physical prompt literally, and inspect the
fresh-blank and real-specimen before/after results. The resulting map can then
be used at the same settings for the later live Linux V4L2 acceptance run.
