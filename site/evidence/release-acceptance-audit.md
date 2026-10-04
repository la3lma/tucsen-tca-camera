# Release acceptance audit

Date: 2026-10-04

Scope: public Linux-first prerelease `v0.2.0-alpha.7` plus the post-release
producer-timing preparation at `a60ecac`, including optically validated
record-boundary assembly, gain, motion, white-balance, calibrated-field
tooling, and measured direct-reader cadence.

This is a readiness audit, not owner acceptance. It distinguishes a useful
Linux alpha from completion of every item in the Docstack Definition of Done.

## Definition of Done

| Item | Status | Evidence and remaining work |
|---|---|---|
| 1. Still acquisition | Pass for spatial capture; color calibration partial | Correct record assembly produces coherent 1280x960 and complete 3664x2748 Bayer rasters. Three consecutive full-resolution frames have distinct hashes and no left strip. Multi-resolution PNGs are verified. A 10x configuration produced unclipped preview and full-resolution stills at 250 ms/gain 0 after a bounded sweep. Final Bayer phase and known-target color response remain open. |
| 2. Streaming | Pass for userspace stream; Linux application retest partial | A corrected 16-frame run produced 16 distinct coherent frames and an H.264 proof clip. Earlier 14,400-frame testing establishes USB/process endurance but used the superseded multi-request image assembly. Post-release main now lets the V4L2 bridge preserve the reader's monotonic producer sidecar, but the post-fix physical Linux consumer cadence/drop comparison remains open. |
| 3. Operation | Partial | Cold start, mode 0/mode 2 selection, start/stop lifecycle, exposure, and analog gain are bounded. A 100-ms optical sweep verified monotonic gain 0..320, and one stale pre-control record is now discarded before frame zero. Neutral-background white-balance estimation is verified. Flat-field maps bind exposure/gain and the V4L2 path fails before camera or loopback mutation on mismatch; true blocked-light dark and blank-field calibration remain open. Automatic exposure and continuously adaptive color correction are explicit non-goals for this bounded alpha rather than hidden acceptance gates. |
| 4. Reader API | Pass | Portable C17 userspace core and CLI provide deterministic raw/Bayer capture, structured diagnostics, bounded controls, dry-run output, and no arbitrary USB request surface. Ubuntu and macOS CI pass. |
| 5. Application path | Partial | FFmpeg creates coherent stills and H.264 from the corrected macOS reader. The Linux V4L2 adapter consumes reader stdout; a synthetic corrected-stream preflight delivered six frames through a temporary loopback to a separate consumer. Commit `a60ecac` adds separately recorded producer timestamps, and commit `470b3d9` packages the bounded live-camera Linux run, cleanup, reopen, and manifest as an inert-by-default harness. The earlier physical proof still predates the assembly correction. AVFoundation remains deferred. |
| 6. Evidence and recovery | Pass for process/host recovery; physical reconnect open | Protocol notes, hashes, safety boundaries, tests, process-kill recovery, repeated reopen, endurance, host reboot, ownership hand-back, microscope-mounted capture, and a clearly labeled physical-size self-flat diagnostic are recorded. The diagnostic proves correction plumbing while explicitly rejecting its scene-erasing output as optical calibration. The inert physical disconnect/reconnect harness is prepared but has not run. |

## Non-functional requirements

| Requirement | Status | Evidence and remaining work |
|---|---|---|
| NFR-01 safety | Pass | Live behavior is opt-in, bounded, and based on trace-confirmed tuples; no reset, firmware upload, non-volatile write, arbitrary control request, or kernel camera driver is exposed. |
| NFR-02 portability | Pass for the direct reader API | The core builds and tests on AArch64 Linux and Apple Silicon macOS. The exact-tag Apple Silicon binary captured the physical camera directly in both supported modes with exact frame sizes and exit zero, then reopened preview in a fresh process. Byte layout and packing are explicit. An AVFoundation surface remains deferred. |
| NFR-03 determinism | Pass | Offline tests and known evidence hashes are stable without the camera. |
| NFR-04 observability | Pass | Diagnostics identify stage, transfer tuple, expected/actual lengths, and outcome without credentials. |
| NFR-05 stability | Pass for preview endurance | The 40-minute preview run exceeded the 30-minute target without unrecovered timeout, parser loss, or observed memory growth. |
| NFR-06 resource use | Pass for the current synchronous reader | USB and frame buffers are fixed and bounded. The synchronous CLI applies producer back-pressure rather than an unbounded queue; the optional V4L2 path delegates downstream buffering to FFmpeg and v4l2loopback. |
| NFR-07 reproducibility | Pass | Exact tag `v0.2.0-alpha.7` is published from commit `72f6e63`. Independent main/tag Ubuntu and macOS CI passed; the exact commit passed the complete Raspberry Pi AArch64 suite; and the downloaded tag archive passed the suite outside a Git checkout. Post-release commits `a60ecac` and `470b3d9` independently pass the complete Apple Silicon, Raspberry Pi AArch64, Ubuntu, and macOS suites; the latter also passes its Pi dry-run without a USB transfer. |
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
