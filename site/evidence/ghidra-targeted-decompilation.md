# Targeted Ghidra decompilation of the TCA software stack

Static analysis performed 2026-09-29. No analyzed Windows binary was executed,
no driver was loaded, and this work sent no USB request to the camera.

## Tool provenance and reproducibility

Ghidra 12.1.4 was downloaded from the
[official NSA release](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build),
whose page and published checksum were verified accessible on 2026-09-29. The
archive remained inside the project and its SHA-256 matched the release value:

```text
ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db  work/ghidra/downloads/ghidra_12.1.4_PUBLIC_20260921.zip
```

The distribution identifies itself as version 12.1.4, public build
2026-09-21. Because the release archive does not ship a macOS x86-64
decompiler binary, `./gradlew buildNatives` was run with JDK 21 and a
project-local Gradle cache at `work/ghidra/gradle-home`. The build completed
successfully. Headless imports and decompilation used the two checked-in helper
scripts:

```text
263bc6e5a8f32c7f459621eb1d3ed433ae331c3539354ae81577d0c7fc5f6370  tools/ghidra/DecompileTargets.java
1b6d2749eda33afc5d05e539a60f386891dbd291862583ae0ac5cffed5a45e9e  tools/ghidra/ListFunctions.java
```

The imported binaries were the purchase-era application DLL and its matching
2011 x86-64 KMDF driver:

```text
ee9c8ec6a680404c375a6bf0c44ded0486c6e7557cdee379a5f332eb9a8d12ac  work/vendor-extracted/tsview7/inno/app/TS1000.dll
01c8fdc3b34c0d13cf67c550968d7ae0236e633cb66154a67c04bd10e9326987  work/vendor-extracted/tca/app/tucsen64.sys
```

The persistent headless projects are `work/ghidra/projects/microscope-tca-ghidra`
and `work/ghidra/projects/microscope-tca-driver`. Generated decompiler outputs
are under `work/analysis/ghidra/`; their hashes are recorded in
`evidence/hashes.sha256`.

## Application-side control ABI

The decompiler independently confirms the ten-byte command record already
recovered from disassembly and emulation. `TS1000.dll` always calls
`DeviceIoControl(..., 0x222059, record, 10, response, response_length, ...)`.
The matching driver reads:

| Record offset | USB setup field |
|---:|---|
| 4 | `bRequest` |
| 6 | `wValue`, little endian |
| 8 | `wIndex`, little endian |

The 2011 driver hard-codes `bmRequestType=0xc0`. In particular:

- `FUN_10008ed0` is the sensor-register write wrapper. It sends request
  `0x0a`, `wValue = data XOR 0x17a0`, `wIndex = register XOR 0x17a0`, asks
  for one byte, and accepts only acknowledgement `0x08`.
- `FUN_10009590` is the sensor-register read wrapper. It sends request
  `0x11`, zero `wValue`, the register address in `wIndex`, asks for three
  bytes, requires byte 2 to equal `0x08`, and interprets bytes 0 and 1 as a
  big-endian 16-bit value.
- `FUN_100087b0` emits request `0x02`, value zero for this camera's observed
  product-string branch, index `0x000f`, and zero response bytes.
- `FUN_10008810` emits the paired request `0x03`, value zero on close, index
  `0x000e`, and zero response bytes.

These results match `src/tca_protocol.c` exactly; no protocol correction was
needed.

## Driver-side KMDF path

The driver imports KMDF through a function table rather than named functions.
Its package includes `WdfCoInstaller01009.dll`, identifying the KMDF 1.9
generation. The table address corresponding to index 322 is `0x00016c80`, so
the inferred base is `0x00016270`. The USB-region indices and call signatures
agree with Microsoft's current
[official KMDF function enumeration](https://github.com/microsoft/Windows-Driver-Frameworks/blob/main/src/publicinc/wdf/kmdf/1.27/wdffuncenum.h),
verified accessible 2026-09-29 and preserved locally as
`work/ghidra/reference/wdffuncenum-kmdf-1.27.h`.

| Driver slot | Index | Resolved KMDF call | Observed purpose |
|---:|---:|---|---|
| `0x16c80` | 322 | `WdfUsbTargetDeviceCreate` | Create USB target in prepare-hardware |
| `0x16c88` | 323 | `WdfUsbTargetDeviceRetrieveInformation` | Read USB capability information |
| `0x16c90` | 324 | `WdfUsbTargetDeviceGetDeviceDescriptor` | Cache device descriptor |
| `0x16c98` | 325 | `WdfUsbTargetDeviceRetrieveConfigDescriptor` | Two-pass configuration descriptor retrieval |
| `0x16cb8` | 329 | `WdfUsbTargetDeviceGetNumInterfaces` | Validate interface count |
| `0x16cc0` | 330 | `WdfUsbTargetDeviceSelectConfig` | Select the single-interface configuration |
| `0x16cd8` | 333 | `WdfUsbTargetDeviceSendControlTransferSynchronously` | Submit IOCTL `0x222059` as endpoint-zero control transfer |
| `0x16ce8` | 335 | `WdfUsbTargetDeviceIsConnectedSynchronous` | First half of IOCTL `0x220004` recovery path |
| `0x16cf0` | 336 | `WdfUsbTargetDeviceResetPortSynchronously` | Second half of IOCTL `0x220004` recovery path |
| `0x16d18` | 341 | `WdfUsbTargetPipeGetInformation` | Classify selected pipe |
| `0x16d38` | 345 | `WdfUsbTargetPipeSetNoMaximumPacketSizeCheck` | Allow large application reads |
| `0x16d78` | 353 | `WdfUsbTargetPipeResetSynchronously` | Reset a selected pipe |
| `0x16d90` | 356 | `WdfUsbTargetPipeFormatRequestForUrb` | Format split bulk requests |
| `0x16dd8` | 365 | `WdfUsbInterfaceGetConfiguredPipe` | Select pipe by index |
| `0x16de0` | 366 | `WdfUsbTargetPipeWdmGetPipeHandle` | Populate each bulk URB |

`FUN_00019008`, the device-add path, creates the device and request queues.
`FUN_0001953c`, its prepare-hardware callback, creates the USB target, obtains
the device and configuration descriptors, selects one configuration, and
records the configured-interface handle and pipe count. There is no separate
firmware-loader call in this path.

The read path accepts bulk or interrupt IN pipes, splits large application
reads into at most `0x80000`-byte URBs, and supports multiple outstanding
requests. This is consistent with TSView's four-lane overlapped reader and with
the successful direct 640-by-480 bulk capture.

## IOCTL consequence

The decompiled `FUN_00019988` dispatches only `0x220000`, `0x220004`,
`0x220008`, and `0x222059`. It does not dispatch the DLL's `0x22208a` call.
That call therefore cannot conceal a USB control transaction in this matched
driver; its failure is ignored by the application. Conversely, IOCTL
`0x220004` performs a connectivity check and port reset, but the TSView open
sequence does not call it.

## What this proves and what remains open

The Ghidra lane raises confidence in the existing portable protocol, geometry,
and bulk scheduler. It also narrows the cold-start gap: the Windows driver
performs ordinary KMDF enumeration/configuration before the application's
first request and contains no discovered firmware upload in that path.

It does **not** explain why the exact `c0 02 0000 000f` request stalls from a
physical-cold Linux session. The next evidence gate remains a successful
Windows initialization observed below the forwarding layer. Static output is
not authorization to add or transmit speculative requests.

