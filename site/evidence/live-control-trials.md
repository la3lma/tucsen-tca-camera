# Bounded Linux control-transfer trials

Trials were performed on 2026-09-27 against the Raspberry Pi-attached camera
`0547:c003`. Every trial used a one-second timeout and was followed by the
descriptor/claim/release health probe. No bulk transfer, USB reset, firmware
operation, or persistent write was performed.

## Superseded ISCapture-lineage attempts

The first five trials were derived from the later ISCapture `TS1000.dll`,
before the matching TSView7 TCA software was recovered:

| Trial | Tuple | Result | Post-check |
|---:|---|---|---|
| 1 | `c0 b4 00c4 0000`, length 10 | `LIBUSB_ERROR_PIPE` | Healthy |
| 2 | `c0 b4 00c0 0000`, length 10 | `LIBUSB_ERROR_PIPE` | Healthy |
| 3 | `c0 bb 0000 0000`, length 10 | `LIBUSB_ERROR_PIPE` | Healthy |
| 4 | `c0 ba 0000 0000`, length 10 | `LIBUSB_ERROR_PIPE` | Healthy |
| 5 | `40 b4 00c0 0000`, ten zero bytes | `LIBUSB_ERROR_PIPE` | Healthy |

The first four tested the 2011 driver's hard-coded IN mapping with a later DLL;
the fifth tested the mapping of the 2013 driver actually paired with that DLL.
The camera remained at the same bus address and the kernel reported no USB
fault. These negative results are retained because they exposed a software-
generation mismatch; they are not candidates for repetition.

## Current experiment boundary

Trial 6 attempted the TSView7 TCA register read as
`c0 11 3ff0 0000`, length 3, expected final byte `08`. It returned
`LIBUSB_ERROR_TIMEOUT` after one second. Later byte-accurate reconstruction of
the DLL's ten-byte IOCTL record corrected the tuple to
`c0 11 0000 3ff0`: register addresses are carried in `wIndex`, while `wValue`
is zero for reads. Trial 6 therefore had those two fields reversed and is not a
valid negative test of the TCA register-read primitive. The immediate
descriptor/claim/release check succeeded, the camera remained at bus 1 address
2, runtime power status remained `active`, and autosuspend remained disabled.

The corrected tuple is encoded in version 2 of both TCA probes. It was later
exercised once in the physical-cold Trial 9 below.

The version-2 sources were cross-built natively on `rpios-17` on 2026-09-27
using the preserved project-local libusb header and the Pi's installed
`libusb-1.0.so.0`. Their AArch64 binary SHA-256 values are:

```text
fd2dd027fccc74c4680b9b3fcd9dcd3f2aeb71d632c5624d855d78ae74d8df9d  tca_register_probe
612d50fa3daf99b22a90e8de8afdd76a91f2e4e8936c7f49dffe840e218ccb1a  tca_open_read_probe
```

Both binaries were run without an execution token and printed the corrected
`wValue=0x0000`, `wIndex=0x3ff0` plan followed by `NO TRANSFER SENT`. A dynamic
symbol audit found `libusb_control_transfer` but no bulk, interrupt, reset, or
set-configuration API. The standard descriptor and claim/release health probe
then passed at bus 1 address 3. The staged binaries remain inert pending a
physical camera USB power cycle.

Trial 7 executed version 1 of that profile. The first operation,
`c0 02 0000 000f` with zero data length, timed out after one second. Because
open did not complete, the tool correctly skipped both the register read and
close. The immediate post-check again succeeded at bus 1 address 2 with
runtime power `active` and autosuspend control `on` (disabled). The Pi binary
SHA-256 was
`0acb31d2ed40fa41667ebbeca07ce5351457ae86c31ecdcaf2f4ab4e9e6982ef`;
its dynamic-symbol audit found `libusb_control_transfer` and none of the bulk,
reset, or set-configuration APIs.

No further request-field variation is justified in the current powered
session. The next physical experiment requires a cold camera power cycle. If
the fixed prefix still times out from cold power, a targeted Windows USB trace
is the preferred discriminator between a missing driver-side state transition,
a transfer-timing quirk, and a protocol-revision mismatch.

## Trial 8: targeted host-port cycle and exact-prefix repeat

The Pi exposes a root-owned disable control for the camera's resolved host
port, `/sys/bus/usb/devices/1-0:1.0/usb1-port2/disable`. Before changing it,
the script verified that `/sys/bus/usb/devices/1-2` was exactly `0547:c003`.
The port was disabled for eight seconds. The device disappeared from sysfs,
then re-enumerated at bus 1 address 3 after the port was enabled. It retained
the same descriptors, and the standard descriptor plus interface
claim/release probe succeeded.

This is evidence of a USB host-port disconnect/re-enumeration, but not proof
that VBUS power was removed; host-port disable semantics do not guarantee a
physical cold-power cycle.

Version 1 of `tca_open_read_probe` was then run once without changing any tuple.
The first operation, `c0 02 0000 000f` with zero data length, again returned
`LIBUSB_ERROR_TIMEOUT` after one second. The tool correctly skipped the read
and close. The immediate health probe succeeded at address 3, with runtime
power `active` and power control `on`.

No additional live vendor request was sent. This repeat rules out stale Linux
USB enumeration state as the simple cause of the open-command timeout. Because
the vendor DLL ignores the `0x02` result and continues, and because the read
tuple is now corrected, the next cold-session fixture may continue to exactly
one `c0 11 0000 3ff0` read after the bounded open timeout. That behavior must
remain explicit and versioned; it is not permission for general request-field
variation.

## Trial 9: physical-cold corrected prefix

The owner physically disconnected camera USB power for more than ten seconds
and reconnected it. The device enumerated as a new USB instance at bus 1
address 4, compared with address 3 before disconnect, while retaining identity
`0547:c003` and the same descriptors.

The pinned version-2 harness then executed the exact open/read/close prefix
once. Open `c0 02 0000 000f`, corrected register read
`c0 11 0000 3ff0` length three, and close `c0 03 0000 000e` each returned
`LIBUSB_ERROR_TIMEOUT` after one second. The read followed the open timeout
because the matching TSView7 DLL ignores the open wrapper result and proceeds
to its register validation.

Before and after the attempt, the safe fixture successfully opened the device,
read descriptors, claimed and released interface 0, and closed it. The device
identity records were byte-identical, the USB inventory did not change, and
the kernel log gained no USB error. The complete hashed record is summarized
in [D40 physical-cold probe result](d40-cold-result.md).

This is the final approved Linux vendor-control variation at D40. The corrected
prefix has now failed from a proven physical cold start without harming the
camera. Further request guessing is unjustified; the next experiment is a
targeted first-attach trace of the recovered TSView7 stack in isolated x86-64
Windows emulation.
