# Physical cable reconnect acceptance harness

Prepared: 2026-10-03

Status: staged and inert-tested; physical disconnect/reconnect not yet run.

`tools/run_alpha3_reconnect_acceptance.sh` turns the remaining D100 cable test
into a bounded, evidence-producing interaction. Without arguments it prints a
dry run and performs no USB transfer and no wait. Static/inert tests pass.

The execution path requires:

- exactly one enumerated USB `0547:c003` before starting;
- exact release commit `3c16d2ae560ae0668033b70c42ce881d78197959`;
- the exact opt-in token printed by the dry run;
- observation of camera count zero before accepting a re-enumeration; and
- an existing, explicitly supplied evidence parent.

After the physical reconnect it runs only alpha-3's documented mode-2 startup,
gain 20, 100-ms exposure, and three-frame capture. It requires the exact
1,229,312-byte untouched device frame, 3,686,400 Bayer bytes, and
`frames=3 status=ok`; it then analyzes the first frame and hashes the evidence
directory. It contains no reset, deauthorization, configuration change,
firmware operation, or arbitrary control surface.

The harness was copied to:

```text
/home/rmz/tca-reconnect-harness/run_alpha3_reconnect_acceptance.sh
```

on `rpios-17`, with release worktree
`/home/rmz/tucsen-tca-camera-alpha3-3c16d2a` and existing evidence parent
`/home/rmz/tca-reconnect-evidence`. Its Pi-side SHA-256 is:

```text
64320a0050a7a900975d69efca4447e76f2b50c1bf6163e58e75910a52fc06c8
```

The Pi dry run confirmed the exact commit and reported `transfer=none`; the
camera remained present as `Bus 003 Device 002: ID 0547:c003`. The active wait
has deliberately not been started because it requires the camera owner to be
ready to unplug and reconnect the camera USB cable while leaving the Pi
powered.
