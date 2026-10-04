# TSView7 TCA startup validation path

Static inspection date: 2026-09-27

Binary: `work/vendor-extracted/tsview7/inno/app/TS1000.dll`

SHA-256:
`ee9c8ec6a680404c375a6bf0c44ded0486c6e7557cdee379a5f332eb9a8d12ac`

No vendor executable was run and this analysis sent no USB traffic.

## Corrected startup control flow

The product-open path beginning near `0x10008e3d` does the following:

1. Calls the wrapper at `0x100087b0`, which issues the `0xc0/0x02` request to
   index `0x000f` with a zero-length data stage.
2. Does **not** test that wrapper's return value.
3. Calls `DeviceIoControl(0x22208a)` through the wrapper at `0x10008bc0` and
   does not test that result either. The recovered 2011 TCA driver dispatch
   does not implement this IOCTL, so it is not evidence of a missing USB
   transaction.
4. Calls `0x10009720` and tests its return value.
5. On validation failure, sleeps 100 ms and calls `0x10008eb0`, which performs
   a paired open/state command and close/state command.

This corrects the earlier experimental assumption that a timeout from the
zero-length `0x02` command should terminate the reconstruction. The vendor DLL
continues into register validation even when that wrapper reports failure.
That fact does not authorize blindly continuing on Linux: it defines the next
trace question and the exact behavior a future bounded fixture must model.

## Register validation

The routine at `0x10009720` constructs a 160-byte constant table, then reads
80 even-numbered registers from `0x0000` through `0x009e` using the
`0xc0/0x11` three-byte register-read wrapper at `0x10009590`. Each returned
16-bit value is assembled from the first two bytes in big-endian order; the
third byte must be acknowledgement `0x08`. The routine stops at the first
failed transfer, bad acknowledgement, or value mismatch.

The register address is placed in `wIndex`; `wValue` is zero for these reads.
This follows directly from the wrapper's input-record offset 8 and the 2011
driver's mapping of record offset 8 to `wIndex`. An earlier probe revision
reversed these fields, so its timeout is not evidence against the register-read
primitive.

The complete signature can be reproduced from the preserved disassembly with:

```sh
python3 tools/extract_tca_signature.py
```

The extractor is offline-only and rejects incomplete tables. Its output has
80 rows and ends with register `0x009e` expected value `0x01d0`.

## Consequence for D40

The current Linux trial stopped earlier than the vendor startup path because
the opt-in probe treated the open timeout as fatal. After a verified device
power or port cycle, the next experiment should distinguish these hypotheses
without guessing request fields:

- the camera accepts `0x02` only from a genuinely cold state;
- Windows records the zero-length transfer differently from libusb while the
  subsequent `0x11` reads still work; or
- the attached camera implements the alternate IS1000 lineage despite its
  purchase-era and physical TCA evidence.

A Windows USB trace remains the strongest discriminator if a cold Linux
attempt cannot obtain the first register response.
