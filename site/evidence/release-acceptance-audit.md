# Release acceptance audit

Date: 2026-10-04

Scope: public Linux-first prerelease `v0.2.0-alpha.6`, including optically
validated record-boundary assembly, gain, motion, and white-balance evidence.

This is a readiness audit, not owner acceptance. It distinguishes a useful
Linux alpha from completion of every item in the Docstack Definition of Done.

## Definition of Done

| Item | Status | Evidence and remaining work |
|---|---|---|
| 1. Still acquisition | Pass for spatial capture; color calibration partial | Correct record assembly produces coherent 1280x960 and complete 3664x2748 Bayer rasters. Three consecutive full-resolution frames have distinct hashes and no left strip. Multi-resolution PNGs are verified. A 10x configuration produced unclipped preview and full-resolution stills at 250 ms/gain 0 after a bounded sweep. Final Bayer phase and known-target color response remain open. |
| 2. Streaming | Pass for userspace stream; Linux application retest partial | A corrected 16-frame run produced 16 distinct coherent frames and an H.264 proof clip. Earlier 14,400-frame testing establishes USB/process endurance but used the superseded multi-request image assembly. Post-fix Linux V4L2 should be retested. |
| 3. Operation | Partial | Cold start, mode 0/mode 2 selection, start/stop lifecycle, exposure, and analog gain are bounded. A 100-ms optical sweep verified monotonic gain 0..320, and one stale pre-control record is now discarded before frame zero. Neutral-background white-balance estimation is verified; automatic exposure and adaptive color correction remain open. |
| 4. Reader API | Pass | Portable C17 userspace core and CLI provide deterministic raw/Bayer capture, structured diagnostics, bounded controls, dry-run output, and no arbitrary USB request surface. Ubuntu and macOS CI pass. |
| 5. Application path | Partial | FFmpeg creates coherent stills and H.264 from the corrected macOS reader. The existing Linux V4L2 adapter consumes reader stdout and requires no structural change, but its earlier live proof predates the assembly correction. AVFoundation remains deferred. |
| 6. Evidence and recovery | Pass for reconnect; ongoing for calibration | Protocol notes, hashes, safety boundaries, tests, process-kill recovery, repeated reopen, endurance, host reboot, ownership hand-back, physical cable reconnect, and microscope-mounted capture are recorded. |

## Non-functional requirements

| Requirement | Status | Evidence and remaining work |
|---|---|---|
| NFR-01 safety | Pass | Live behavior is opt-in, bounded, and based on trace-confirmed tuples; no reset, firmware upload, non-volatile write, arbitrary control request, or kernel camera driver is exposed. |
| NFR-02 portability | Pass for the direct reader API | The core builds and tests on AArch64 Linux and Apple Silicon macOS. The exact-tag Apple Silicon binary captured the physical camera directly in both supported modes with exact frame sizes and exit zero, then reopened preview in a fresh process. Byte layout and packing are explicit. An AVFoundation surface remains deferred. |
| NFR-03 determinism | Pass | Offline tests and known evidence hashes are stable without the camera. |
| NFR-04 observability | Pass | Diagnostics identify stage, transfer tuple, expected/actual lengths, and outcome without credentials. |
| NFR-05 stability | Pass for preview endurance | The 40-minute preview run exceeded the 30-minute target without unrecovered timeout, parser loss, or observed memory growth. |
| NFR-06 resource use | Pass for the current synchronous reader | USB and frame buffers are fixed and bounded. The synchronous CLI applies producer back-pressure rather than an unbounded queue; the optional V4L2 path delegates downstream buffering to FFmpeg and v4l2loopback. |
| NFR-07 reproducibility | Pass | Exact tag `v0.2.0-alpha.6` is published from commit `0fded6e`. Its release binary passed the complete local suite and an exact-size physical preview smoke capture; the unchanged frame assembler passed exact-size physical captures in both modes immediately before release. Prior exact-tag Pi and independent CI evidence remains recorded. |
| NFR-08 legal hygiene | Pass | The public Apache-2.0 repository contains independently developed source and documentation, not vendor drivers, SDK binaries, firmware, or captured proprietary packages. |

## Exit decision

The present release is a useful userspace alpha, but D120 remains open. The
minimum remaining acceptance path is:

1. validate Bayer phase/color against a known target;
2. retest the corrected stream through Linux V4L2 and record measured timing;
3. validate a manual focus curve and choose calibrated exposure/gain defaults;
4. retain the recorded Linux-first deferral for AVFoundation, or reopen the
   application-surface portion of D90 if the owner changes scope; and
5. review and accept each row above against the final release commit and hash.
