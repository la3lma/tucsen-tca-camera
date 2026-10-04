# Optical validation tooling readiness

Date: 2026-10-03

Scope: public repository commit
`a61c0443a82cbeb3d6eac67f9a27f6621c844fe7`.

This record proves that the remaining microscope-mounted checks have a tested,
reproducible procedure and working analysis tool. It does **not** claim an
optical result: the camera sensor was still covered for every physical capture
described here.

## Published tooling

Commit `a61c044` adds:

- `scripts/tca-frame-stats`, a Python-standard-library utility for exactly one
  headerless Bayer8 frame;
- `tests/test_frame_stats.py`, including geometry, parity, focus, JSON, error,
  and no-overwrite checks;
- `docs/optical-validation.md`, covering Bayer phase, orientation, exposure,
  gain, a manual focus curve, a full-resolution still, V4L2 consumption, and
  the acceptance record; and
- `make install` integration for the analyzer.

The analyzer reports exact geometry and SHA-256, intensity percentiles and
clipping, the four sensor-parity planes, all four candidate Bayer phase maps,
and population variance of a four-neighbour Laplacian over non-overlapping
2-by-2 Bayer-tile means. The latter makes the initial focus score independent
of an unverified Bayer phase.

The commit was pushed to public `main`. GitHub Actions run
<https://github.com/la3lma/tucsen-tca-camera/actions/runs/37150645082>
completed successfully on both Ubuntu and macOS.

## Workstation checks

The complete reader, V4L2, and analyzer test suite passed on Apple Silicon.
A staged `make install` produced executable `tca-camera`, `tca-v4l2`, and
`tca-frame-stats` programs; the installed analyzer accepted a preserved
physical-camera frame.

The four documented FFmpeg phase commands were exercised against that
1,228,800-byte frame. They produced four valid 1280-by-960 RGB PNG files using
`rggb`, `grbg`, `gbrg`, and `bggr`. Because the sensor was covered, those files
validate the conversion commands only; they cannot identify the correct phase.

## Exact-commit Raspberry Pi check

A detached clean worktree at exact commit `a61c044` was created on
`rpios-17`. `make clean all test` passed all three suites. With the physical
`0547:c003` camera attached, that build then ran:

```text
./build/tca-camera capture --frames 1 \
  --raw-first work/live-tool-a61c044-20261003T201236Z/one-device-frame.raw \
  --bayer work/live-tool-a61c044-20261003T201236Z/one-frame.bayer \
  --exposure-ms 100 --gain 20
scripts/tca-frame-stats \
  work/live-tool-a61c044-20261003T201236Z/one-frame.bayer \
  --json work/live-tool-a61c044-20261003T201236Z/one-frame.stats.json
```

The capture exited zero with `frames=1 status=ok`. It preserved exactly
1,229,312 device bytes and emitted exactly 1,228,800 Bayer bytes. The analyzer
identified mode 2 at 1280 by 960, processed 304,964 focus samples, and reported
mean 10.0366, median 10, 1st/99th percentiles 9/11, no zero pixels, and no
saturated pixels. Those dark-frame values are transport/tooling evidence, not
an optical calibration.

Artifact hashes:

```text
1b6b22cb6536207fbec018380b995c1e2df6aa0be2c4b826c8090798c34a897e  one-device-frame.raw
432421f874cfb0a902273b8a9abda440df3aabc72944b87bbd363c63e16fd23a  one-frame.bayer
6472450bf0138f18780826eba3e150137f49c96286969ff76c6e1b119d2f8df1  one-frame.stats.json
```

The project-local copies are in
`work/pi-live-optical-tool-a61c044-20261003T201236Z/`.

## Decision

The optical session no longer depends on designing ad-hoc measurements at the
microscope. D60 remains open only because an exposed sensor, optical path,
textured specimen, and color reference are physically required. No Bayer
phase, orientation, color, or focus claim should be made from these covered-
sensor frames.
