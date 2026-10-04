# Public release live validation

Validated on 2026-10-03 against the physical AmScope/Tucsen camera attached to
Raspberry Pi host `rpios-17`.

## Exact source under test

- Repository: <https://github.com/la3lma/tucsen-tca-camera>
- Commit: `607d1dcd2b678583e181fffc3fc923adb86c81dd`
- Release lineage: `v0.1.0-alpha.1`, plus the README link to the forthcoming
  Journal of Bjørn report
- Pi checkout: `/home/rmz/tucsen-tca-camera-public`
- The tracked worktree and index both matched the commit. Build products and
  validation outputs were untracked.

The native `make test` suite passed before physical capture. The test host was
ARM64 Linux 6.18.39+rpt-rpi-2712 with GCC 14.2.0 and libusb 1.0.28. The device
enumerated as `0547:c003 Anchor Chips, Inc. 10MP CMOS Camera`.

## Controlled 30-frame smoke test

The exact public binary ran:

```text
tca-camera capture --frames 30 --exposure-ms 400 --gain 20
```

It completed 30 frames in 16 seconds with exit status zero. All seven startup
commands and both optional control writes produced the trace-confirmed
`LIBUSB_ERROR_PIPE` data-stage result. The final diagnostic was
`frames=30 status=ok`.

- untouched first device frame SHA-256:
  `de70bb774c3b276fd3c9af897afe42f34336c16f71044c37b045886576d21954`
- 30-frame Bayer stream SHA-256:
  `c672509091c69fa77041847423043cb0fc9b7ef4ed09a2b3e4e2877c035ce205`

The compact log, result, hash file, and first raw frame are preserved inside
the project at
`work/public-release-validation-20261003/public-smoke-20261003T180609Z/`.
The disposable 36,864,000-byte Bayer stream was hash-recorded on the Pi rather
than downloaded.

## Process-level reopen test

Ten separate invocations each opened, initialized, captured ten frames, and
closed the camera. All ten completed with `frames=10 status=ok`: 100 frames in
26 seconds with no failed open, initialization, capture, marker validation, or
close. The ten untouched first-frame hashes are preserved in
`work/public-release-validation-20261003/reopen-10x10-20261003T180638Z/sha256.txt`.

This is evidence for process-level release/reopen, not for a physical USB
disconnect or Pi reboot. Those fault cases remain distinct acceptance tests.

## Endurance run

A 14,400-frame continuous run at 100-ms exposure and normalized gain 20 was
started at `2026-10-03T18:07:21Z` and completed after 2,410 seconds. Bayer
output was discarded to avoid turning the test into a storage benchmark. The
reader exited zero with `frames=14400 status=ok`; sampled resident memory
remained 4,784 KiB throughout the run. The complete 1,229,312-byte untouched
first frame has SHA-256
`49562e8cebd975f9fbbb6a9f455191fbdf22d27abdfc32fd4dc05485fa7a0020`.

The compact raw frame, diagnostics, timing, result, and hash files are
preserved at
`work/public-release-validation-20261003/endurance-14400-20261003T180721Z/`.

## Evidence-flush hardening

Commit `c1ac14714c1ea91291c3800777114022f3f06d29` immediately flushes the
first untouched device frame after its complete write. During a 100-frame
physical run, the evidence file was already the full 1,229,312 bytes while the
reader process was still active. The reader subsequently completed 100/100
frames with exit zero. Evidence is preserved under
`work/public-release-validation-20261003/raw-flush-live-20261003T205000Z/`.

## Public full-resolution reader candidate

After the separately guarded mode-0 probe succeeded, source SHA-256
`b909ca28564139a3bf328f7a62b7fcd873ed4fe99629316a3134e88f2cc85f93`
promoted the verified profile behind explicit option `--mode 0`. It captured
three consecutive 3664-by-2748 frames and then three default 1280-by-960
frames. Both processes exited zero; the Bayer outputs were exactly 30,206,016
and 3,686,400 bytes respectively. The corresponding first-frame hashes are:

```text
acf22fc301fdd98687c7821c370ade1fa8bdd414ff927c96ee191348ff96503c  mode 0
b60ee147a7fd0de2634bb6a54807e00b17a49baf01140ccbd0d4f6cc6feb26d2  mode 2
```

That source and its validation documentation became public commit
`f35dad144d9333fc5692a31d3d310ec285a705ea`. Compact evidence is preserved
under `work/public-release-validation-20261003/mode-option-live-20261003T205300Z/`.

Finally, the Pi fast-forwarded to exact tag `v0.2.0-alpha.1` at that commit,
rebuilt, and passed `make test`. One tagged capture in each mode exited zero
with exact raw/application lengths: 10,068,992/10,068,672 bytes for mode 0 and
1,229,312/1,228,800 bytes for mode 2. Hashes and compact artifacts are under
`work/public-release-validation-20261003/release-v0.2.0-alpha.1-live-20261003T210000Z/`.

## Abrupt process death and reopen

The exact tagged mode-2 reader was observed active with a complete
1,229,312-byte first raw frame, then terminated with `SIGKILL`. The shell
recorded expected status 137. Without a device reset or power cycle, a new
tagged process immediately captured three mode-2 frames with exit zero and
`frames=3 status=ok`. Compact evidence is under
`work/public-release-validation-20261003/process-kill-recovery-v0.2.0-alpha.1-20261003T210200Z/`.

## Host reboot and cold reopen

The Pi checkout was fast-forwarded without tracked modifications to public
commit `71fdae1d93afe0d2cfc06a7fc3d850d0bef8c12e`, rebuilt, and passed its
native static/inert reader and V4L2 tests. With the camera connected and no
reader or bridge process active, the host was rebooted once. Its Linux boot ID
changed from `d588bee0-fe1b-4dc4-a2ba-eea7b3803168` to
`77a640be-2c3b-43ce-bdeb-c1fd06bbd181`, establishing a real host restart rather
than an SSH reconnect.

After the system reached `running`, the camera appeared as a fresh USB instance
on bus 003, device 002 with the unchanged identity `0547:c003`. The rebuilt
public reader then cold-opened it, issued the seven trace-confirmed startup
controls, applied normalized gain 20 and 100-ms exposure, and captured three
mode-2 frames. It exited zero with `frames=3 status=ok`; the files had the exact
expected sizes:

```text
1,229,312  first untouched device frame
3,686,400  three application Bayer frames
```

Their SHA-256 hashes are:

```text
b30eccf5fd2e1a220c5657bf37a63ed987658fa63c2e80415f257b3f747456af  first device frame
a35f96f7beb6c4184433aaf391aaf9940d72800961a3d57e2fab0157e0247bf0  three Bayer frames
```

The project-local bundle is retained at
`work/public-release-validation-20261003/reboot-recovery-20261003T213606Z/`.
This verifies connected-camera host-reboot recovery. Physical cable
disconnect/reconnect remains a separate hands-on test.

## Alpha-2 hand-back hardening and exact-tag capture

Physical Apple Silicon capture through the Pi relay exposed one
marker-invalid initial warm-up frame when ownership returned to Linux. Public
commit `6fa708f08edc34f826076a6a5802c01eccec0bbb` adds a two-frame maximum
initial resynchronization window while retaining fatal marker handling after
frame delivery starts. The reproduced hand-back discarded exactly one invalid
warm-up frame, captured three valid frames in the same Pi process, preserved
exactly one untouched raw frame, and exited zero. Full details are in
`evidence/macos-virtualhere-live-validation.md`.

GitHub CI passed that commit on Ubuntu and macOS. Tag `v0.2.0-alpha.2` was then
pushed. A fresh detached Pi worktree checked out that exact tag, rebuilt,
passed `make test`, and cold-captured three mode-2 frames with exit zero:

```text
22968a3acce34a6fd2d003e8d7d501ccedfdf7b9b1e24c0ce682bc6efd18085d  first device frame
546e5c74a3f243abbcb6c1b9e2356f733f0fcae0919407f98a31fc49fb9ed40c  three Bayer frames
```

The exact-tag bundle is retained at
`work/public-release-validation-20261003/tagged-live-20261003T2005Z/`.
