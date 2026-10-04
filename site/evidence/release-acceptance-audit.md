# Release acceptance audit

Date: 2026-10-04

Scope: public Linux-first prerelease `v0.2.0-alpha.7` plus post-release
producer timing, physical-acceptance preparation, and camera-free V4L2
lifecycle candidate `eb8acd3`, including optically validated record-boundary
assembly, gain, motion, white-balance, calibrated-field tooling, and measured
direct-reader cadence.

This is a readiness audit, not owner acceptance. It distinguishes a useful
Linux alpha from completion of every item in the Docstack Definition of Done.

## Definition of Done

| Item | Status | Evidence and remaining work |
|---|---|---|
| 1. Still acquisition | Pass for spatial capture; color calibration partial | Correct record assembly produces coherent 1280x960 and complete 3664x2748 Bayer rasters. Three consecutive full-resolution frames have distinct hashes and no left strip. Multi-resolution PNGs are verified. A 10x configuration produced unclipped preview and full-resolution stills at 250 ms/gain 0 after a bounded sweep. Final Bayer phase and known-target color response remain open. |
| 2. Streaming | Pass for userspace stream; physical Linux application retest partial | A corrected 16-frame run produced 16 distinct coherent frames and an H.264 proof clip. Earlier 14,400-frame testing establishes USB/process endurance but used the superseded multi-request image assembly. Post-release main preserves the V4L2 bridge's producer sidecar; candidate `eb8acd3` passed camera-free detach/reattach and a deliberately slow consumer with bounded RSS, but the post-fix physical Linux consumer cadence/drop comparison remains open. |
| 3. Operation | Partial | Cold start, mode 0/mode 2 selection, start/stop lifecycle, exposure, and analog gain are bounded. A 100-ms optical sweep verified monotonic gain 0..320, and one stale pre-control record is now discarded before frame zero. Neutral-background white-balance estimation is verified. Flat-field maps bind exposure/gain and the V4L2 path fails before camera or loopback mutation on mismatch; true blocked-light dark and blank-field calibration remain open. Automatic exposure and continuously adaptive color correction are explicit non-goals for this bounded alpha rather than hidden acceptance gates. |
| 4. Reader API | Pass | Portable C17 userspace core and CLI provide deterministic raw/Bayer capture, structured diagnostics, bounded controls, dry-run output, and no arbitrary USB request surface. Ubuntu and macOS CI pass. |
| 5. Application path | Partial; software lifecycle verified, physical corrected run open | FFmpeg creates coherent stills and H.264 from the corrected macOS reader. The Linux V4L2 adapter consumes reader stdout; candidate `eb8acd3` exercised the real bridge with a USB-inert reader, normal consumer detach, slow-consumer reattach, only 1,184 KiB RSS growth, deterministic TERM status, and complete loopback cleanup. Commit `470b3d9` packages the remaining bounded live-camera run, cleanup, reopen, and manifest. The earlier physical proof predates the assembly correction. AVFoundation remains deferred. |
| 6. Evidence and recovery | Pass for process/host recovery; physical reconnect open | Protocol notes, hashes, safety boundaries, tests, process-kill recovery, repeated reopen, endurance, host reboot, ownership hand-back, microscope-mounted capture, and a clearly labeled physical-size self-flat diagnostic are recorded. The diagnostic proves correction plumbing while explicitly rejecting its scene-erasing output as optical calibration. The inert physical disconnect/reconnect harness is prepared but has not run. |

## Non-functional requirements

| Requirement | Status | Evidence and remaining work |
|---|---|---|
| NFR-01 safety | Pass | Live behavior is opt-in, bounded, and based on trace-confirmed tuples; no reset, firmware upload, non-volatile write, arbitrary control request, or kernel camera driver is exposed. |
| NFR-02 portability | Pass for the direct reader API | The core builds and tests on AArch64 Linux and Apple Silicon macOS. The exact-tag Apple Silicon binary captured the physical camera directly in both supported modes with exact frame sizes and exit zero, then reopened preview in a fresh process. Byte layout and packing are explicit. An AVFoundation surface remains deferred. |
| NFR-03 determinism | Pass | Offline tests and known evidence hashes are stable without the camera. |
| NFR-04 observability | Pass | Diagnostics identify stage, transfer tuple, expected/actual lengths, and outcome without credentials. |
| NFR-05 stability | Pass for preview endurance | The 40-minute preview run exceeded the 30-minute target without unrecovered timeout, parser loss, or observed memory growth. |
| NFR-06 resource use | Pass for the current synchronous reader and synthetic V4L2 lifecycle | USB and frame buffers are fixed and bounded. The synchronous CLI applies producer back-pressure rather than an unbounded queue. During a deliberately slow eight-frame V4L2 consumer, the complete bridge process tree grew by only 1,184 KiB and remained live; physical-camera application timing remains a separate gate. |
| NFR-07 reproducibility | Pass | Exact tag `v0.2.0-alpha.7` is published from commit `72f6e63`. Independent main/tag Ubuntu and macOS CI passed; the exact commit passed the complete Raspberry Pi AArch64 suite; and the downloaded tag archive passed the suite outside a Git checkout. Post-release commits `a60ecac` and `470b3d9` pass Apple Silicon, Raspberry Pi AArch64, Ubuntu, and macOS suites. Candidate `eb8acd3` adds an exact-commit Pi suite and manifested camera-free lifecycle run plus successful Ubuntu/macOS CI. |
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
