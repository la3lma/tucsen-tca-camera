# Release acceptance audit

Date: 2026-10-04

Scope: public Linux-first prerelease `v0.2.0-alpha.7` through public main
`0ff17a6`, including post-release producer timing, physical-acceptance
preparation, two-mode camera-free V4L2 lifecycle, exact-post-merge physical
Apple Silicon regression, optically validated record-boundary assembly, gain,
motion, white-balance, calibrated-field tooling, measured direct-reader
cadence, and mutually linked public evidence, Docstack, and report.

This is a readiness audit, not owner acceptance. It distinguishes a useful
Linux alpha from completion of every item in the Docstack Definition of Done.

## Definition of Done

| Item | Status | Evidence and remaining work |
|---|---|---|
| 1. Still acquisition | Pass for spatial capture; color calibration partial | Correct record assembly produces coherent 1280x960 and complete 3664x2748 Bayer rasters. Exact post-merge public main physically produced three distinct preview and two distinct complete full-resolution frames at 250 ms/gain 0; the analyzed first frames were unclipped and the published full-resolution image has neither the historic half-black boundary nor an edge strip. Final Bayer phase and known-target color response remain open. |
| 2. Streaming | Pass for userspace stream and both software V4L2 geometries; physical Linux application retest partial | A corrected 16-frame run produced 16 distinct coherent frames and an H.264 proof clip. Earlier 14,400-frame testing establishes USB/process endurance but used the superseded multi-request image assembly. Public main `72964bb` includes camera-free V4L2 detach/reattach and delayed-consumer passes at both 1280x960 and 3664x2748 with bounded warm-pipeline RSS, but the post-fix physical Linux consumer cadence/drop comparison remains open. |
| 3. Operation | Partial | Cold start, mode 0/mode 2 selection, start/stop lifecycle, exposure, and analog gain are bounded. A 100-ms optical sweep verified monotonic gain 0..320, and one stale pre-control record is now discarded before frame zero. Neutral-background white-balance estimation is verified. Flat-field maps bind exposure/gain and the V4L2 path fails before camera or loopback mutation on mismatch; true blocked-light dark and blank-field calibration remain open. Automatic exposure and continuously adaptive color correction are explicit non-goals for this bounded alpha rather than hidden acceptance gates. |
| 4. Reader API | Pass | Portable C17 userspace core and CLI provide deterministic raw/Bayer capture, structured diagnostics, bounded controls, dry-run output, and no arbitrary USB request surface. Ubuntu and macOS CI pass. |
| 5. Application path | Pass for software lifecycle at preview and full resolution; physical corrected run open | FFmpeg creates coherent stills and H.264 from the corrected macOS reader. Public main `72964bb` exercised the real Linux V4L2 bridge with a USB-inert reader at 1280x960 and 3664x2748: exact application byte counts, consumer detach/reattach, delayed consumption, bounded post-warm-up RSS, deterministic TERM status, and complete loopback cleanup passed. Commit `470b3d9` packages the remaining bounded live-camera run, cleanup, reopen, and manifest. The earlier physical proof predates the assembly correction. AVFoundation remains deferred. |
| 6. Evidence and recovery | Pass for process/host recovery; physical reconnect open | Protocol notes, hashes, safety boundaries, tests, process-kill recovery, repeated reopen, endurance, host reboot, ownership hand-back, microscope-mounted capture, and a clearly labeled physical-size self-flat diagnostic are recorded. The diagnostic proves correction plumbing while explicitly rejecting its scene-erasing output as optical calibration. The inert physical disconnect/reconnect harness is prepared but has not run. |

## Non-functional requirements

| Requirement | Status | Evidence and remaining work |
|---|---|---|
| NFR-01 safety | Pass | Live behavior is opt-in, bounded, and based on trace-confirmed tuples; no reset, firmware upload, non-volatile write, arbitrary control request, or kernel camera driver is exposed. |
| NFR-02 portability | Pass for the direct reader API | The core builds and tests on AArch64 Linux and Apple Silicon macOS. Exact post-V4L2-merge public main captured the physical camera directly in both supported modes with exact frame sizes, changing coherent optical content, measured cadence, and exit zero. Public main `8319696` adds a tested, build-scoped native-libusb package path for mixed Intel/ARM Homebrew hosts. Byte layout and packing are explicit. An AVFoundation surface remains deferred. |
| NFR-03 determinism | Pass | Offline tests and known evidence hashes are stable without the camera. |
| NFR-04 observability | Pass | Diagnostics identify stage, transfer tuple, expected/actual lengths, and outcome without credentials. |
| NFR-05 stability | Pass for preview endurance | The 40-minute preview run exceeded the 30-minute target without unrecovered timeout, parser loss, or observed memory growth. |
| NFR-06 resource use | Pass for the current synchronous reader and both synthetic V4L2 geometries | USB and frame buffers are fixed and bounded. The synchronous CLI applies producer back-pressure rather than an unbounded queue. After warm-up, delayed-consumer bridge-tree RSS growth was zero at preview resolution and 29,504 KiB at full resolution, both below the unchanged 65,536-KiB bound; physical-camera application timing remains a separate gate. |
| NFR-07 reproducibility | Pass | Exact tag `v0.2.0-alpha.7` is published from commit `72f6e63`. Independent main/tag Ubuntu and macOS CI passed; the exact commit passed the complete Raspberry Pi AArch64 suite; and the downloaded tag archive passed outside a Git checkout. Public main `72964bb` adds exact-commit Pi and manifested preview/full-resolution V4L2 lifecycle runs; `8319696` publishes the post-merge physical Mac evidence and scoped libusb discovery; `0ff17a6` publishes Docstack revision 3.9 and the 16-page report. Their hosted CI and Pages deployments pass. |
| NFR-08 legal hygiene | Pass | The public Apache-2.0 repository contains independently developed source and documentation, not vendor drivers, SDK binaries, firmware, or captured proprietary packages. |

## Exit decision

The present release is a useful userspace alpha, but D120 remains open. The
minimum remaining acceptance path is:

1. capture a same-settings blocked-light dark and translated/defocused blank
   flat, then verify a fresh blank and specimen through the settings-bound map;
2. validate Bayer phase/color against a known target;
3. retest the corrected stream through Linux V4L2 and record measured timing;
4. validate a manual focus curve and choose calibrated exposure/gain defaults;
5. retain the recorded Linux-first deferral for AVFoundation, or reopen the
   application-surface portion of D90 if the owner changes scope; and
6. review and accept each row above against the final release commit and hash.

## Publication verification

Public main `0ff17a6` deploys the rendered E-074 record, clickable 1280x960 and
3664x2748 images, Docstack revision 3.9, and the 16-page PDF report. The report
downloaded independently from the project Pages site and Journal of Bjorn is
byte-identical to the locally verified PDF:

```text
f0b51d726294d20b836f6f6b797ce598ef9e18360ea807ee2ea103c5d24e628e  microscope-window-sensor.pdf
```

The public full-resolution JPEG likewise matches its retained derivative:

```text
49c4d0403e69af2906f341598d8f0070eea1edea7e511246633fdd9ff9043e64  current-main-mode0-optical.jpg
```
