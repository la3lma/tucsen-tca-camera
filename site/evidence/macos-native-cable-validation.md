# Native-cable Apple Silicon validation

Date: 2026-10-04

The camera was connected directly to the Apple Silicon workstation rather
than forwarded through the Raspberry Pi. IOKit enumerated exactly one active
`10MP CMOS Camera` at USB address 23 with vendor/product `0547:c003` and a
480,000,000-bit/s link. No Windows guest, VirtualHere relay, kernel camera
driver, USB reset, configuration change, or firmware operation participated.

## Release under test

- public tag: `v0.2.0-alpha.3`
- exact commit: `3c16d2ae560ae0668033b70c42ce881d78197959`
- host: macOS 26.5.2, Darwin 25.5.0, ARM64
- reader binary SHA-256:
  `beaab0264f6fef6c17b304f74d50ca528ba3e46883a10ede28e8331051b4a029`
- libusb: project-local ARM64 1.0.28 build

The exact tag rebuilt from clean generated output and passed the complete
packaged test suite before live use.

## Cold-attach observation

The first reader invocation claimed interface 0. Its first `b4/c2` command
returned the expected `LIBUSB_ERROR_PIPE`; the following `b5/a2` transfer
returned positive length 1 rather than the expected stall or complete ten-byte
response. The release correctly failed closed before frame capture. Its
diagnostic calls `libusb_error_name(1)`, which prints the misleading enum name
`LIBUSB_TRANSFER_ERROR`; for the synchronous libusb API the positive value is
the actual transferred byte count.

A separately compiled, evidence-local probe then sent only the same seven
known startup controls, logged response lengths, and did not relax the public
reader. All seven returned `LIBUSB_ERROR_PIPE`. The unmodified reader then
completed every subsequent run. This is one observed, self-clearing
cold-attach transient. The evidence does not justify accepting arbitrary short
control responses, and the public safety rule remains unchanged.

## Direct-cable captures

The unmodified exact-tag reader applied normalized gain 20 and 100-ms exposure
for each run.

| Run | Result | Untouched device bytes | Bayer bytes |
|---|---|---:|---:|
| Preview | 3 frames, `frames=3 status=ok` | 1,229,312 | 3,686,400 |
| Full resolution | 1 frame, `frames=1 status=ok` | 10,068,992 | 10,068,672 |
| Fresh-process preview reopen | 1 frame, `frames=1 status=ok` | 1,229,312 | 1,228,800 |

Every successful invocation recorded the expected stall for all seven startup
commands and both optional control writes. Mode 0 validated its twenty marker
boundaries; both preview processes validated three per device frame. The
fresh-process mode change back to preview proves that mode 0 did not leave the
directly connected camera unusable.

Captured-payload SHA-256 values:

```text
9e5b7244e95e2924cf640cac4ba4ef7c66a1bb5998ae6d9deb23f1648ed4bc21  preview retry untouched device frame
af771bca314f99f542e77f982f6da494abe054b8d7b4f594d6a9c1f841f0a330  three-frame preview Bayer stream
3b06501ff7889c2a4dd446af38919178130b8b975868324d4bda7f29aa646a78  full-resolution untouched device frame
80bd0f98e4a485bc1fd903e5350581cc70aa804cfb4a639518f0f1c8ba88626a  full-resolution Bayer frame
b5b5ba080d0795907542c7d88e9660e905fedf48d7185ab9a862b1bb0162a015  reopened preview untouched device frame
d5215e655d0a09ec5d91c942b1a7bc7baa6a3149760a48b7c9a0411224a1273c  reopened preview Bayer frame
```

The covered sensor produced the expected dark-frame distributions. Preview
frame zero had median 11, mean 10.575, and p99 12. The full-resolution frame
had median 10, mean 10.314, and p99 14. These measurements validate the direct
transport and analysis path, not optical phase, color, focus, or image quality.

## Acceptance effect

This closes the native-cable macOS reader deferral and demonstrates that the
same userspace executable and protocol implementation work directly on the
Mac in both supported modes. It does not provide an AVFoundation or system-wide
virtual-camera surface. The first-invocation short response remains a recorded
reliability observation for a future physical cold-attach repetition; it is
not masked with a broad retry or short-response policy.

The complete raw evidence bundle is retained at
`work/macos-native-alpha3-20261004T080254Z/`. It contains host and source
provenance, IOKit inventories, reader logs, the bounded diagnostic probe,
captured payloads, frame-statistics JSON, byte counts, and SHA-256 manifests.
# Superseding optical note (2026-10-04)

The native-cable success, control behavior, and exact byte counts remain valid.
The three/twenty-marker application assembly described below was later shown
to concatenate the beginnings of independent records. Correct preview capture
uses one bulk request and a 512-byte prefix. Correct full-resolution capture
uses the payload after byte 512 in record N plus the 192-byte continuation at
bytes 320--511 of record N+1. See `first-optical-capture.md`.
