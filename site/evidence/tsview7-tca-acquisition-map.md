# TSView7 TCA acquisition and frame-geometry map

Static inspection performed 2026-09-27. No Windows executable was run and no
USB request was sent while producing this note.

## Scope and source

This note follows the acquisition path in the purchase-era TSView7
`TS1000.dll` (SHA-256
`ee9c8ec6a680404c375a6bf0c44ded0486c6e7557cdee379a5f332eb9a8d12ac`).
Addresses use the DLL's preferred image base `0x10000000`.

The exported entry points are thin wrappers around a singleton camera object:

| Export | Internal target | Observed role |
|---|---:|---|
| `TS1000CameraPlay` | `0x10002030` | Starts two worker threads and creates their stop events |
| `TS1000CameraStop` | `0x100020a0` | Signals termination, waits for both workers, and closes their handles |
| `TS1000CameraGrabFrame` | `0x100020f0` | Calls the device object's bulk-frame method |
| `TS1000CameraGetImageSize` | `0x100023f0` | Returns the selected output dimensions |
| `TS1000CameraGetImageDataRGB24` | `0x10002430` | Copies the current decoded RGB24 image |
| `TS1000CameraGetImageData` | `0x10002470` | Copies the current raw/processed image representation |

`Play` itself does not issue a camera control request. The workers eventually
call `0x10004500`, which forwards to the bulk acquisition routine at
`0x10008fd0`.

## Transport identity

The import-address-table slots are unambiguous:

| Address | Import |
|---:|---|
| `0x1003421c` | `ReadFile` |
| `0x10034220` | `GetOverlappedResult` |
| `0x10034228` | `DeviceIoControl` |
| `0x1003422c` | `CreateFileA` |
| `0x10034230` | `WaitForSingleObject` |
| `0x10034234` | `CloseHandle` |
| `0x10034238` | `CreateEventA` |

The device object opens `\\.\tca000-0` for controls and the driver's read-pipe
path for the data plane. The camera descriptor independently exposes exactly
one non-control endpoint, bulk IN `0x82`. Together these establish that the
`ReadFile` path is the Windows-driver representation of the camera's bulk-IN
pipe rather than a second undocumented endpoint.

## Raw frame geometry

The mode selector at `0x10005d00` sets a width and height, saves the same pair
as the output dimensions, and passes the pair to `0x10008f50`. The jump table
at `0x10005de8` maps modes as follows:

| Mode | Width | Height | Raw bytes per frame | Status |
|---:|---:|---:|---:|---|
| 0 | 3664 | 2748 | 10,068,672 | Full sensor fallback/default |
| 1 | 1600 | 1200 | 1,920,000 | Fixed |
| 2 | 1280 | 960 | 1,228,800 | Fixed |
| 3 | 800 | 600 | 480,000 | Fixed |
| 4 | 640 | 480 | 307,200 | Fixed |
| 5 | register-derived | register-derived | width x height | ROI/dynamic |

The total byte count is exactly `width * height`, not RGB24 size. This is strong
evidence for an eight-bit, one-sample-per-pixel sensor stream, most likely a
Bayer mosaic. Offline emulation of the DLL's default converter identifies its
memory convention as GRBG input and Windows BGR24 output. Whether a live crop
begins on that phase, plus row orientation, possible optical-black regions, and
color calibration, remain unverified until a raw target frame is captured.

Mode 5 obtains its dimensions from the sensor-window state rather than a fixed
constant. An out-of-range mode falls back to mode 0 and resets the stored mode
to zero.

## Bulk transfer scheduler

The setup routine at `0x10008f50` stores:

```text
frame_bytes = width * height
chunk_bytes = width * 256
while floor(frame_bytes / chunk_bytes) < 3:
    chunk_bytes /= 2
while chunk_bytes > 0x80000:
    chunk_bytes /= 2
```

The cap is 524,288 bytes. The acquisition routine at `0x10008fd0` creates four
manual-reset event/OVERLAPPED records, submits four `ReadFile` operations, and
rotates them while assembling exactly `frame_bytes` bytes in the caller's
buffer. Each staging lane is `0x80200` bytes apart, leaving 512 bytes beyond
the maximum transfer size. Completion is checked with `GetOverlappedResult`.
Every `ReadFile` requests a full `chunk_bytes`, including the last one. The
final completion is intentionally shorter and must equal `final_bytes`; it is
not submitted with a reduced request length. Offline execution of the DLL's
`GrabFrame` path confirms this requested-versus-actual distinction, lane order,
and exact output bytes for all five fixed modes.

The resulting fixed-mode geometry is:

| Mode | Chunk bytes | Full chunks | Final bytes | Scheduled reads |
|---:|---:|---:|---:|---:|
| 0 | 468,992 | 21 | 219,840 | 22 |
| 1 | 409,600 | 4 | 281,600 | 5 |
| 2 | 327,680 | 3 | 245,760 | 4 |
| 3 | 102,400 | 4 | 70,400 | 5 |
| 4 | 81,920 | 3 | 61,440 | 4 |

`tools/tca_frame_geometry.py` reproduces these calculations without importing
libusb or touching a device. The portable staged scheduler and its exhaustive
fault tests are documented in `offline-capture-scheduler.md`.

## Initialization boundary

Static analysis now gives a concrete bulk read shape, but it does not remove
the D40 control-state gate. The DLL programs sensor registers before the first
successful frame read. For example, the path around `0x10005e40` writes the
sensor streaming/reset registers `0x0100`, `0x0103`, and `0x0104`, with a
300 ms delay between reset-related writes, before applying the selected mode.
Those mode-initialization writes use the TCA `0xc0/0x0a` acknowledged-write
wrapper. The DLL XOR-obfuscates both the register and value with `0x17a0`
before placing the result in the driver's ten-byte record. They are mutating
operations; the separate `0xc0/0x10` wrapper is not the mode-programming path.

The one bounded physical-cold TCA open/read/close prefix has now been executed.
All three fixed commands timed out while the before/after health checks passed.
A frame reader may continue to be implemented and tested against offline
fixtures, but it must not guess or replay the incomplete initialization
sequence against the physical camera. A targeted Windows first-attach USB
trace is now the evidence source for the missing state transition.
