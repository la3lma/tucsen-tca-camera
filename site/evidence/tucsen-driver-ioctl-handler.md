# Tucsen KMDF control-handler analysis

Static inspection performed 2026-09-27. Neither driver was loaded, no Windows
executable was run, and no request was sent to the camera.

## Analyzed binaries

| File | Architecture | SHA-256 |
|---|---|---|
| `work/vendor-extracted/tca/app/tucsen.sys` | 2011, 32-bit x86 | `bcdc650eed43d339e4a40318d34883194791df1a2f580a2a18f3eab7c4fc979c` |
| `work/vendor-extracted/tca/app/tucsen64.sys` | 2011, x86-64 | `01c8fdc3b34c0d13cf67c550968d7ae0236e633cb66154a67c04bd10e9326987` |
| `work/vendor-extracted/beta/app/tucsen.sys` | 2013, 32-bit x86 | `f93ab23ffe9591a6b5f3d1f1f65c938061cf5c6a4d253205e966310a09a4ffee` |
| `work/vendor-extracted/beta/app/tucsen64.sys` | 2013, x86-64 | `588d622176d212a8fb3cba821f4f6770f6bf2de3ab1576f6b79f9f616c99bb3a` |

The 2011 pair are KMDF drivers built in September 2010 from a project whose
embedded PDB path ends in `ncusb.pdb`. The INF binds both `0547:c003` and
`0828:c003` and names the device `Tucsen TCA-10.0-N Camera`.

The 2013 INF labels `0547:c003` as `IS1000 USB Camera`; this package is the
generation matched to the inspected 2012 `TS1000.dll`. Its two driver builds
implement a materially different setup-packet mapping, discovered after the
first Linux trials with the 2011 mapping stalled.

## IOCTL dispatch

The `EvtIoDeviceControl`-shaped routines begin at preferred-image addresses
`0x00016998` in the x86 driver and `0x00019988` in the x86-64 driver. Both use
the same subtraction chain to dispatch four control codes:

```text
0x220000
0x220004
0x220008
0x222059
```

The final branch is reached by subtracting `0x220000`, then `4`, then `4`, and
finally comparing/subtracting `0x2051`. This independently confirms that the
user-mode DLL's sole `DeviceIoControl` wrapper reaches the `0x222059` branch.

## 2011 setup-packet construction

The `0x222059` branch is at `0x00016a1a` (x86) and `0x00019a27` (x86-64).
The two compiler outputs agree on the following behavior:

1. Obtain the ten-byte input record and the caller's direct-I/O response
   buffer.
2. Zero-initialize an eight-byte `WDF_USB_CONTROL_SETUP_PACKET`.
3. Set the setup packet's first byte to `0xc0`.
4. Copy input-record byte offset 4 to `bRequest`.
5. Copy the little-endian 16-bit value at offset 6 to `wValue`.
6. Copy the little-endian 16-bit value at offset 8 to `wIndex`.
7. Submit a synchronous USB control transfer and complete the WDF request with
   the resulting status and transferred-byte count.

The decisive x86 instructions are:

```text
movzx ecx, word ptr [esi + 0x8]  ; wIndex
movzx edx, word ptr [esi + 0x6]  ; wValue
mov   bl,  byte ptr [esi + 0x4]  ; bRequest
...
and   al, 0x1c
or    al, 0xc0
...
mov   byte ptr [setup + 1], bl
mov   word ptr [setup + 2], dx
mov   word ptr [setup + 4], cx
```

The x86-64 routine performs the same loads from offsets 8, 6, and 4 and the
same `and al,0x1c; or al,0xc0` construction. The resulting byte has direction
device-to-host, vendor type, and device recipient. It is therefore exactly the
libusb request type `LIBUSB_ENDPOINT_IN | LIBUSB_REQUEST_TYPE_VENDOR |
LIBUSB_RECIPIENT_DEVICE`, or `0xc0`.

The first four bytes of the record are not consulted by this older handler.
The driver does not derive direction, type, or recipient from them;
it hard-codes all three properties. The earlier `0xc0` interpretation is now a
confirmed static result for the **2011 driver only**, not an inference.

## 2013 setup-packet construction

The later x86 and x86-64 handlers agree with each other but not with the 2011
pair. For IOCTL `0x222059`, they:

1. read record byte 0 as a direction flag;
2. shift its low bit into setup-packet bit 7;
3. set the vendor-type bits with `OR 0x40`;
4. copy record byte 4 to `bRequest`;
5. copy record words at offsets 6 and 8 to `wValue` and `wIndex`.

The decisive x86 sequence at `0x1709a`–`0x170dc` includes:

```text
mov   al, byte ptr [esi + 0x4]  ; request
movzx ecx, byte ptr [esi]       ; direction flag
movzx edx, word ptr [esi + 0x8] ; index
movzx ebx, word ptr [esi + 0x6] ; value
...
and   al, 0x1c
shl   cl, 0x7
or    al, cl
or    al, 0x40
```

The x86-64 sequence at `0x1a2f9`–`0x1a352` performs the same operation.
`TS1000.dll` initializes its wrapper record as direction `0`, type `2`,
recipient `0`, then places the request at byte 4. With the matched 2013 driver,
that record therefore produces `bmRequestType = 0x40`: host-to-device, vendor,
device. The DLL zero-initializes its ten-byte transfer buffers, so commands
whose record length is ten send ten zero bytes; they do not read a ten-byte
response.

## Equivalent libusb shape for the matched 2013 pair

For an eight-byte DLL record laid out as `request, pad, value, index, length`,
the corresponding operation is now known to have this shape:

```c
libusb_control_transfer(handle,
                        0x40,
                        record.request,
                        record.value,
                        record.index,
                        zero_filled_command,
                        record.length,
                        timeout_ms);
```

This is a protocol mapping, not authorization to transmit every embedded
request. Request `0xb3` remains especially unsuitable for an initial trial
because the DLL invokes it immediately before bulk capture and requests no data
stage.

## Live falsification of the older mapping

On 2026-09-27, bounded Linux trials using the 2011 `0xc0` interpretation sent
`b4/c4`, `b4/c0`, `bb/0`, and `ba/0`. Every operation returned
`LIBUSB_ERROR_PIPE` before a data stage. Each trial was followed by successful
descriptor reads and interface claim/release, and the device remained at the
same bus address. These failures are consistent with using the wrong direction
for the 2013 DLL/driver generation and prompted the cross-generation audit.

A subsequent bounded trial used that corrected `0x40` mapping and still
returned `LIBUSB_ERROR_PIPE`, with a healthy post-check. Recovery of the
official TSView7 package then showed that the purchase-era TCA lineage uses a
different request family entirely. Further live work follows
`tsview7-tca-protocol-map.md`; the `b3`–`be` family is retained as later-
generation evidence, not as the next experiment.
