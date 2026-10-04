# Installed V4L2 helper discovery

Date: 2026-10-04

Public main commit `e1632505ed62acb060ac243668a0cf7879ad331e`
closes a Linux packaging defect in the optional application bridge. The
source-tree `scripts/tca-v4l2` correctly found helpers under `build/`, but
the installed copy retained that source-tree assumption even though
`make install` places `tca-v4l2`, `tca-camera`, and `tca-flat-field`
together in `PREFIX/bin`. A documented installation could therefore build
and install successfully yet fail before opening the camera.

## Correction

The bridge now resolves executables in this order:

1. an explicit `TCA_CAMERA_READER` or `TCA_FLAT_FIELD_TOOL` override;
2. an executable sibling of the installed bridge;
3. the source-tree `build/` location.

The source-tree path remains the final diagnostic fallback so a missing helper
still produces the existing explicit error. The new
`tca-v4l2 --diagnose-install` command reports both resolved paths and their
executable state, prints `NO USB TRANSFER SENT`, and exits without requiring
Linux, loading `v4l2loopback`, opening a video device, or touching USB.

The staged-install regression executes that installed diagnostic rather than
merely inspecting file presence. It also retains the existing exact-file
uninstall check and unrelated-file sentinel.

## Native AArch64 validation

A fresh clone of exact public main `e163250` on Raspberry Pi host
`rpios-17` reported AArch64 and Linux
`6.18.39+rpt-rpi-2712`. No `0547:c003` camera was attached. The clone
completed:

1. a clean native build;
2. the complete project test suite;
3. a staged installation of all six public programs with
   `PREFIX=/usr/local`; and
4. the installed bridge diagnostic.

The installed diagnostic resolved executable sibling copies of
`tca-camera` and `tca-flat-field` under the staged
`usr/local/bin` and ended with:

```text
NO USB TRANSFER SENT.
```

The complete suite also passed locally on Apple Silicon and in hosted
Ubuntu/macOS CI. [PR #16](https://github.com/la3lma/tucsen-tca-camera/pull/16)
was merged to public main before the Pi clone was made.

## Retained private evidence hashes

The private project bundle contains the host/commit inventory, complete native
test log, staged-install log, diagnostic output, summary, and a manifest. It
does not contain vendor software, disassembly, firmware, packet captures, or
credentials.

```text
82f9ff599bf874f2de7139da01bd269b4544ad8fa558f79f381764ae77c6e656  environment.txt
4a7897490d31e2e3c673001ae5875b778063f13939f5d92254b6e3d47b1a1e27  pi-main-e163250-test.log
2cb2eb20381d842aba471c2ef9acd6610103a34ab319f62d69a32ab20cb78768  pi-main-e163250-install.log
9d9fb4f7b255f9d157ad39710c3b5ced7d3843dedea77854a88e06e3c38876c0  pi-main-e163250-diagnose.txt
e9c208b1e6121ad80e77fde02db64970fcd359dccace23f1be186045fa9e2e2b  summary.md
```

This proves the packaged Linux path on native AArch64 without a camera. It
does not replace the still-open physical `0547:c003`-to-V4L2 application
acceptance run.
