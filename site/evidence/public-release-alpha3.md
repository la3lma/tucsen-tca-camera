# Public release v0.2.0-alpha.3

Date: 2026-10-03

Release: <https://github.com/la3lma/tucsen-tca-camera/releases/tag/v0.2.0-alpha.3>

The annotated tag `v0.2.0-alpha.3` resolves to exact source commit
`3c16d2ae560ae0668033b70c42ce881d78197959`. It packages the optical-validation
procedure and Bayer statistics/focus tool from `a61c044`, plus the documented
and tested install/removal operations from `fb502c1`.

## Hosted validation

The source commit passed Ubuntu and macOS CI on public main:

<https://github.com/la3lma/tucsen-tca-camera/actions/runs/37151187248>

Pushing the annotated tag triggered a second independent Ubuntu/macOS run,
which also passed:

<https://github.com/la3lma/tucsen-tca-camera/actions/runs/37151241568>

The GitHub release is published as a prerelease rather than a final release. Its
notes explicitly preserve the open physical camera-cable reconnect and
microscope optical checks, as well as the non-blocking native-cable macOS and
AVFoundation deferrals.

## Downloaded source archive

The public tag archive was downloaded into the report project, rather than a
global downloads directory:

```text
aa8a7c7fd6827d0a06c8fbb657c43f769b841466c78783c9a0d34502e70af63e  tucsen-tca-camera-v0.2.0-alpha.3.tar.gz
```

It was extracted into a new directory with no repository metadata. From that
clean source archive, Apple Silicon `make clean all test` rebuilt the reader
and passed all four suites, including staged installation and exact-file
removal. This confirms that the public archive contains the documented optical
procedure, analyzer, tests, and required source rather than relying on files in
the development checkout.

## Exact-tag Raspberry Pi validation

A fresh detached worktree on `rpios-17` checked out exact commit `3c16d2a`.
`make clean all test` rebuilt the reader and passed the reader, V4L2, Bayer
statistics, and staged install/removal suites. The install/removal test kept an
unrelated same-directory sentinel intact.

That exact build then cold-opened the attached physical `0547:c003` camera,
applied normalized gain 20 and 100-ms exposure, captured one mode-2 frame, ran
the released analyzer, and exited zero with `frames=1 status=ok`.

```text
f6f616099ff80093de15ddc34f228e089b9225d85fb86f6ff486c9519b56d0c5  one-device-frame.raw
4227f9e9b0db7a6b2fddf68582f16617df7a5f2510bcc5f28a5d3cdb9767a258  one-frame.bayer
aa962bebbed86e017ccde05b9af217d78dbfe9b5bc3fea3f96fbb32497b3dfd9  one-frame.stats.json
```

The raw device frame is exactly 1,229,312 bytes and its Bayer payload is
exactly 1,228,800 bytes. The local evidence is preserved under
`work/public-release-validation-20261003/alpha3-live-20261003T202050Z/`.

The sensor remained covered. This exact-tag run proves source identity,
build/test reproducibility, physical transport, controls, frame sizes, and the
analysis path; it does not establish Bayer phase, color, orientation, or focus.
