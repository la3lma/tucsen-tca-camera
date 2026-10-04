---
title: Microscope Camera Reader Docstack
subtitle: From recovered USB protocol to controllable still capture, streaming, and application integration
date: 2026-09-27
lang: en
---

<main>

<nav class="project-links" aria-label="Project documents">
  <strong>Project map</strong>
  <a href="https://github.com/la3lma/tucsen-tca-camera#readme">Code &amp; README</a>
  <a href="https://la3lma.github.io/tucsen-tca-camera/report/microscope-window-sensor.pdf">PDF report</a>
  <a href="https://la3lma.github.io/tucsen-tca-camera/docstack/" aria-current="page">Live Docstack</a>
</nav>

# Objective

::: overview-grid
::: objective-card
<p class="eyebrow">Release objective</p>

## Make the camera usable, not merely understood

Deliver a safe, documented reader for the legacy AmScope/Tucsen
`0547:c003` microscope camera that can initialize the device, acquire full
frames, stream a supported preview mode, expose useful camera controls, and
feed ordinary applications through at least one standard operating-system
camera path.

<div class="status-row">
  <span class="status-chip">USB identity confirmed</span>
  <span class="status-chip">Linux cold start recovered</span>
  <span class="status-chip">Two Bayer8 modes captured</span>
  <span class="status-chip">Exposure + gain operational</span>
  <span class="status-chip">Neutral white balance measured</span>
  <span class="status-chip">V4L2 application path verified</span>
</div>
:::

::: next-card
<p class="eyebrow">Next evidence gate · D60 color and Linux integration</p>

### Calibrate color and retest the corrected Linux application path

The corrected userspace reader now assembles complete frames from validated
physical records and produces coherent 1280x960 and 3664x2748 microscope images. Optical testing
verified monotonic gain response and a 16-frame motion sequence; PNGs at three
resolutions and an H.264 proof clip are preserved. Full-resolution look-ahead
assembly removes the false 192-pixel strip without cropping, and an illuminated
blank region now provides reproducible in-situ white balance. The next gate is
a known color target, measured frame timing, and a live post-fix V4L2 run on
Linux.

**Safety boundary:** preserve the raw device record, change one documented
variable at a time, and keep provisional Bayer/color claims explicit.
:::
:::

<div class="evidence-strip" aria-label="Current evidence summary">
  <div><span class="metric">0547:c003</span><p>Observed device identity; product string “10MP CMOS Camera”.</p></div>
  <div><span class="metric">0x82 BULK IN</span><p>One vendor-specific interface; 512-byte high-speed packets.</p></div>
  <div><span class="metric">2 MODES</span><p>1280x960 preview and 3664x2748 full-resolution Bayer8 physically verified.</p></div>
  <div><span class="metric">14,400 FRAMES</span><p>40-minute preview endurance completed with flat sampled memory.</p></div>
</div>

## Definition of Done

The project is complete when all of the following are demonstrated from a clean
checkout on documented hardware:

1. **Still acquisition:** capture and decode a full-sensor still image with
   stable dimensions, bit depth, color interpretation, and metadata.
2. **Streaming:** sustain one supported preview mode for 30 minutes without
   parser desynchronization, unbounded memory growth, or an unrecoverable USB
   fault; publish measured frame rate and drop statistics.
3. **Operation:** expose every control that can be identified and safely
   verified, at minimum exposure and any supported gain, white-balance, mode,
   start, and stop operations. Unsupported controls fail explicitly.
4. **Reader API:** provide a portable user-space core and a command-line reader
   with deterministic raw capture, decoded output, structured diagnostics, and
   a stable control contract.
5. **Application path:** make frames available to ordinary applications through
   at least Linux V4L2 or a macOS camera integration, while preserving a direct
   library/API path on both Linux and macOS.
6. **Evidence and recovery:** ship protocol notes, fixtures, hashes, safety
   interlocks, reset/reconnect behavior, build instructions, tests, and an
   accepted evidence bundle.

## Document Control

| Field | Value |
|---|---|
| Objective | Build a usable driver/reader, stream, control surface, and application bridge for the legacy microscope camera |
| Canonical source | [camera-reader-docstack.md](camera-reader-docstack.md) |
| Published website | [GitHub Pages Docstack](https://la3lma.github.io/tucsen-tca-camera/docstack/) |
| Revision | 3.0, field-uniformity diagnosis and optical/flat-field correction plan added; exact alpha-6 Pi bench and post-switch optical/V4L2 harness prepared |
| Execution state | D00–D50 are complete and D60 is substantially advanced. Optical autocorrelation showed that separate 524,288-byte requests restarted at new record origins, causing the earlier repeated regions and false seam. Mode 2 fits after a 512-byte prefix. Mode 0 is assembled from record N `[512,end)` plus the 192-byte continuation at record N+1 `[320,512)`. Three consecutive full-resolution frames have distinct hashes and no false left strip. At 100 ms, gain 0..320 is monotonic; gain 256 produced a bright frame with negligible clipping. One pre-control buffered record is consumed before frame zero. A 16-frame run yielded distinct frames, three still sizes, and a 640x480 H.264 proof clip. Neutral-background white balance independently produced approximately R/G/B `0.87/1.0/2.0` in both modes; alpha-6 preserves those ratios when normalizing into FFmpeg's multiplier range. After changing to 10x, a bounded sweep recovered unclipped preview and full-resolution stills at 250 ms/gain 0. Exact alpha-6 is now built and fully tested on the Pi. A synthetic producer/consumer preflight passed six exact 1280x960 YUYV frames through the generic V4L2 loopback and cleaned it up, and an inert one-shot camera harness is staged for the cable move. Final known-target Bayer/color calibration, measured timing, and execution of that post-fix live-camera V4L2 gate remain open. AVFoundation remains deferred. |
| Acceptance authority | Camera owner, or an explicitly delegated technical owner recorded in D120 |
| Related report | [PDF report](https://la3lma.github.io/tucsen-tca-camera/report/microscope-window-sensor.pdf) |
| Reader source | [GitHub repository and README](https://github.com/la3lma/tucsen-tca-camera#readme) |
| Primary test bench | Raspberry Pi 5 `rpios-17` for physical USB, usbmon, and Linux validation; project-local Windows VM for reference initialization; macOS as the portability target and relay host |

## Method and Provenance

This plan follows the locally exported Agency Docstack convention:

- Concept, PRD, Design, and Plan are separate layers.
- Desired state, observed state, and evidence are never conflated.
- Every task has actors, dependencies, preconditions, postconditions, failure
  handling, and decidable proof.
- The dependency graph has one start and one exit; every task lies on a
  complete start-to-exit path.
- Device mutation is authorized only by its task gate, never merely because a
  request appears to be device-to-host.
- Evidence is append-only and contains no credentials.

The live Agency console was unavailable while this revision was authored
because its Docker runtime did not become ready. The structure was checked
against the local exported `docstack` exemplar and cached master Docstack. This
provenance limitation affects convention lookup, not the camera evidence.

# Concept

## Problem

The camera is physically sound enough to enumerate but is unusable as a normal
camera. It is not UVC. It exposes a vendor-specific USB interface and one bulk
IN endpoint, while its lost Windows installation depended on a proprietary
KMDF driver and model DLL. Modern applications therefore cannot discover,
control, or consume it.

The project must bridge three gaps:

1. **Protocol gap:** recover initialization, mode, control, capture, and frame
   boundary semantics from static evidence and bounded experiments.
2. **Image gap:** determine dimensions, packing, bit depth, Bayer pattern or
   other encoding, calibration, and color conversion.
3. **Application gap:** turn a working low-level reader into a stable API and a
   standard camera source usable by existing applications.

## Product Stance

The first implementation is a **portable user-space reader**, not a new kernel
driver. A shared core using libusb can run on Raspberry Pi Linux, desktop Linux,
and macOS; the application-facing surface can then be adapted separately.

A kernel driver becomes justified only if evidence shows that user-space USB
cannot meet throughput, latency, lifecycle, or standard-application integration
requirements. This prevents protocol discovery from becoming entangled with
kernel development and keeps unsafe experiments out of privileged code.

## Non-Goals for the First Release

- Reflashing or modifying persistent camera firmware.
- Guessing vendor requests or bulk lengths from names alone.
- Reproducing every feature of the legacy ISCapture application.
- Shipping extracted vendor binaries, proprietary code, or undocumented data
  outside the private evidence workspace.
- Supporting every historical Tucsen camera that shares a related DLL.
- Starting with a Linux kernel module, DriverKit extension, or macOS camera
  extension before the user-space reader is stable.
- Claiming a frame rate, color accuracy, or sensor model before measurement.

## Architectural Invariants

<div class="invariant-grid">
  <div class="info-card"><strong>Evidence before traffic</strong><p>Every live request has a static or captured provenance, declared expected result, bounded timeout, and recovery action.</p></div>
  <div class="info-card"><strong>Raw is authoritative</strong><p>Raw USB and frame bytes are preserved before decoding; decoded images are reproducible derivatives.</p></div>
  <div class="info-card"><strong>Core before adapters</strong><p>Protocol, transport, and decoding remain independent of V4L2, AVFoundation, GUI, or any one application.</p></div>
  <div class="info-card"><strong>No silent fallback</strong><p>Unknown modes, controls, short reads, and parser loss fail explicitly with structured evidence.</p></div>
  <div class="info-card"><strong>Reconnection is normal</strong><p>Unplug, reset, process crash, and application exit leave the camera recoverable without rebooting the host.</p></div>
  <div class="info-card"><strong>One source of protocol truth</strong><p>Packet definitions, response lengths, and mode tables are versioned once and consumed by tests and implementations.</p></div>
</div>

## Actors and Interests

| Actor | Interest |
|---|---|
| Microscope operator | See a correctly oriented, responsive preview; adjust exposure and capture a full-resolution still without USB knowledge |
| Scientific application | Receive frames with stable timestamps, dimensions, pixel format, and predictable start/stop behavior |
| Developer | Replay deterministic fixtures, inspect raw bytes, test without hardware, and add protocol knowledge without unsafe defaults |
| Support engineer | Diagnose permissions, enumeration, control failure, frame loss, and decoding problems from structured logs |
| Camera | Receive only evidence-backed commands within bounded timing and transfer limits |
| Operating-system adapter | Translate the stable reader contract into V4L2, AVFoundation, or another standard application surface |

## System Context

<div class="diagram-shell" role="img" aria-label="Camera reader system context">
<svg viewBox="0 0 1040 310" xmlns="http://www.w3.org/2000/svg">
  <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"/></marker></defs>
  <rect class="box target" x="20" y="105" width="180" height="100" rx="7"/>
  <text class="label" x="110" y="142" text-anchor="middle">Microscope camera</text>
  <text class="small" x="110" y="166" text-anchor="middle">0547:c003</text>
  <text class="small" x="110" y="187" text-anchor="middle">EP0 control + 0x82 bulk IN</text>
  <rect class="box core" x="280" y="65" width="255" height="180" rx="7"/>
  <text class="label" x="407" y="102" text-anchor="middle">Portable reader core</text>
  <text class="small" x="407" y="132" text-anchor="middle">USB transport</text>
  <text class="small" x="407" y="158" text-anchor="middle">Protocol state machine</text>
  <text class="small" x="407" y="184" text-anchor="middle">Frame parser + decoder</text>
  <text class="small" x="407" y="210" text-anchor="middle">Controls + diagnostics</text>
  <rect class="box" x="620" y="20" width="180" height="78" rx="7"/>
  <text class="label" x="710" y="52" text-anchor="middle">CLI / library API</text>
  <text class="small" x="710" y="76" text-anchor="middle">raw, still, stream, control</text>
  <rect class="box" x="620" y="116" width="180" height="78" rx="7"/>
  <text class="label" x="710" y="148" text-anchor="middle">Linux adapter</text>
  <text class="small" x="710" y="172" text-anchor="middle">V4L2 loopback / pipeline</text>
  <rect class="box" x="620" y="212" width="180" height="78" rx="7"/>
  <text class="label" x="710" y="244" text-anchor="middle">macOS adapter</text>
  <text class="small" x="710" y="268" text-anchor="middle">AVFoundation / extension</text>
  <rect class="box target" x="860" y="105" width="160" height="100" rx="7"/>
  <text class="label" x="940" y="142" text-anchor="middle">Applications</text>
  <text class="small" x="940" y="166" text-anchor="middle">preview · capture</text>
  <text class="small" x="940" y="187" text-anchor="middle">analysis · recording</text>
  <path class="edge" d="M200 155 H280"/>
  <path class="edge" d="M535 155 C575 155 580 59 620 59"/>
  <path class="edge" d="M535 155 H620"/>
  <path class="edge" d="M535 155 C575 155 580 251 620 251"/>
  <path class="edge" d="M800 59 C840 59 820 135 860 135"/>
  <path class="edge" d="M800 155 H860"/>
  <path class="edge" d="M800 251 C840 251 820 175 860 175"/>
</svg>
</div>

# PRD

## Product Goal

Provide a maintainable camera reader that turns the observed vendor-specific USB
device into a safe acquisition and control service, with standard application
integration layered over a portable protocol core.

## Release Rings

<div class="release-grid">
  <div class="release-card"><strong>R1 · Evidence reader</strong><p>Confirmed commands, deterministic raw still capture, frame boundaries, metadata, and offline fixtures.</p></div>
  <div class="release-card"><strong>R2 · Operable stream</strong><p>Decoded preview, explicit controls, stable start/stop/reconnect, library API, and CLI on Linux and macOS.</p></div>
  <div class="release-card"><strong>R3 · Application camera</strong><p>At least one standard OS camera path accepted in a real application, with the second platform proved or explicitly deferred.</p></div>
</div>

R1 is not a disposable prototype: its raw artifacts and protocol fixtures are
the executable basis for R2. R2 remains useful even if an OS-level virtual
camera proves expensive. R3 adapts the reader; it must not duplicate protocol
or decoder logic.

## Primary Use Cases

### UC1 — Inspect and identify

- **Trigger:** camera is connected or diagnostics are requested.
- **Success:** reader reports exact USB path, speed, descriptors, permissions,
  endpoint topology, reader version, and supported proven capabilities.
- **Minimum guarantee:** no vendor-specific request is sent in discovery mode.

### UC2 — Capture one full-resolution still

- **Trigger:** operator requests a still image.
- **Success:** reader initializes a known mode, obtains one complete raw frame,
  verifies boundaries and byte count, decodes it, and stores raw plus metadata.
- **Failure:** partial or ambiguous data is retained as failed evidence and is
  never presented as a successful image.

### UC3 — Stream a preview

- **Trigger:** an application or operator starts preview.
- **Success:** reader enters a proven stream state, emits timestamped frames in
  a declared pixel format, reports loss, and stops cleanly.
- **Failure:** repeated short reads, marker loss, or disconnect transitions to
  a bounded recovery state rather than an infinite retry loop.

### UC4 — Operate camera controls

- **Trigger:** caller reads or changes an advertised control.
- **Success:** supported range, units, current value, and resulting state are
  explicit; a read-back or observable frame change verifies writes where
  possible.
- **Failure:** unknown or unsafe operations are rejected before USB traffic.

### UC5 — Use the camera in an ordinary application

- **Trigger:** application opens the virtual/standard camera source.
- **Success:** application receives frames and can start/stop without owning
  raw USB; supported controls are available directly or through a companion
  control surface.
- **Failure:** one application's crash does not strand the camera or corrupt the
  next session.

### UC6 — Recover from interruption

- **Trigger:** unplug, USB reset, timeout, parser desynchronization, or reader
  crash.
- **Success:** reader stops transfers, releases resources, records the last
  proven state, and either reconnects through the full initialization sequence
  or exits with a specific repair action.

## Functional Requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| FR-01 | Enumerate and select only `0547:c003` by default; support explicit bus/path selection when several devices exist | Enumeration fixture and two-device selection test |
| FR-02 | Keep descriptor-only discovery physically incapable of vendor or bulk transfers | Import/call audit and runtime USB trace |
| FR-03 | Encode confirmed setup packets as `bmRequestType, bRequest, wValue, wIndex, data length` from versioned, generation-specific protocol tables | Golden packet tests against matched driver/DLL evidence |
| FR-04 | Model initialization, mode selection, capture, stream, stop, and recovery as explicit states | State transition tests and structured logs |
| FR-05 | Capture raw control responses and bulk data without silently truncating or padding | Raw artifacts, lengths, hashes, and short-read tests |
| FR-06 | Detect frame boundaries and validate complete frame byte counts before decoding | Parser fixtures including corruption and split markers |
| FR-07 | Decode at least one full-resolution still and one preview mode | Golden raw-to-image fixtures and visual checks |
| FR-08 | Expose proven controls with ranges, units, defaults, and read-back semantics | Control matrix and before/after evidence |
| FR-09 | Provide CLI operations for inspect, still, stream, controls, diagnostics, and fixture replay | Help snapshot and end-to-end CLI tests |
| FR-10 | Provide a stable library or local-process API that transports frames, timestamps, metadata, controls, and errors | Versioned API contract and compatibility tests |
| FR-11 | Feed one standard application camera interface without duplicating USB/protocol logic | Accepted application session and adapter boundary test |
| FR-12 | Recover after unplug/replug and process restart without rebooting the host | Reconnect matrix and repeated session test |

## Non-Functional Requirements

| ID | Requirement | Gate |
|---|---|---|
| NFR-01 Safety | Live vendor operations require an explicit opt-in build/runtime path, bounded length and timeout, and a recorded provenance | Every device task |
| NFR-02 Portability | Core builds on AArch64 Linux and Apple Silicon macOS; byte order and packing are explicit | D70 |
| NFR-03 Determinism | Offline protocol and decoder tests run without the camera and yield stable hashes | D60 onward |
| NFR-04 Observability | Logs identify device path, state transition, request tuple, expected/actual bytes, duration, and outcome without dumping secrets | D40 onward |
| NFR-05 Stability | 30-minute preview has no parser loss, unrecovered timeout, or unbounded memory growth; frame drops are measured | D100 |
| NFR-06 Resource use | Reader bounds USB buffers, frame queues, and disk capture; slow consumers have an explicit drop/back-pressure policy | D70 |
| NFR-07 Reproducibility | Clean build and test instructions pin required dependencies and preserve source hashes | D110 |
| NFR-08 Legal hygiene | Vendor binaries remain evidence-only and are not redistributed in packages | D110 |

## Acceptance Scenarios

1. On `rpios-17`, connect the camera, run inspect, capture a still, stream for
   30 minutes, change each supported control, stop, unplug/replug, and repeat.
2. On macOS, build the same core, enumerate the same identity, capture or replay
   a known frame, and prove the selected application integration boundary.
3. With no camera attached, run all packet, parser, decoder, state-machine, and
   adapter contract fixtures.
4. Inject short reads, split markers, malformed lengths, stalls, disconnects,
   and slow consumers; verify bounded failure and recovery.
5. Open the standard camera source in a named real application, record a short
   session, and compare frame metadata with the reader diagnostics.

# Design

## Target Architecture

The provisional implementation is a small C17 core with libusb. C keeps the
existing descriptor probe reusable, provides a stable ABI for adapters, and
avoids coupling the protocol to a GUI or platform runtime. D30 may revise this
choice only through an explicit architecture decision with migration cost.

| Component | Responsibility | Must not own |
|---|---|---|
| `usb_transport` | Device selection, claim/release, bounded control and bulk operations | Camera semantics or image decoding |
| `camera_protocol` | Request table, initialization/mode/control sequences, timing, state transitions | OS virtual-camera APIs |
| `frame_parser` | Bulk accumulation, marker handling, byte-count validation, frame metadata | Color policy or application lifecycle |
| `frame_decoder` | Packing, Bayer/color conversion, orientation, calibration hooks | USB access |
| `reader_api` | Stable lifecycle, frame, control, error, and diagnostics contract | Platform-specific camera registration |
| `camera-reader` CLI | Inspection, raw capture, decoded still, stream dump, replay, diagnostics | Private protocol duplication |
| Linux adapter | Convert reader frames to V4L2/GStreamer/FFmpeg-facing stream | Direct USB control |
| macOS adapter | Convert reader frames to AVFoundation-compatible buffers and chosen camera surface | Direct USB control |

## Confirmed Protocol Boundary

There are two incompatible Windows protocol generations for the same USB ID.
The 2011 TCA driver hard-codes vendor/device/IN `0xc0`; the 2013 IS1000 driver
derives direction from the DLL record and the later DLL uses vendor/device/OUT
`0x40`. Both copy request/value/index from record offsets 4/6/8. A DLL must be
paired with its matching driver; VID/PID alone is not sufficient provenance.

The purchase period and official compatibility matrix make TSView7 plus the
2011 TCA driver the primary lineage. Its fixed register read is:

```c
libusb_control_transfer(handle, 0xc0, 0x11, 0x0000, 0x3ff0,
                        response, 3, timeout_ms);
```

The response is a big-endian 16-bit value followed by acknowledgement `0x08`.
The DLL precedes register reads with `c0 02 0000 000f` and closes with
`c0 03 0000 000e` for this camera's observed product-string branch. Static
mapping is confirmed; live state entry is not yet working.

The data plane is bulk IN endpoint `0x82`, maximum packet size 512. The matching
TCA DLL reads exactly one byte per pixel and exposes fixed 3664x2748,
1600x1200, 1280x960, 800x600, and 640x480 modes plus a register-derived ROI
mode. It schedules four overlapped reads at a time, with mode-dependent chunks
capped at 524,288 bytes, and assembles exactly `width * height` bytes. The
`0x88`/`0x99` marker search and request `0xb3` belong to the incompatible later
ISCapture lineage; they remain comparison evidence and must not be imported
into the TCA implementation without a trace showing that this hardware uses
them.

## Reader State Machine

<div class="state-machine" aria-label="Reader states">
  <div class="state"><strong>Disconnected</strong><br><small>No handle</small></div><span class="arrow">→</span>
  <div class="state"><strong>Enumerated</strong><br><small>Identity checked</small></div><span class="arrow">→</span>
  <div class="state"><strong>Claimed</strong><br><small>Interface 0</small></div><span class="arrow">→</span>
  <div class="state"><strong>Initialized</strong><br><small>Proven sequence</small></div><span class="arrow">→</span>
  <div class="state"><strong>Acquiring</strong><br><small>Still or stream</small></div><span class="arrow">→</span>
  <div class="state"><strong>Stopping</strong><br><small>Drain + release</small></div>
</div>

Any state may enter `Fault`. A fault record includes the prior state, last
completed operation, expected and actual length, libusb/OS error, and whether a
full close/reopen is required. Automatic recovery is allowed only for a tested
transition; otherwise the reader releases resources and exits explicitly.

## API Shape

The stable reader surface should express capabilities rather than expose raw
request numbers:

```text
reader_open(selector, safety_policy)
reader_capabilities()
reader_configure(mode, control_set)
reader_capture_still(destination)
reader_start_stream(frame_callback, queue_policy)
reader_set_control(control_id, value)
reader_get_control(control_id)
reader_stop()
reader_diagnostics()
reader_close()
```

An expert-only diagnostics layer may render a confirmed packet in dry-run mode.
Arbitrary vendor requests are not part of the supported public API.

## Frame and Queue Contract

Each emitted frame carries:

- monotonically increasing reader sequence;
- host monotonic timestamp and acquisition duration;
- raw and decoded byte counts;
- width, height, stride, bit depth, and pixel format;
- current proven control snapshot;
- frame-integrity flags and any recovery boundary; and
- optional link to the raw evidence artifact.

The live stream uses a bounded queue. The default policy keeps the newest frame
for preview and increments a dropped-frame counter when consumers are slow.
Lossless recording uses an explicit back-pressure or disk-spool mode and may
refuse startup if the configured capacity is inadequate.

## Safety Model

<div class="gate-grid">
  <div class="info-card"><strong>Static gate</strong><p>Request tuple, caller, order, response length, and expected role are recovered before implementation.</p></div>
  <div class="info-card"><strong>Dry-run gate</strong><p>The tool prints exact USB fields and refuses transmission; golden tests compare them with evidence.</p></div>
  <div class="info-card"><strong>Live gate</strong><p>One opt-in request runs with bounded timeout/length, before-and-after enumeration, and a power-cycle recovery path.</p></div>
</div>

Device-to-host does not mean non-mutating. A vendor-IN request may trigger a
capture, advance internal state, or clear a status latch. Safety classification
depends on call context and observed behavior, not only `bmRequestType`.

## Standard Application Integration

### Linux

Prefer a user-space adapter that publishes decoded frames through an existing
standard path. The first candidate is V4L2 loopback or a GStreamer/FFmpeg
pipeline fed by the reader API. The adapter owns pixel-format negotiation and
application lifecycle; it never embeds protocol tables.

The current Micro-Manager tree has a Linux Video4Linux adapter with a
configurable device path/resolution and YUYV handling, making the proven
temporary V4L2 bridge the preferred first microscopy-application test. Its
separate AmScope adapter targets Windows MU-series USB 3/ToupCam hardware and
does not establish C003 compatibility. Pycro-Manager belongs above a working
MMCore camera/stage configuration; it is not another USB transport.

### macOS

First prove the C reader and decoded buffers independently. Then select the
least-complex application path that meets acceptance: direct AVFoundation use
inside a small capture application, or a modern Camera Extension when the
camera must appear system-wide. Signing, entitlements, installation, and host
OS support are separate adapter concerns.

## Recovery and Rollback

- Every live experiment begins and ends with descriptor enumeration and an
  interface claim/release check.
- A stalled transfer is cancelled or times out; buffers are discarded unless
  explicitly retained as failed evidence.
- Protocol changes are table/version changes with golden fixtures; rollback is
  selection of the previous table and reader revision.
- Adapter failure is isolated from the core; stopping an adapter closes its
  reader session and leaves no persistent registration unless explicitly
  installed under D80 or D90.
- No task writes camera non-volatile firmware. Discovering a required volatile
  upload creates a new reviewed task with its own hash and power-cycle proof.

## Key Decisions

| Decision | Current choice | Revisit when |
|---|---|---|
| Kernel versus user space | User-space libusb core | Measured throughput, latency, or application contract cannot be met |
| Core language | C17, provisional | D30 compares safety, ABI, tooling, and reuse cost |
| First physical host | Raspberry Pi 5 `rpios-17`; UTM CocoaSPICE and direct-QEMU USB paths are closed negative branches | Revisit only if a future UTM/libusb release demonstrably enumerates `0547:c003` |
| First app bridge | Linux standard path | D70 measurements or user priority justify macOS first |
| Windows emulator | Working D40 evidence bench; test mode, Tucsen driver, TSView, E1000 networking, and live host handoff verified; usbip-win2 is a preserved negative transport result | VirtualHere plus Linux `usbmon` exposes the successful initialization transactions; repeat once from a documented physical cold cycle |
| Persistent firmware | Prohibited | New evidence proves a volatile upload is required; non-volatile writes remain out of scope |

# Plan

## Execution Policy

D00 through D50 now record completed discovery and protocol work. The isolated
Windows/VirtualHere bench supplied a successful reference trace after USB/IP,
UTM CocoaSPICE, and direct-QEMU redirection were closed as preserved negative
branches. Its seven-command cold initializer and framing rules are reproduced
natively on `rpios-17`, so neither Windows nor a relay is a runtime dependency.
Mode 2 (`b4/c2`) is the established preview mode; mode 0 (`b4/c0`) is the
physically verified 3664×2748 still/full-resolution mode. D60 remains active
only for optical Bayer phase, orientation, and color validation once the
camera is mounted on the microscope. D100 continues Linux fault/reconnect
work, while D110 maintains the public source release and evidence index.

For every live-device task:

1. record source revision, device path, descriptors, power topology, and current
   evidence hashes;
2. state the exact operation, expected response, timeout, byte limit, and abort
   condition;
3. run one bounded variable at a time;
4. preserve raw result and host log;
5. re-enumerate and repeat the safe claim/release probe; and
6. update the evidence ledger before declaring the task complete.

No task is complete because code exists. Completion requires its declared
proof, clean recovery, and updated protocol/documentation state.

## Delivery Gates

| Gate | Exit condition | Unlocks |
|---|---|---|
| G0 Identity | Descriptors, interface, endpoint, permissions, hashes, and safe claim/release reproduced | Static protocol work |
| G1 Control map | Both driver generations, matched DLLs, exact TCA read/open/close tuples, and dry-run tooling independently confirmed | Bounded first-response work |
| G2 First response | One non-mutating request returns a stable, understood-length response without harming enumeration | Initialization trials |
| G3 Raw frame | One complete bulk frame is bounded, hashed, repeatable, and separable from headers/markers | Decoder work |
| G4 Decoded image | Full still and preview mode decode reproducibly with documented geometry and pixel format | Reader API and controls |
| G5 Operable reader | Stream, controls, stop, reconnect, fixtures, and diagnostics meet R2 acceptance | OS adapters |
| G6 Application camera | Real application consumes accepted frames; installation/removal and crash recovery pass | Packaging and release acceptance |

## Dependency Graph

Arrows are represented by each card's dependency line. D80 and D90 run in
parallel after the core reader, then merge at D100.

<div class="dag" aria-label="Task dependency graph">
  <a href="#d00"><span class="id">D00 · COMPLETE</span>Preserve physical and USB baseline<span class="deps">START</span></a>
  <a href="#d10"><span class="id">D10 · COMPLETE</span>Separate Windows transport generations<span class="deps">depends D00</span></a>
  <a href="#d20"><span class="id">D20 · COMPLETE</span>Classify requests and call order<span class="deps">depends D10</span></a>
  <a href="#d30"><span class="id">D30 · COMPLETE</span>Build dry-run protocol fixtures<span class="deps">depends D20</span></a>
  <a href="#d40"><span class="id">D40 · COMPLETE</span>Resolve first safe live response<span class="deps">depends D30</span></a>
  <a href="#d50"><span class="id">D50 · COMPLETE</span>Recover initialization and modes<span class="deps">depends D40</span></a>
  <a href="#d60"><span class="id">D60 · ACTIVE (OPTICS)</span>Capture and decode frames<span class="deps">depends D50</span></a>
  <a href="#d70"><span class="id">D70 · COMPLETE (ALPHA)</span>Build operable reader core<span class="deps">depends D60</span></a>
  <a href="#d80"><span class="id">D80 · COMPLETE (LINUX)</span>Linux application bridge<span class="deps">depends D70</span></a>
  <a href="#d90"><span class="id">D90 · READER COMPLETE / APP DEFERRED</span>macOS application bridge<span class="deps">depends D70</span></a>
  <a class="merge" href="#d100"><span class="id">D100 · ACTIVE (LINUX)</span>Stability, fault, and application acceptance<span class="deps">depends D80 + D90 or recorded macOS deferral</span></a>
  <a href="#d110"><span class="id">D110 · ACTIVE (ALPHA)</span>Package source, fixtures, and operations<span class="deps">depends D100</span></a>
  <a href="#d120"><span class="id">D120 · EXIT</span>Accept release and residual risks<span class="deps">depends D110</span></a>
</div>

## Task Summary

| ID | Task | Dependencies | State | Primary proof |
|---|---|---|---|---|
| D00 | Preserve physical and USB baseline | None | Complete | Photographs, descriptors, Pi enumeration, safe claim/release, hashes |
| D10 | Separate Windows transport generations | D00 | Complete | x86/x64 agreement within both 2011 and 2013 driver pairs |
| D20 | Classify requests and call order | D10 | Complete | TCA and IS1000 call graphs, safety classification, fixed TCA read candidate |
| D30 | Build dry-run protocol fixtures | D20 | Complete | Inert-by-default plans plus separately named, fixed opt-in binaries |
| D40 | Resolve first safe live response | D30 | Complete | 744-operation Windows reference capture decoded without pairing or validation gaps; seven-command native cold start reproduced |
| D50 | Recover initialization and modes | D40 | Complete | Repeatable mode-2 cold start, exposure/gain controls, and physically verified mode-0 selector/profile |
| D60 | Capture and decode frames | D50 | Active; transport complete, optics pending | Continuous 1280×960 and 3664×2748 Bayer8, exact marker framing, raw preservation, and decoder; optical phase pending |
| D70 | Build operable reader core | D60 | Complete for alpha | Public C17 libusb CLI, controls, stream, diagnostics, reopen tests, and cross-platform CI |
| D80 | Build Linux application bridge | D70 | Complete for alpha | Live physical-camera V4L2 device consumed by `v4l2-ctl` and FFmpeg, then cleanly removed |
| D90 | Build macOS application bridge | D70 | Portable reader complete; AVFoundation deferred | Exact alpha-3 directly captured preview and full-resolution frames over the native cable; system-camera surface deferred |
| D100 | Prove stability and fault recovery | D80,D90 | Active, Linux-first | Reopen, endurance, process-kill, host reboot, direct Apple Silicon capture, and bounded ownership hand-back passed; physical Pi cable disconnect/reconnect remains |
| D110 | Package source and operations | D100 | Active, alpha-3 published | Public GitHub repository, Apache-2.0 license, udev/V4L2 operations, CI, two modes, bounded initial recovery, optical procedure/analyzer, tested install/removal, validation record, report links |
| D120 | Accept release | D110 | Proposed | Owner acceptance against Definition of Done |

### Non-gating Research Lane — Updated Firmware Discovery

This is a **low-priority, opportunistic investigation**, not a dependency or
prerequisite for D20–D120. It may run whenever protocol work is waiting on
hardware, long tests, or review.

| Field | Contract |
|---|---|
| Priority | Low, but retained in scope |
| Goal | Determine whether a newer, compatible firmware image or official updater exists for `0547:c003` / TCA-10.0N / IS1000 |
| Search surface | Tucsen and AmScope archives/support pages; archived vendor sites; distributor mirrors; driver packages; updater manifests; public USB and Linux projects |
| Evidence | Preserve source URL, retrieval date, package hash, signatures, model/VID/PID claims, firmware version markers, and license/redistribution status |
| Safety boundary | Search and static extraction only; never upload firmware merely because a file or updater matches the model name |
| Adoption gate | Any candidate upload becomes a separately reviewed, explicitly authorized experiment with a verified target identity, recovery method, power-loss analysis, and rollback path |
| Relationship to delivery | Findings may simplify or improve the reader, but absence of updated firmware cannot block the operating-system reader plan |

Current result: no standalone firmware image or official updater has been
found. The official Tucsen archive supplies driver/application packages. A
2026-09-29 static refresh preserved AmScope's current ARM64 Linux and Windows
packages: the Linux udev rule covers vendor `0547` broadly, but neither package
names C003/TCA/IS1000, and both 232-entry Windows INFs omit
`USB\\VID_0547&PID_C003`. The recovered legacy INF phrase `Firmware Device` is
a driver label, not proof of an external firmware payload. A 2026-10-03
official-domain refresh found firmware tools only for unrelated newer Tucsen
families and no exact-model candidate. See the
[firmware-discovery evidence](../evidence/firmware-discovery.md). This bounded
negative result does not change the delivery dependency graph.

Useful search aliases include `TCA-10.0N`, `TCA-10.0-N`, `IS1000`,
`0547:C003`, `Xintu Photonics`, `Tucsen`, `AmScope 10MP`, and strings or version
identifiers extracted from the archived driver and camera DLL packages.

### Non-gating Research Lane — Historical Application Integration

A 2014 University College London thesis explicitly identifies a Tucsen
TCA-10.0-N running on Micro-Manager 1.4 for live view and an 80-hour time-lapse.
This proves that the exact model reached a general scientific-imaging
application. Inspection of the official Micro-Manager tree at the nearest
pre-publication commit finds generic TWAIN and OpenCV camera adapters, but no
legacy Tucsen-specific adapter. The historical route may therefore have used a
separately supplied TWAIN or system-camera source, or an adapter not present in
the public tree; it remains unresolved.

This finding makes Micro-Manager a credible later acceptance application and
supports selecting a standard V4L2/media bridge on Linux. It does not resolve
cold initialization, prove UVC/DirectShow/TWAIN registration, or authorize a
live request. See the
[Micro-Manager application precedent](../evidence/micromanager-application-precedent.md).

### Non-gating Reverse-Engineering Lane — Ghidra Call-Graph Recovery

Ghidra is used to refine, name, and cross-check the static model recovered from
the working purchase-era Windows stack. This lane remains parallel to the live
transport trace: it supplies implementation guidance, but does not delay
observation of the known-good cold-start sequence.

| Field | Contract |
|---|---|
| Primary target | Working `TS1000.dll`, because it contains the TCA-10.0-N model logic, initialization tables, register semantics, modes, and frame handling |
| Secondary target | `Tucsen64.sys`, to name IOCTL dispatch, request marshalling, buffer limits, completion behavior, and error translation in the thin USB transport |
| Inputs | Only the hash-pinned binaries from the verified Windows installation; preserve originals and analyze copies |
| Method | Import PE symbols and types, identify `CreateFile`/`DeviceIoControl` callers, propagate IOCTL structures, recover call graphs and state transitions, and correlate constants with the emulator and USB trace |
| Required outputs | Reproducible headless Ghidra project or script, function-address/name map, decompiler excerpts limited to project evidence, request-structure types, unresolved edges, and hashes |
| Validation | Every inferred request or state edge must match a captured transaction, an emulated execution, or a byte-level disassembly check before entering reader code |
| Safety boundary | Static analysis only; decompiler output never authorizes a live request or firmware operation by itself |
| Integration point | Feed confirmed names, sequencing, timing, and register semantics into D40/D50 and convert stable findings into golden protocol tests |

The first targeted headless pass is complete. Official Ghidra 12.1.4 was
hash-verified and built with project-local dependencies; persistent projects,
reusable scripts, function inventories, and decompiler outputs are preserved.
It independently confirms the ten-byte command ABI, obfuscated register
writes, register reads, four implemented driver IOCTLs, ordinary KMDF USB
enumeration/configuration, and the split bulk-URB path. It also proves that
the DLL's ignored `0x22208a` call cannot hide a USB transaction in the matched
driver. No firmware-loader call was found in prepare-hardware. See the
[targeted Ghidra evidence](../evidence/ghidra-targeted-decompilation.md).

This substantially improves maintainability and cross-checks the current C17
implementation, but does not yet explain the physical-cold `0x02` timeout.
The VirtualHere trace therefore remains the evidence gate.

## Task Contracts

<div class="task-controls" role="group" aria-label="Filter task contracts">
  <button type="button" data-task-filter="all" aria-pressed="true">All tasks</button>
  <button type="button" data-task-filter="ready" aria-pressed="false">Ready</button>
  <button type="button" data-task-filter="complete" aria-pressed="false">Complete</button>
  <button type="button" data-task-filter="proposed" aria-pressed="false">Proposed</button>
  <span class="task-progress" aria-live="polite"></span>
</div>

::: {.task-card data-state="complete"}
<!-- task: D00; depends: none; state: complete -->
### D00 — Preserve Physical and USB Baseline {#d00}

| Field | Contract |
|---|---|
| State | Complete; sole start |
| Actors | Camera owner, protocol developer |
| Goal | Establish immutable identity, topology, host behavior, and safe access before any protocol experiment |
| Preconditions | Physical camera and at least one macOS/Linux host available |
| Postconditions | Photographs, descriptors, strings, VID/PID, endpoint layout, Pi enumeration, permissions, safe claim/release, and source hashes preserved |
| Failure/rollback | Disconnect camera; preserve partial logs; do not install speculative drivers |
| Expected proof | `device-identity.md`, Pi enumeration, safe probe note, photographs, and verified hashes |

Happy-day steps:

1. Photograph enclosure, USB connector, and protected sensor side.
2. Enumerate descriptors on macOS and Raspberry Pi Linux.
3. Confirm interface `0xff` and bulk-IN endpoint `0x82` at high speed.
4. Install device-specific permissions and prove open/claim/release with a
   binary that imports no transfer operation.
:::

::: {.task-card data-state="complete"}
<!-- task: D10; depends: D00; state: complete -->
### D10 — Separate Windows Transport Generations {#d10}

| Field | Contract |
|---|---|
| State | Complete |
| Actors | Protocol developer |
| Goal | Convert each recovered DLL/driver boundary into an exact, generation-specific USB control-transfer shape |
| Preconditions | D00 complete; vendor archives extracted statically and hashed |
| Postconditions | IOCTL `0x222059` and record offsets independently agree in x86/x86-64; 2011 TCA hard-codes `0xc0`, while 2013 IS1000 derives `0x40` from its record |
| Failure/rollback | Static-only; discard generated disassembly and retain original binaries unchanged |
| Expected proof | `ts1000-static-protocol-map.md` and `tucsen-driver-ioctl-handler.md` |

Happy-day steps:

1. Trace the DLL's only `DeviceIoControl` call and ten-byte record.
2. Locate both KMDF IOCTL handlers and their dispatch branch.
3. Cross-check setup-packet construction in both architectures.
4. Record the exact libusb shape without transmitting it.
:::

::: {.task-card data-state="complete"}
<!-- task: D20; depends: D10; state: complete -->
### D20 — Classify Requests and Call Order {#d20}

| Field | Contract |
|---|---|
| State | Complete |
| Actors | Protocol developer, reviewer |
| Goal | Give every embedded request a caller, order, response length, timing context, and safety classification |
| Preconditions | D10 complete; DLL and disassembly hashes match evidence |
| Postconditions | Later requests `b3`–`be` are separated from the TCA family; TCA `0x11/0x3ff0` is classified as a non-mutating, three-byte register read with an exact open/close prefix |
| Failure/rollback | Static-only; unresolved semantics remain unknown rather than guessed; Windows trace becomes a targeted fallback |
| Expected proof | Annotated call graph, sequence tables, unresolved-edge list, and selected D40 candidate rationale |

Happy-day steps:

1. Trace request-table references to initialization, control, preview, still,
   and shutdown call sites.
2. Record request/value/index/length, ordering, repetition, delays, and response
   consumers.
3. Separate observation from semantic inference and rank candidates by risk.
4. Select the first candidate only if it is nonzero-response and not adjacent to
   capture, mode change, reset, or shutdown.
:::

::: {.task-card data-state="complete"}
<!-- task: D30; depends: D20; state: complete -->
### D30 — Build the Dry-Run Protocol Fixture {#d30}

| Field | Contract |
|---|---|
| State | Complete |
| Actors | Reader developer, reviewer |
| Goal | Encode confirmed packet construction and planned sequences while making transmission impossible by default |
| Preconditions | D20 complete; protocol table and first-candidate rationale reviewed |
| Postconditions | Tool renders exact tuples, lengths, timeouts, evidence IDs, and sequence order; golden tests pass on Linux/macOS |
| Failure/rollback | Tool remains dry-run-only; remove any transfer import from the default binary |
| Expected proof | Source review, symbol/import audit, golden output hashes, malformed-input refusal tests |

Happy-day steps:

1. Define versioned protocol records and provenance fields.
2. Add a dry-run command that prints exact setup and expected response.
3. Compile a default binary without control/bulk transfer calls.
4. Add a separately named opt-in experimental binary only after review.
:::

::: {.task-card data-state="complete"}
<!-- task: D40; depends: D30; state: complete -->
### D40 — Resolve the First Safe Live Response {#d40}

| Field | Contract |
|---|---|
| State | Complete; the successful Windows session was captured below the relay and its minimal cold-start sequence was reproduced natively on Linux |
| Actors | Camera owner, protocol developer |
| Goal | Obtain one stable vendor response without starting capture or degrading enumeration |
| Preconditions | D30 proof complete; exact tuple, expected length, timeout, abort, and power-cycle path reviewed |
| Postconditions | Response repeats across cold sessions, or a Windows USB trace explains the state-entry requirement; camera passes descriptor and claim/release post-check |
| Failure/rollback | Stop after one bounded failure; close, unplug, wait, repower, and run safe probe; do not vary multiple fields |
| Expected proof | Before/after inventory, raw response hashes, timing, return codes, kernel log, and recovery result |

Completion evidence:

1. The sealed trace contains 744 paired operations, including 191 vendor
   controls and 528 bulk transfers, with no correlation or semantic-validation
   issue.
2. Seven fixed vendor controls initialize mode 2. Their stalled IN data stages
   are expected side effects, not failed commands.
3. Direct Linux replay on a cold device enables continuous bulk streaming;
   Windows and the relay are no longer runtime dependencies.
4. USBPcap and USB/IP failures remain preserved as negative instrumentation and
   transport evidence rather than being silently discarded.
:::

::: {.task-card data-state="complete"}
<!-- task: D50; depends: D40; state: complete -->
### D50 — Recover Initialization, Modes, and Controls {#d50}

| Field | Contract |
|---|---|
| State | Complete; preview/full-resolution initialization plus exposure/gain are physically verified and versioned |
| Actors | Protocol developer, camera operator |
| Goal | Establish the smallest repeatable transition from claimed device to a known acquisition mode |
| Preconditions | D40 stable response; remaining sequence evidence classified or a targeted Windows trace approved |
| Postconditions | Initialization, mode, control read/write, start, stop, and shutdown sequences are versioned with timing and response rules |
| Failure/rollback | Close/reopen or power-cycle; revert to last proven prefix; no persistent firmware action |
| Expected proof | State-machine traces, capability table, differential experiments, and cold-start repetitions |

Happy-day steps:

1. Reconstruct initialization in evidence-backed prefixes, using named Ghidra
   functions and types where they agree with the captured USB sequence.
2. Add one request at a time and validate responses and device health.
3. Compare isolated mode/control changes rather than long mixed sessions.
4. Freeze one still mode and one preview mode for D60.

Completion evidence: mode 2 (`b4/c2`) is the accepted preview mode. Selector
`b4/c0`, 3664×2748 geometry, and the exact next-512-byte transfer formula
produce a 10,068,992-byte record. Later optical work established that the
formula's 320-byte surplus precedes a 192-byte continuation from the preceding
frame; the current frame begins at offset 512 and completes in the next record.
The reader applies recovered row times to bounded exposure control.
:::

::: {.task-card data-state="active"}
<!-- task: D60; depends: D50; state: active -->
### D60 — Capture, Parse, and Decode Frames {#d60}

| Field | Contract |
|---|---|
| State | Active; coherent preview/full-resolution images, optical gain, and neutral-background white balance pass; exact alpha-6 Pi bench and one-shot Linux application harness are ready, while final known-target phase/color and live execution remain |
| Actors | Protocol developer, imaging reviewer |
| Goal | Turn bounded bulk reads into reproducible full still and preview images |
| Preconditions | D50 sequences and exact expected bulk limits available |
| Postconditions | Parser handles transfer boundaries; frame geometry, headers, markers, packing, orientation, and color interpretation are documented and tested |
| Failure/rollback | Preserve raw bytes; decoder changes cannot alter authoritative raw artifacts; return to last known parser revision |
| Expected proof | Multiple cold-session raw hashes, parser corruption fixtures, golden decoded images, dimensions, and pixel statistics |

Happy-day steps:

1. Capture bounded raw bulk data with timestamps and packet/read lengths.
2. Verify that each selected TCA mode yields exactly its recovered
   `width * height` byte count across arbitrary USB transfer splits.
3. Determine whether the bytes are unframed Bayer samples or include a small
   header/trailer not represented in the DLL's delivered frame count.
4. Decode one full still and preview mode; confirm Bayer order, orientation,
   crop, and color with a
   simple physical target.

Current slice: one bulk request retrieves a complete 1,229,312-byte mode-2 or
10,068,992-byte mode-0 physical record. Mode 2 emits the raster after offset
512. Mode 0 emits record N after offset 512 and appends bytes 320--511 of record
N+1, retaining N+1 as look-ahead. Both modes now produce coherent optical
images, and three consecutive full-resolution frames have distinct hashes.
Gain response is monotonic, one buffered pre-control record is handled
explicitly, a 16-frame motion proof passes, and neutral-background white
balance is reproducible. The current 10x blank field is measurably asymmetric:
equal regions range from mean luma 134.0 at bottom-left to 193.9 at top-middle.
The [field-uniformity note](../evidence/field-illumination-correction.md) records
a Köhler alignment and relay-isolation checklist plus a per-Bayer-plane
dark/flat correction that can run before demosaic or V4L2 output. File/stdout conversion passes; the existing V4L2
adapter awaits a live post-fix Linux retest. Exact alpha-6 already builds and
passes its complete suite on the prepared Pi. A synthetic producer and separate
consumer passed six exact 1280x960 YUYV frames through its loopback dependency,
which was then removed, and an inert exact-commit harness is staged to capture
both modes and have FFmpeg consume six camera frames through `/dev/video42`
immediately after the physical cable move.
:::

::: {.task-card data-state="complete"}
<!-- task: D70; depends: D60; state: complete -->
### D70 — Build the Operable Reader Core {#d70}

| Field | Contract |
|---|---|
| State | Complete for the Linux-first alpha; additional modes and optical calibration remain compatible extensions |
| Actors | Reader developer, API reviewer, camera operator |
| Goal | Productize protocol and decoding as a portable library and CLI with controls, streaming, diagnostics, and recovery |
| Preconditions | D60 golden fixtures and modes complete |
| Postconditions | C API/ABI and CLI work on Pi Linux and Apple Silicon macOS; offline tests need no camera; bounded queue and reconnect policies are explicit |
| Failure/rollback | Keep last fixture-compatible reader revision; adapters cannot bypass the stable API |
| Expected proof | Clean builds, API contract, CLI snapshots, unit/fixture tests, stream/control/reconnect sessions, memory and queue metrics |

Offline implementation slice complete: `src/tca_reader.[ch]` and the
`camera-reader` CLI implement the stable session, exact-frame decode, metadata,
bounded latest/lossless queues, control validation, diagnostics, fault/close/
reopen behavior, mode inspection, and replay. Strict and sanitizer tests pass
on macOS; the same sources and CLI tests pass natively on Ubuntu ARM64. The
final public C17 executable now cold-initializes the physical
camera directly, applies bounded exposure/gain, validates and removes the record
framing, streams Bayer8 to a file or stdout, and releases the claimed interface
on exit. Native ARM64 Linux and Apple Silicon builds pass an exact libusb import
allowlist and inert CLI tests; GitHub CI repeats both builds. Ten separate live
processes completed open/init/capture/close without failure. See the
[portable reader evidence](../evidence/offline-reader-session.md) and
[public live-validation evidence](../evidence/public-release-live-validation.md).

Happy-day steps:

1. Separate transport, protocol, parser, decoder, and public API modules.
2. Implement inspect, still, stream, controls, replay, and diagnostics commands.
3. Add bounded queues, structured errors, stop, close, and reconnect.
4. Prove source and binary portability on both target operating systems.
:::

::: {.task-card data-state="complete"}
<!-- task: D80; depends: D70; state: complete -->
### D80 — Build the Linux Application Bridge {#d80}

| Field | Contract |
|---|---|
| State | Complete for the Linux-first alpha |
| Actors | Linux adapter developer, application user |
| Goal | Make reader frames consumable through a standard Linux video or media pipeline |
| Preconditions | D70 stable reader API and accepted preview pixel format |
| Postconditions | Selected V4L2/GStreamer/FFmpeg path starts, streams, stops, and restarts in at least two representative applications |
| Failure/rollback | Remove/stop user-space adapter and any loopback device configuration; core reader remains usable |
| Expected proof | Install/remove script, capability listing, application recordings/screenshots, metadata comparison, crash/reopen test |

The final foreground bridge consumes live Bayer8 from the physical camera,
converts it with FFmpeg, feeds a temporary 1280×960 YUYV V4L2 device, refuses
to disturb an existing loopback configuration, and removes only the device it
created. `v4l2-ctl` reported the intended format and FFmpeg consumed three
frames into a lossless recording. See the [Linux V4L2 replay bridge
evidence](../evidence/linux-v4l2-replay-bridge.md) and report milestone.

Happy-day steps:

1. Choose the smallest standard path and document the decision.
2. Translate reader frames and timestamps without copying protocol logic.
3. Prove application negotiation, stream lifecycle, and slow-consumer behavior.
4. Verify clean removal and camera reuse after application failure.
:::

::: {.task-card data-state="proposed"}
<!-- task: D90; depends: D70; state: proposed -->
### D90 — Build the macOS Application Bridge {#d90}

| Field | Contract |
|---|---|
| State | Portable reader complete over the native cable; AVFoundation application surface deferred for the Linux-first alpha |
| Actors | macOS adapter developer, application user |
| Goal | Prove the portable reader in AVFoundation and provide the least-complex accepted macOS camera surface |
| Preconditions | D70 stable reader API; signing/entitlement needs inventoried |
| Postconditions | Decoded frames reach an AVFoundation consumer; direct app integration or Camera Extension is installed, exercised, and removable as selected |
| Failure/rollback | Uninstall extension/adapter and retain CLI/library path; no system USB driver is installed |
| Expected proof | Build/sign/install receipt as applicable, application session, timestamps/pixel format, crash/reopen and uninstall result |

Happy-day steps:

1. Bridge reader buffers into CVPixelBuffer/AVFoundation-compatible form.
2. Prove capture inside a minimal host application.
3. Decide whether system-wide discovery is required for acceptance.
4. If required, implement and verify a modern Camera Extension with clean
   install/remove behavior.

The exact alpha-3 Apple Silicon CLI/library path now captures the camera over a
direct native cable, without Windows or a Pi relay. Three preview frames, one
full-resolution frame, and a fresh-process preview reopen passed with exact
sizes, controls, analysis, and exit zero. The first cold-attach invocation
failed closed on a one-byte response where the trace predicts a stall; all
subsequent controls returned the predicted stall. AVFoundation/Camera
Extension work remains a recorded deferral under the owner's Linux-first,
macOS-non-blocking objective. See [native-cable Apple Silicon
validation](../evidence/macos-native-cable-validation.md) and [relay
validation](../evidence/macos-virtualhere-live-validation.md).
:::

::: {.task-card data-state="active"}
<!-- task: D100; depends: D80,D90; state: active -->
### D100 — Prove Stability, Fault Handling, and Application Acceptance {#d100}

| Field | Contract |
|---|---|
| State | Active, Linux-first; macOS application integration is explicitly non-blocking for this stabilization pass |
| Actors | Test owner, camera owner, platform reviewers |
| Goal | Demonstrate that the reader and adapters remain usable beyond a successful laboratory frame |
| Preconditions | D80 and D90 complete or an explicit owner-approved platform deferral is recorded |
| Postconditions | Stream, controls, application lifecycle, disconnect, timeout, malformed data, and slow-consumer cases meet declared thresholds |
| Failure/rollback | Retain failed artifacts; fix the owning layer; do not mask failures with retries or adapter buffering |
| Expected proof | 30-minute metrics, fault-injection matrix, memory/queue profile, repeated cold starts, real-application acceptance record |

Happy-day steps:

1. Run repeated still and 30-minute preview sessions.
2. Inject short reads, marker splits, stalls, unplug/replug, process crash, and
   slow consumption.
3. Verify each supported control and unsupported-control refusal.
4. Accept measured frame rate and quality against hardware limits.

Current slice: 30 controlled frames, ten independent ten-frame processes, and
a 14,400-frame/2,410-second continuous run passed. Sampled RSS remained 4,784
KiB. A first-frame flush was observed complete while a 100-frame process was
still active. After a controlled `SIGKILL`, a new process immediately reopened
the device and captured three frames. A connected-camera Pi reboot produced a
new Linux boot ID and USB instance, after which public main rebuilt, passed its
tests, and cold-captured three exact-size frames. Physical cable
disconnect/reconnect remains a separate hands-on test. An inert exact-alpha-3
harness is staged on the Pi: it requires a real zero-device interval before
accepting re-enumeration, then captures three frames, checks exact sizes and
status, analyzes frame zero, and hashes the evidence directory. It has passed
static and Pi dry-run checks but has deliberately not begun its operator wait.
Physical Apple Silicon capture through a Pi relay also passed, and exact
alpha-3 subsequently passed preview, full-resolution, and reopen capture over
the direct Mac cable. Returning the camera to Linux reproduced one invalid leading warm-up frame; public alpha-2
now preserves it as raw evidence, discards at most two invalid frames before
frame zero, and passed the same hand-back in one process. Marker loss after
delivery begins remains fatal.
:::

::: {.task-card data-state="active"}
<!-- task: D110; depends: D100; state: active -->
### D110 — Package Source, Fixtures, and Operations {#d110}

| Field | Contract |
|---|---|
| State | Active; public alpha-3 packages the reader, optical tooling, and tested install/removal while residual physical validation continues |
| Actors | Release developer, support reviewer |
| Goal | Make the accepted reader reproducible and supportable without redistributing vendor binaries |
| Preconditions | D100 proof complete; licenses and dependency versions inventoried |
| Postconditions | Source release, fixture subset, build/install/remove procedures, udev guidance, diagnostics, and troubleshooting are complete |
| Failure/rollback | Packages are not published; retain local artifacts and correct reproducibility/licensing gaps |
| Expected proof | Clean Pi/macOS builds, package hashes, license manifest, install/remove test, documentation review, evidence bundle index |

Happy-day steps:

1. Pin and document build dependencies and supported platforms.
2. Separate redistributable fixtures from private vendor evidence.
3. Package reader, CLI, adapters, permissions, and diagnostics.
4. Rehearse clean installation, use, removal, and rebuild.

The early release is at <https://github.com/la3lma/tucsen-tca-camera> with an
Apache License 2.0, C17 source, Linux/macOS CI, udev rule, optional V4L2 adapter,
protocol notes, safety boundaries, contribution guidance, and links back to
the forthcoming Journal of Bjørn report.

Public main commit `a61c044` additionally provides a dependency-free Bayer
frame statistics/focus utility and a microscope-mounted optical procedure. The
exact commit passed Ubuntu/macOS CI and all Pi tests, then cold-captured and
analyzed one fresh physical mode-2 frame with exact byte counts and exit zero.
Because the sensor remained covered, this is tooling readiness rather than an
optical pass.

Current main commit `fb502c1` also documents and tests staged installation and
exact-file removal of the reader, V4L2 helper, and frame analyzer. The test
requires an unrelated sentinel in the same directory to survive. It passes on
Apple Silicon, the Pi, Ubuntu CI, and macOS CI without modifying the live Pi
installation.

These changes are sealed in annotated public prerelease
[`v0.2.0-alpha.3`](https://github.com/la3lma/tucsen-tca-camera/releases/tag/v0.2.0-alpha.3)
at exact commit `3c16d2a`. Independent main and tag CI runs pass on Ubuntu and
macOS. A clean exact-tag Pi worktree passed all tests, then cold-captured and
analyzed one exact-size physical frame with controls and exit zero.

The current [release acceptance audit](../evidence/release-acceptance-audit.md)
marks the Linux reader/API, preview endurance, application bridge, direct-cable
Apple Silicon reader path, safety, reproducibility, and legal-hygiene
requirements as passed. D120 remains open for physical cable reconnect and
optical/color validation. AVFoundation remains an explicit Linux-first
deferral rather than an exit blocker.
:::

::: {.task-card data-state="proposed"}
<!-- task: D120; depends: D110; state: proposed -->
### D120 — Accept the Release and Residual Risks {#d120}

| Field | Contract |
|---|---|
| State | Proposed; sole exit |
| Actors | Camera owner/acceptance authority, technical owner |
| Goal | Decide whether the delivered reader satisfies the objective and record any explicit deferrals |
| Preconditions | D110 evidence bundle complete; Definition of Done evaluated line by line |
| Postconditions | Release is accepted with version/hash and residual risks, or returned to the owning task with specific failed criteria |
| Failure/rollback | Keep last accepted build; uninstall rejected adapters; preserve evidence and camera recoverability |
| Expected proof | Dated acceptance referencing source/package hashes, supported modes/controls/apps, known limits, and deferred platform work |

Happy-day steps:

1. Re-run the principal still, stream, control, reconnect, and application flows.
2. Review installation/removal, diagnostics, source, fixtures, and legal hygiene.
3. Record supported platforms, modes, controls, applications, and measured
   performance.
4. Accept or reject each Definition of Done item and publish the release status.
:::

## Evidence Ledger

| ID | Claim | Evidence | Status |
|---|---|---|---|
| E-001 | Physical enclosure and lack of visible model marking are documented | [Owner photographs](../evidence/photos/) | VERIFIED |
| E-002 | Device is `0547:c003`, high-speed USB 2.0, one `0xff` interface, bulk IN `0x82`, 512-byte packets | [Device identity](../evidence/device-identity.md) and Pi enumeration | VERIFIED |
| E-003 | Linux opens and safely claims/releases interface 0 without a transfer-capable probe | [Safe libusb probe](../evidence/safe-libusb-probe.md) | VERIFIED |
| E-004 | IOCTL `0x222059` has distinct 2011 `0xc0` and 2013 direction-aware mappings; both copy request/value/index record offsets | [Windows IOCTL handler analysis](../evidence/tucsen-driver-ioctl-handler.md) | VERIFIED |
| E-005 | DLL contains requests `b3`, `b4`, `b5`, `b6`, `b7`, `b8`, `ba`, `bb`, `bd`, `be` | [Static protocol map](../evidence/ts1000-static-protocol-map.md) | VERIFIED |
| E-006 | Later-lineage `b3` is a capture trigger | Static call proximity only | INFERRED / OPEN |
| E-007 | Initialization, response semantics, frame dimensions, encoding, and controls are known | No accepted evidence yet | OPEN |
| E-008 | Reader streams into standard Linux/macOS applications | No implementation yet | OPEN |
| E-009 | Official software maps TCA-10.0N `0547:c003` to TSView6/7; its TCA DLL exposes a fixed `0x11/0x3ff0` register read and open/close prefix | [TSView7 TCA protocol map](../evidence/tsview7-tca-protocol-map.md) | VERIFIED |
| E-010 | Nine bounded Linux trials failed without loss of enumeration; the final physical-cold run used the corrected TCA tuple and timed out on open/read/close while both health checks passed | [Live control trials](../evidence/live-control-trials.md) | VERIFIED NEGATIVE |
| E-011 | No standalone C003 firmware/updater was found in the official surfaces and recovered packages inspected; this remains a bounded search result | [Firmware discovery](../evidence/firmware-discovery.md) | VERIFIED NEGATIVE / NON-GATING |
| E-012 | Historical open-source inventory names IS1000 C003, but its implemented driver targets 4D88 and must not be replayed against this camera | [Open-source prior art](../evidence/open-source-prior-art.md) | VERIFIED BOUNDARY |
| E-013 | TSView7 ignores the `0x02` wrapper result, then validates 80 even registers `0x0000`–`0x009e` with `0x11`; the Linux probe stopped earlier than the vendor path | [TCA startup validation](../evidence/tsview7-tca-startup-validation.md) | VERIFIED STATIC |
| E-014 | All eight USBPcap roots were captured; only QEMU `0627:0001` HIDs appeared, proving CocoaSPICE usbredir bypasses the Windows filter and requires a lower observation point | [Windows trace bench](../evidence/windows-trace-bench.md) | VERIFIED NEGATIVE INSTRUMENTATION |
| E-015 | TSView7 reads one byte per pixel from the bulk pipe using four overlapped lanes; five fixed modes range from 640x480 to 3664x2748 and have deterministically recovered chunk sizes | [TCA acquisition map](../evidence/tsview7-tca-acquisition-map.md) and offline geometry fixture | VERIFIED STATIC |
| E-016 | The first portable C17 frame-core slice reproduces the five mode geometries and assembles exact-length frames across arbitrary fragments while rejecting short/overflow cases; native macOS and Pi tests pass | [Offline frame-core verification](../evidence/offline-frame-core.md) | VERIFIED OFFLINE |
| E-017 | Byte-accurate x86 emulation of the matching TSView7 DLL confirms register addresses occupy `wIndex`, recovers the obfuscated `0x0a` fixed-mode writes, and passes deterministic golden tests without a host USB API | [TCA initialization emulation](../evidence/tsview7-tca-emulated-init.md) | VERIFIED EMULATED / NOT LIVE |
| E-018 | Portable C17 modules encode the corrected open/read/close records and all five fixed-mode initialization plans, then execute them through a fail-fast transport contract; golden and fault-injection tests cover all 154 writes and every mode-4 failure boundary on macOS and Pi without USB imports | [Offline protocol-plan verification](../evidence/offline-protocol-plan.md) | VERIFIED OFFLINE / NOT LIVE |
| E-019 | Emulated TSView7 conversion identifies GRBG-to-BGR24 memory conventions; a portable explicit-pattern decoder and exact-frame replay CLI pass macOS/Pi tests and feed a synthetic RGB24 stream into FFmpeg | [Offline image pipeline](../evidence/offline-image-pipeline.md) | VERIFIED OFFLINE / SYNTHETIC |
| E-020 | Static analysis and offline DLL emulation separate sensor controls from host processing, recover exposure units/limits, analog-gain encoding, and four frame-speed PLL plans; a portable C17 planner passes golden tests on macOS and Pi | [TCA control reconstruction](../evidence/tsview7-tca-controls.md) | VERIFIED OFFLINE / NOT LIVE |
| E-021 | Offline DLL execution confirms full-chunk requests, four-lane rotation, and the intentional final-remainder completion for every fixed mode; a portable staged scheduler matches those semantics and cancels all outstanding reads on every injected submit/completion/unexpected-length failure; sanitizer and native Pi tests pass without USB imports | [Offline capture scheduler](../evidence/offline-capture-scheduler.md) and [DLL emulation](../evidence/tsview7-tca-emulated-init.md) | VERIFIED EMULATED + OFFLINE / NOT LIVE |
| E-022 | The one-shot D40 harness pinned the reviewed v2 probe hash and captured before/after identity, kernel, safe-claim, raw result, status, and hashes after an owner-confirmed physical cold cycle | [Cold-session harness](../evidence/cold-probe-harness.md) | EXECUTED ONCE / VERIFIED |
| E-023 | On a new USB instance after physical cold power, corrected open/read/close all timed out; before/after descriptors and interface claims passed, identity was byte-identical, and no kernel fault occurred | [D40 physical-cold result](../evidence/d40-cold-result.md) | VERIFIED NEGATIVE / TERMINAL LINUX BRANCH |
| E-024 | With Secure Boot disabled only in the offline VM and Windows test mode active, the 2011 Tucsen driver reports `Started`; TSView7 discovers the camera and reaches a ready control window with resolution, snapshot, record, white-balance, exposure, and property controls | [Windows trace bench](../evidence/windows-trace-bench.md) | VERIFIED LIVE WINDOWS |
| E-025 | After Windows initialized the still-powered camera, macOS libusb captured exactly 307,200 bytes as 81,920 + 81,920 + 81,920 + 61,440; ten `0x88` marker bytes begin every block and GRBG replay yields the expected taped-sensor dark image | [Working Windows reference and direct host capture](../evidence/windows-reference-live-capture.md) | VERIFIED LIVE DATA PLANE |
| E-026 | The installed working `TS1000.dll` and `Tucsen64.sys` hashes match the analyzed purchase-era TCA pair, and the INF explicitly identifies `0547:c003` as TCA-10.0-N | [Working Windows reference and direct host capture](../evidence/windows-reference-live-capture.md) | VERIFIED LINEAGE |
| E-027 | Windows `usbip-win2` attached the camera and received valid descriptors, but its repeated 18-byte device-descriptor read timed out after 5.004272 seconds before `SET_CONFIGURATION`; the immutable usbmon capture is preserved and the transport branch is closed | [USB/IP result and VirtualHere fallback](../evidence/virtualhere-trace-bench.md) | VERIFIED NEGATIVE TRANSPORT |
| E-028 | Headless Ghidra 12.1.4 independently confirms the TCA command ABI, register read/write wrappers, four implemented driver IOCTLs, ordinary KMDF configuration, and split bulk-URB path; it finds no prepare-hardware firmware loader and shows ignored IOCTL `0x22208a` cannot hide a USB transaction | [Targeted Ghidra decompilation](../evidence/ghidra-targeted-decompilation.md) | VERIFIED STATIC / NOT LIVE |
| E-029 | A portable C17 startup module emits all 80 even-register validation reads and checks the extracted expected signature with deterministic first-mismatch reporting; tests pass on macOS and the Ubuntu ARM64 bench without USB imports | [Offline startup-signature core](../evidence/offline-startup-signature.md) | VERIFIED OFFLINE / NOT LIVE |
| E-030 | A 2014 UCL thesis documents exact-model TCA-10.0-N live view and 80-hour time-lapse use in Micro-Manager 1.4; the contemporary public adapter tree has generic TWAIN/OpenCV adapters but no legacy Tucsen-specific adapter, so the application precedent is verified while its transport path remains unresolved | [Historical Micro-Manager application precedent](../evidence/micromanager-application-precedent.md) | VERIFIED APPLICATION PRECEDENT / PATH OPEN |
| E-031 | The live-captured mode-4 Bayer8 frame was decoded and presented through a removable 640x480 YUYV V4L2 loopback on Ubuntu ARM64; v4l2-ctl and FFmpeg each consumed three exact-size frames across a remove/recreate cycle, and a packaged reader-core bridge reproduced the capture hash while refusing existing setups and cleaning up its device/module | [Linux V4L2 replay bridge](../evidence/linux-v4l2-replay-bridge.md) | VERIFIED APPLICATION BOUNDARY / REPLAY ONLY |
| E-032 | A transport-neutral C17 reader implements the planned lifecycle, exact frame/decode metadata, bounded latest/lossless queues, validated controls, structured diagnostics, fault/close/reopen, inspect, and replay; strict native tests pass on macOS and Ubuntu ARM64, sanitizer execution passes, and the live-captured fixture decodes byte-identically on both | [Portable reader session and CLI](../evidence/offline-reader-session.md) | VERIFIED OFFLINE CORE / COLD LIVE COMPLETION OPEN |
| E-033 | An opt-in libusb backend connects the portable reader to the previously verified warm mode-4 data plane; native ARM64 Linux and Apple Silicon binaries import only the exact descriptor/open/claim/release plus bulk-transfer allowlist, pass inert-token and fault-injection tests covering the exact schedule, short/zero/error paths, no-retry behavior, state guards, and partial raw preservation, and contain no control/reset/configuration/alternate-setting path; a separately token-gated Linux script is ready to feed decoded frames into a temporary V4L2 node while preserving raw bytes; live execution remains deferred until a known-good warm handoff exists | [Warm-state libusb reader backend](../evidence/warm-reader-backend.md) | VERIFIED BUILD + STATIC SAFETY / WARM LIVE RUN PENDING |
| E-034 | A separately compiled operable backend composes the warm reader with checked exposure, normalized-gain, and eleven-write/two-delay frame-speed plans; injected native tests on Apple Silicon and ARM64 Linux verify exact tuples, delays, configuration guards, fail-fast timeout/short/ack/sleep reporting, and no state update after a partial failed plan; a separately named inert-by-default CLI can apply exactly one prevalidated control and exit without starting acquisition; the read-only streaming binary remains unchanged and physical control execution is pending the known-good warm handoff | [Opt-in operable libusb control backend](../evidence/operable-control-backend.md) | VERIFIED OFFLINE CONTROL TRANSPORT + CLI / LIVE CONTROL PENDING |
| E-035 | A deterministic usbmon extractor correlates submit/completion URBs and preserves timing, setup fields, statuses, lengths, and payloads; synthetic vendor-control/bulk tests and the preserved USB/IP capture pass on macOS and ARM64 Linux, with the latter independently reproducing ten standard-control pairs, one 5.004272-second `-104` failure, no vendor request, and no bulk transfer | [Deterministic usbmon trace extractor](../evidence/usbmon-trace-extractor.md) | VERIFIED OFFLINE TRACE ANALYSIS / VIRTUALHERE CAPTURE PENDING |
| E-036 | The official 2026 AmScope ARM64 Linux and Windows packages were downloaded project-locally, hash-pinned, and extracted without execution; neither tree names C003/TCA/IS1000, both current 232-entry Windows INFs omit `0547:c003`, and no standalone firmware/updater file was found; the Linux package's vendor-wide udev rule is permission evidence only, not a compatibility claim | [Updated-firmware discovery](../evidence/firmware-discovery.md) | VERIFIED STATIC NEGATIVE / NON-GATING |
| E-037 | A USB-inert semantic stage consumes only paired trace TSV, labels recovered TCA open/close/state/read/write and endpoint-`0x82` bulk events, reverses write XOR encoding, decodes big-endian read values, validates status/length/acknowledgement, and preserves unknown vendor requests as unclassified; synthetic tests pass and the USB/IP negative trace remains ten standard controls with one transport error | [Deterministic usbmon extractor and TCA annotator](../evidence/usbmon-trace-extractor.md) | VERIFIED OFFLINE TRACE SEMANTICS / VIRTUALHERE CAPTURE PENDING |
| E-038 | A USB-free C generator composes the existing open, 80-read signature, and fixed-mode plans into a 120-control mode-4 Ready expectation; a deterministic TSV comparator aligns captured controls and validates response patterns without generating USB operations; strict tests and the USB/IP negative-trace comparison are byte-identical on Apple Silicon and AArch64 Linux | [Modeled TCA trace plan and comparator](../evidence/tca-trace-plan-comparator.md) | VERIFIED OFFLINE COMPARISON / SUCCESSFUL TRACE PENDING |
| E-039 | Both post-reboot UTM USB paths failed without harming enumeration; the camera was moved cold to `rpios-17`, where exact-device identity, `usbmon3`, pinned VirtualHere inputs, and Windows-side discovery through the UTM gateway relay are live; the v4 handoff ISO removes boot-specific addressing and verifies its embedded sources byte-for-byte | [VirtualHere fallback trace bench](../evidence/virtualhere-trace-bench.md) | VERIFIED LIVE INFRASTRUCTURE / DEVICE ATTACH PENDING |
| E-040 | The completed Windows reference capture contains 744 paired operations (25 standard controls, 191 vendor controls, 528 bulk transfers), no pairing gaps, and no semantic validation issue; it exposes the seven-command cold-start sequence and three-read 1280×960 frame schedule | Preserved VirtualHere session under `work/trace-captures/virtualhere-session-pi-20261003T120230Z/` | VERIFIED LIVE REFERENCE TRACE |
| E-041 | Native ARM64 Linux reproduces only those seven startup commands, accepts their trace-confirmed stalled IN data stages, validates three `0x88` markers per frame, streams continuous 1280×960 Bayer8, and applies bounded exposure/gain writes without Windows or a camera-specific kernel driver | Report current milestone and [public validation](../evidence/public-release-live-validation.md) | VERIFIED LIVE LINUX COLD START + CONTROLS |
| E-042 | A foreground bridge converts the live physical Bayer stream to a temporary 1280×960 YUYV V4L2 device; `v4l2-ctl` reports the intended format, FFmpeg consumes three frames, and cleanup removes only the loopback created for the session | Report current milestone and V4L2 work bundle | VERIFIED LIVE APPLICATION BOUNDARY |
| E-043 | The exact public reader commit passes a 30-frame controlled capture, ten independent open/init/ten-frame/close processes (100/100 frames), and a 14,400-frame/2,410-second continuous run with flat sampled memory; Ubuntu and macOS CI pass | [Public release live validation](../evidence/public-release-live-validation.md) | VERIFIED REOPEN + ENDURANCE |
| E-044 | Recovered selector `b4/c0`, 3664×2748 geometry, and formula `((pixels >> 9) + 1) << 9` predicted a 10,068,992-byte frame; the guarded physical probe received that exact length with all twenty markers, and mode-2 recovery captured three frames | [Guarded full-resolution probe](../evidence/full-resolution-probe.md) | VERIFIED LIVE FULL RESOLUTION + RECOVERY |
| E-045 | The public two-mode reader candidate captured three consecutive frames in mode 0 and then mode 2 with exact raw/application byte counts; its mode-aware exposure conversion programmed 324 and 834 lines respectively at 100 ms | [Public release live validation](../evidence/public-release-live-validation.md) | VERIFIED LIVE PUBLIC READER BOTH MODES |
| E-046 | Exact tag `v0.2.0-alpha.1` was terminated with `SIGKILL` during mode-2 capture after its complete first-frame flush; without a USB reset or power cycle, a new tagged process immediately reopened and captured three frames | [Public release live validation](../evidence/public-release-live-validation.md) | VERIFIED PROCESS-DEATH RECOVERY |
| E-047 | Official stable 2026 and legacy 2025 ToupCam SDK packages support Linux/macOS/Windows and ship Python bindings, but their 1,768- and 1,600-pair explicit Windows USB tables omit `0547:c003`; the Python module is a thin proprietary-library wrapper and the vendor-wide Linux udev rule is permission evidence, not device support | [Existing Linux driver candidates](../evidence/existing-linux-driver-candidates.md) | VERIFIED STATIC NEGATIVE / API INSPIRATION |
| E-048 | Micro-Manager's AmScope adapter is Windows-only MU-series/ToupCam code for a different family, while its Linux Video4Linux adapter matches the project's proven YUYV loopback; Pycro-Manager can add acquisition/stage automation only above a working MMCore adapter, and Fiji/MIST remain downstream tile-stitching candidates | [Microscopy application stack](../evidence/microscopy-application-stack.md) | VERIFIED ARCHITECTURE / LIVE MM TEST PENDING |
| E-049 | With the camera connected, a controlled Pi reboot changed the Linux boot ID and USB device instance; public main commit `71fdae1` rebuilt and passed its tests, then cold-opened the re-enumerated `0547:c003` camera and captured three exact-size mode-2 frames with controls and exit zero | [Public release live validation](../evidence/public-release-live-validation.md) | VERIFIED LIVE HOST-REBOOT RECOVERY |
| E-050 | A line-by-line readiness audit distinguishes the useful Linux alpha from final acceptance: streaming, reader/API, Linux application bridge, portable macOS reader, and the non-functional requirements pass, while physical cable reconnect and optical/color checks remain open | [Release acceptance audit](../evidence/release-acceptance-audit.md) | VERIFIED AUDIT; EXIT OPEN |
| E-051 | The Apple Silicon public reader cold-initialized the physical `0547:c003` camera through a one-device Pi relay, applied exposure and gain, captured three exact-size mode-2 frames, and exited zero | [Apple Silicon relay validation](../evidence/macos-virtualhere-live-validation.md) | VERIFIED LIVE MACOS READER |
| E-052 | Returning ownership from macOS to Linux reproduced one marker-invalid leading warm-up frame; public alpha-2 preserved it once, discarded it under a two-frame limit, delivered three valid frames in the same process, and kept later marker loss fatal | [Apple Silicon relay validation](../evidence/macos-virtualhere-live-validation.md) | VERIFIED BOUNDED HAND-BACK RECOVERY |
| E-053 | Public commit `a61c044` adds a no-dependency Bayer statistics/focus utility and reproducible microscope procedure; Ubuntu/macOS CI passed, the exact Pi commit passed every test, and a fresh physical covered-sensor capture produced exact mode-2 byte counts, `frames=1 status=ok`, and a valid JSON analysis | [Optical validation tooling](../evidence/optical-validation-tooling.md) | VERIFIED TOOLING + LIVE DARK-FRAME ANALYSIS / OPTICS OPEN |
| E-054 | Public commit `fb502c1` installs and removes exactly the reader, V4L2 helper, and frame analyzer under `PREFIX`/`DESTDIR`; a staged test proves an unrelated same-directory sentinel survives, and the complete suite passes on Apple Silicon, the Pi, Ubuntu CI, and macOS CI | [Package operations](../evidence/package-operations.md) | VERIFIED INSTALL/REMOVE OPERATIONS |
| E-055 | Annotated public prerelease `v0.2.0-alpha.3` resolves to commit `3c16d2a`; independent main/tag Ubuntu and macOS CI runs pass, the downloaded public source archive passes every test outside a Git checkout, and the exact-tag Pi build passed every test before a controlled physical mode-2 capture and analysis completed with exact byte counts and exit zero | [Public alpha-3 release](../evidence/public-release-alpha3.md) | VERIFIED PUBLIC ARCHIVE + EXACT-TAG LIVE CAPTURE |
| E-056 | An inert exact-alpha-3 reconnect harness is staged on the Pi, requires observation of device count zero before re-enumeration, and will verify a three-frame capture, exact sizes/status, first-frame analysis, and evidence hashes without reset, deauthorization, or speculative control requests | [Physical reconnect harness](../evidence/physical-reconnect-harness.md) | PREPARED + INERT-VERIFIED / PHYSICAL ACTION OPEN |
| E-057 | Exact public alpha-3 on Apple Silicon directly claimed USB `0547:c003`, applied gain/exposure, captured three preview frames, one full-resolution frame, and a fresh-process preview reopen with exact sizes and analysis; the first cold-attach invocation failed closed on a single one-byte control response before all subsequent startup controls returned the reference stall | [Native-cable Apple Silicon validation](../evidence/macos-native-cable-validation.md) | VERIFIED DIRECT READER / COLD-ATTACH TRANSIENT RECORDED |
| E-058 | Microscope imagery and 0.983 autocorrelation at a 524,288-byte lag exposed the old multi-request assembly error; single-request probes proved one prefix per complete record and yielded coherent 1280x960 and 3664x2748 images | [Optical frame-layout correction](../evidence/first-optical-capture.md) | VERIFIED LIVE OPTICAL / READER CORRECTED |
| E-059 | At 100 ms, corrected gain 0..320 produced monotonic mean intensity 14.67..154.88; gain 256 yielded negligible clipping, and a 16-frame run produced 16 distinct hashes plus multi-resolution PNGs and an H.264 proof clip | [Optical frame-layout correction](../evidence/first-optical-capture.md) | VERIFIED LIVE CONTROLS + MOTION SEQUENCE |
| E-060 | Mode-0 record N `[512,end)` plus record N+1 `[320,512)` produced three distinct complete 3664x2748 frames without the false left strip; neutral slide regions independently yielded approximately R/G/B `0.87/1.0/2.0` in both modes | [Optical frame-layout correction](../evidence/first-optical-capture.md) | VERIFIED LIVE FULL-FRAME ASSEMBLY + IN-SITU WHITE BALANCE |
| E-061 | After a change to 10x made the old settings nearly fully clipped, a gain-zero sweep found an unclipped 250-ms preview and complete full-resolution still; public alpha-6 at commit `0fded6e` emits ratio-preserving FFmpeg-safe white-balance gains | [Optical capture and 10x recovery](../evidence/first-optical-capture.md) | VERIFIED LIVE OPTICAL RECOVERY + RELEASE |
| E-062 | Exact public alpha-6 builds and passes every test on `rpios-17`; a synthetic 1280x960 YUYV producer/consumer preflight passed six exact frames through the generic loopback and cleaned it up, and a static-tested inert harness is staged to verify both optical modes plus six ordinary V4L2-consumed camera frames after the cable move | [Pi alpha-6 optical preparation](../evidence/pi-alpha6-linux-optical-preparation.md) | GENERIC V4L2 VERIFIED + CAMERA HARNESS PREPARED / CAMERA MOVE OPEN |
| E-063 | Equal 256x192 regions in the 10x blank-field preview range from mean luma 134.0 at bottom-left to 193.9 at top-middle, showing asymmetric field nonuniformity rather than simple radial falloff; an optical alignment/isolation checklist and calibrated per-Bayer-plane dark/flat correction are now specified | [Field illumination correction](../evidence/field-illumination-correction.md) | MEASURED DIAGNOSIS + CORRECTION PLAN |

## Risk Register

| Risk | Likelihood / impact | Mitigation and decision point |
|---|---|---|
| A vendor-IN request mutates hidden device state | <span class="risk-medium">Medium / High</span> | Call-context classification, dry-run binary, one bounded request, cold-session repetition, power-cycle recovery |
| Initialization depends on undiscovered timing or state | <span class="risk-medium">Medium / High</span> | Prefix experiments, explicit state model, targeted Windows/QEMU trace only if static work stalls |
| Frame format is proprietary or calibrated | <span class="risk-medium">Medium / High</span> | Preserve raw frames, compare modes, inspect decoder exports/tables, separate transport success from decode success |
| USB 2.0 limits full-resolution frame rate | <span class="risk-high">High / Medium</span> | Treat full resolution as still; select and measure a separate preview mode |
| macOS system-wide camera integration is signing-heavy | <span class="risk-medium">Medium / Medium</span> | Prove core and AVFoundation first; keep Linux standard bridge and direct API independently useful |
| Camera hardware is intermittent after long storage | <span class="risk-low">Low / High</span> | Cold-start repetitions, cable/power control, no hidden retries, compare failures across hosts |
| Vendor evidence cannot be redistributed | <span class="risk-high">High / Medium</span> | Publish original code and derived protocol facts; keep vendor files and disassembly private |
| Engineering cost exceeds replacement value | <span class="risk-medium">Medium / Medium</span> | Reassess after G3 and G5; continue only for learning, optics, preservation, or accepted utility |

## Open Decisions

1. What driver-local side effect, prerequisite transaction, or protocol
   difference explains why the corrected TCA prefix times out even from a
   proven physical cold start?
2. Which of the recovered fixed modes are accepted by this exact unit, and
   which mode should be the preview default?
3. What are the Bayer pattern, orientation, optical-black/crop requirements,
   and color calibration requirements for the recovered one-byte-per-pixel
   stream?
4. What are the exact user-facing normalization and persistence semantics for
   host-side RGB gain, gamma, contrast, saturation, white balance, mirrors,
   monochrome, and 50/60 Hz processing? The hardware exposure, analog-gain,
   and four-value frame-speed plan is recovered offline but not yet live-tested.
5. Is a Linux V4L2 loopback path sufficient for first application acceptance,
   or is system-wide macOS discovery required in the same release?
6. Does the user-space core meet measured throughput without platform-specific
   USB scheduling or a kernel component?

## Planning Completion Checklist

- [x] Objective and Definition of Done are explicit.
- [x] Existing observed evidence is separated from inference.
- [x] Product use cases and requirements cover still, stream, controls,
  applications, and recovery.
- [x] User-space core and platform-adapter boundaries are defined.
- [x] Safety gates prohibit guessed USB operations.
- [x] Dependency graph has one start, one exit, and complete reachability.
- [x] Every task has preconditions, postconditions, rollback, and proof.
- [x] Acceptance authority has approved this plan for execution beyond D20.
- [x] First live vendor request was selected, reviewed, bounded, and preserved
  as negative evidence.

> **Current recommendation:** stop varying Linux vendor requests. The physical-
> cold corrected prefix timed out safely and decisively. The isolated Windows
> bench, legacy driver, and TSView camera path now work; use the corrected
> exact-only VirtualHere v4 handoff to record a fresh attach and control
> session below Pi `usbmon3`. The physical Pi bench, gateway relay, Windows
> discovery, and pinned inputs are live; exact `USE` followed by one TSView
> start is the next live action.
> Independently prove the removable Linux V4L2/media application boundary with
> replay frames, using Micro-Manager as a later real-application target. Continue
> static frame/decoder analysis while capture is unavailable; firmware
> discovery remains non-gating.

</main>
