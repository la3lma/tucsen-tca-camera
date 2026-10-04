# D40 cold-session evidence harness

Prepared and dry-run on `rpios-17` on 2026-09-27, then executed exactly once
after an owner-confirmed physical USB cold cycle.

`tools/run_tca_cold_probe.sh` wraps only the already reviewed version-2
open/read/close binary. It hard-codes that binary's SHA-256, refuses a mismatch,
and is inert without the exact token that asserts the operator has physically
disconnected camera USB power for at least ten seconds.

On an authorized run the harness:

1. requires exactly one sysfs device with identity `0547:c003`;
2. records UTC and monotonic time, host/kernel identity, `lsusb`, USB topology,
   udev properties, selected sysfs fields, and the kernel log;
3. records the probe's own dry-run profile;
4. runs the descriptor-only claim/release fixture before the vendor probe;
5. invokes the reviewed v2 execution token exactly once and retains separate
   standard output, standard error, and exit status even on timeout;
6. repeats enumeration, descriptor claim/release, and kernel-log capture if the
   camera remains present; and
7. hashes every resulting evidence file.

It does not call reset, set-configuration, bulk I/O, firmware operations, the
initialization planner, or any control plan. The harness source SHA-256 is:

```text
910b11a92bb41753bc106d5789ef9ba9504eb0a79933a5baa271214cd9826f0d  tools/run_tca_cold_probe.sh
```

The staged copy is
`/home/rmz/microscope-window-sensor-probe/v2/run_tca_cold_probe.sh`. Its Pi dry
run verified the embedded probe hash
`612d50fa3daf99b22a90e8de8afdd76a91f2e4e8936c7f49dffe840e218ccb1a`
and printed the corrected fixed tuple:

```text
c0 02 0000 000f length=0
c0 11 0000 3ff0 length=3 expected-ack=08
c0 03 0000 000e length=0
```

The dry run ended with `NO TRANSFER SENT`. After the camera was physically
disconnected for more than ten seconds and re-enumerated at a new USB address,
the authorized run captured one live result. Open, the corrected register
read, and close each returned `LIBUSB_ERROR_TIMEOUT`; the before/after safe
descriptor and claim/release probes both passed, the device records were
byte-identical, and no kernel USB fault appeared. The result and hashes are
recorded in [D40 physical-cold probe result](d40-cold-result.md). The harness
must not be executed again for request variation.
