# TS1000.dll static protocol map

Static inspection performed 2026-09-27. No extracted executable was run and no
vendor-specific request was sent to the camera.

## Binary and method

- File: `work/vendor-extracted/iscapture/app/TS1000.dll`
- SHA-256: `8262ee4723bb5df0f680b04b1d3a4562525bf7139e414aa263195c9db2cb357f`
- Format: 32-bit x86 Windows DLL, linked in December 2012
- Method: LLVM PE headers, import-table inspection, Intel-syntax disassembly,
  call-site tracing, and direct inspection of initialized data

Addresses below use the DLL's preferred image base `0x10000000`. Names for
non-exported routines are descriptive analysis labels, not original symbols.

## Windows transport split

The DLL enumerates a SetupAPI device-interface GUID whose bytes decode to
`{00873fdf-61a8-11d1-aa5e-00c04fb1728b}`. It opens a control handle and a
second path formed with the literal suffix `PIPE00`. `ReadFile` is used on the
pipe handle, while `DeviceIoControl` is used on the control handle. This
supports the earlier inference that the kernel driver exposes a thin control
channel plus a read pipe corresponding to the camera's sole bulk-IN endpoint.

The relevant import address table entries and observed call sites are:

| API | IAT address | Direct call sites |
|---|---:|---|
| `DeviceIoControl` | `0x100351ec` | one, `0x1001c552` |
| `CreateFileA` | `0x10035210` | device/pipe open helpers |
| `ReadFile` | `0x1003522c` | pipe and unrelated file helpers; camera wrapper at `0x1001c4ba` |
| `WriteFile` | `0x10035228` | unrelated file helpers; no demonstrated camera write path |

## Control-transfer wrapper

The only direct `DeviceIoControl` call is in the routine beginning at
`0x1001c4e0`. It always uses IOCTL `0x222059`, decoded as Windows device type
`0x22`, function `0x816`, `METHOD_IN_DIRECT`, and unrestricted access bits.
The routine supplies a ten-byte input record and a caller-provided output
buffer.

The record construction is consistent with these logical fields:

| Logical field | Observed value |
|---|---|
| direction | `0` |
| request type | `2` (vendor) |
| recipient | `0` (device) |
| request | caller-supplied byte |
| value | caller-supplied 16-bit value |
| index | caller-supplied 16-bit value |

Both generations of the driver's IOCTL handler have now been inspected in x86
and x86-64 builds. The 2011 TCA driver ignores the record's first four bytes and
hard-codes `bmRequestType` to `0xc0`. The matched 2013 IS1000 driver instead
uses record byte 0 as the direction bit and sets vendor/device type; the DLL
sets that byte to zero, producing `bmRequestType=0x40`. Both generations copy
record offsets 4, 6, and 8 to `bRequest`, `wValue`, and `wIndex`. Exact
addresses and the cross-architecture instruction trace are preserved in
`evidence/tucsen-driver-ioctl-handler.md`.

## Embedded request records

The DLL contains eight-byte records laid out as request byte, padding, 16-bit
value, 16-bit index, and 16-bit data-stage length. It sets the length to ten
bytes immediately before most calls. In the matched 2013 transport these are
zero-filled OUT command payloads, not responses. Observed request bytes include:

```text
b3 b4 b5 b6 b7 b8 ba bb bd be
```

Observed parameter families include:

```text
b4 value=c0..c4
b5 value=a0..a4
b8 value=60..62
b7 index=305e
b7 index=3012
```

These are facts about the DLL's records; the semantic names of the requests
are not yet known.

## Capture path

The capture routine computes its planned `ReadFile` size at
`0x1001aa51`--`0x1001aa5d` as:

```text
pixel_bytes = width * height
read_bytes = ((pixel_bytes >> 9) + 1) << 9
```

This selects the next 512-byte boundary, including one additional packet when
the pixel count is already aligned, matching endpoint `0x82`'s high-speed bulk
maximum packet size. A separate `width * height + 0x200` allocation is buffer
headroom rather than the requested transfer length. The later successful
mode-2 physical trace confirms the formula: 1,228,800 pixel bytes become a
1,229,312-byte device frame.

Immediately before the read loop the routine invokes the control wrapper with
request `0xb3`, zero value, zero index, and zero response length. The routine
then reads from the pipe and searches incoming data for a run of ten `0x88`
bytes or, as an alternative mode marker, ten `0x99` bytes.

This makes `0xb3` a strong candidate for a stream/capture trigger and the
repeated-byte runs candidates for frame synchronization. Those roles remain
inferences and must not yet be encoded as confirmed protocol semantics.

## Next static targets

This DLL belongs to the later ISCapture lineage. Its call order, mode table,
and fixed dry/live fixtures have been preserved, but a bounded matched-`0x40`
trial returned `LIBUSB_ERROR_PIPE`. The official compatibility matrix assigns
the purchase-era TCA-10.0N to TSView6/7, whose distinct protocol is now mapped
in `tsview7-tca-protocol-map.md`. No more ISCapture-family request should be
sent unless later evidence shows the camera actually implements that lineage.
