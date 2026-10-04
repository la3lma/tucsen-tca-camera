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
  <a href="https://la3lma.github.io/tucsen-tca-camera/evidence/">Evidence index</a>
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
  <span class="status-chip">Delivered cadence measured</span>
  <span class="status-chip">V4L2 application path verified</span>
  <span class="status-chip">Evidence site rendered + privacy-gated</span>
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
blank region now provides reproducible in-situ white balance. Direct-Mac
delivery cadence is now measured in both recovered modes. The next gate is a
true blocked-light dark plus blank-field flat at locked settings, a known
color target, and a live post-fix V4L2 run on Linux with consumer-side cadence
and drop accounting.
An inert-by-default guided session now locks settings and prompts for each
blocked-dark, repositioned-flat, fresh-blank, and real-specimen state while
preserving exact artifacts and a manifest.

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
| Revision | 3.4, use cases expressed in Cockburn form and UML; delivered-frame cadence measured in both recovered modes; public evidence rendered as HTML and guarded by a permanent full-history privacy policy |
| Execution state | D00–D50 are complete and D60 is substantially advanced. Optical autocorrelation showed that separate 524,288-byte requests restarted at new record origins, causing the earlier repeated regions and false seam. Mode 2 fits after a 512-byte prefix. Mode 0 is assembled from record N `[512,end)` plus the 192-byte continuation at record N+1 `[320,512)`. Three consecutive full-resolution frames have distinct hashes and no false left strip. At 100 ms, gain 0..320 is monotonic; gain 256 produced a bright frame with negligible clipping. One pre-control buffered record is consumed before frame zero. A 16-frame run yielded distinct frames, three still sizes, and a 640x480 H.264 proof clip. Neutral-background white balance independently produced approximately R/G/B `0.87/1.0/2.0` in both modes; alpha-6 preserves those ratios when normalizing into FFmpeg's multiplier range. After changing to 10x, a bounded sweep recovered unclipped preview and full-resolution stills at 250 ms/gain 0. Public commit `1dc096b` adds a portable per-pixel dark/flat corrector and optional corrected V4L2 path; commit `6eb68a7` binds maps to exposure/gain and fails before camera or loopback mutation on mismatch. A real-camera diagnostic corrected eight full-size frames, reducing a 3x3 max/min region ratio from 1.336910 to 1.001023, while deliberately proving that a self-flat erases the specimen and is not a valid calibration. Public commit `176ef90` packages the correct physical calibration sequence. Public commit `064cf31` adds monotonic per-frame timestamps and reports 17.3466 delivered fps for 1280x960 at requested 1 ms, 9.5057 fps for 1280x960 at 250 ms, and 2.7911 fps for 3664x2748 at 250 ms on the direct-Mac/file-output path. The same commit renders all public evidence as navigable HTML and enforces a full-history ban on raw disassembly, vendor binaries, firmware, traces, and private work. Final known-target Bayer/color calibration, true blocked-light dark and blank-field flat execution, and execution of the live-camera Linux V4L2 gate with consumer-side timing remain open. AVFoundation remains deferred. |
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

The live Agency `docstack` forum was consulted for this revision. Standing
conventions applied here include Cockburn use-case fields (message 126), one
validated start/exit with every task on a complete path (141), clickable graph
nodes targeting stable local task anchors (120--121), full-width/overview/detail
diagram modes (142), complete-green/active-orange/blocked-red/neutral waiting
states (143), and reciprocal upstream/downstream task links (144).

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

The diagram gives the familiar system boundary; the tables beneath it use a
compact Cockburn form. “Microscope” means the specimen, illumination, optics,
and manual focus/magnification path. It does not imply a motorized microscope.

<div class="diagram-shell uml-shell" role="img" aria-label="UML use-case diagram for microscope camera operation">
<svg viewBox="0 0 1120 610" xmlns="http://www.w3.org/2000/svg">
  <rect class="system-boundary" x="245" y="28" width="635" height="554" rx="8"/>
  <text class="boundary-label" x="265" y="57">TCA camera reader system</text>
  <circle class="actor-line" cx="92" cy="120" r="19"/><path class="actor-line" d="M92 139v68M55 164h74M92 207l-35 55M92 207l35 55"/>
  <text class="label" x="92" y="290" text-anchor="middle">Microscope operator</text>
  <rect class="actor-box" x="20" y="376" width="145" height="66" rx="6"/>
  <text class="label" x="92" y="404" text-anchor="middle">Scientific</text><text class="label" x="92" y="426" text-anchor="middle">application</text>
  <rect class="actor-box target" x="952" y="102" width="145" height="66" rx="6"/>
  <text class="label" x="1024" y="130" text-anchor="middle">Microscope</text><text class="small" x="1024" y="151" text-anchor="middle">optical path</text>
  <rect class="actor-box target" x="952" y="400" width="145" height="66" rx="6"/>
  <text class="label" x="1024" y="429" text-anchor="middle">USB camera</text><text class="small" x="1024" y="450" text-anchor="middle">0547:c003</text>
  <ellipse class="usecase" cx="425" cy="125" rx="125" ry="47"/><text class="label" x="425" y="121" text-anchor="middle">UC1 Inspect</text><text class="small" x="425" y="144" text-anchor="middle">and identify</text>
  <ellipse class="usecase" cx="690" cy="125" rx="125" ry="47"/><text class="label" x="690" y="121" text-anchor="middle">UC2 Capture</text><text class="small" x="690" y="144" text-anchor="middle">full-resolution still</text>
  <ellipse class="usecase" cx="425" cy="275" rx="125" ry="47"/><text class="label" x="425" y="271" text-anchor="middle">UC3 Stream</text><text class="small" x="425" y="294" text-anchor="middle">responsive preview</text>
  <ellipse class="usecase" cx="690" cy="275" rx="125" ry="47"/><text class="label" x="690" y="271" text-anchor="middle">UC4 Operate</text><text class="small" x="690" y="294" text-anchor="middle">camera controls</text>
  <ellipse class="usecase" cx="425" cy="425" rx="125" ry="47"/><text class="label" x="425" y="421" text-anchor="middle">UC5 Use in</text><text class="small" x="425" y="444" text-anchor="middle">ordinary application</text>
  <ellipse class="usecase" cx="690" cy="425" rx="125" ry="47"/><text class="label" x="690" y="421" text-anchor="middle">UC6 Recover</text><text class="small" x="690" y="444" text-anchor="middle">from interruption</text>
  <path class="association" d="M130 160L315 125M130 188L565 125M130 207L315 275M130 225L565 275M165 409L300 425"/>
  <path class="association" d="M952 135L815 125M952 151L550 275"/>
  <path class="association" d="M952 433L815 425M952 421L815 275M952 445L550 425M952 457L550 125"/>
</svg>
</div>

### UC1 — Inspect and identify

| Cockburn field | Specification |
|---|---|
| Scope / level | TCA reader system / user goal |
| Primary actor | Microscope operator or support engineer |
| Stakeholders | Operator wants an exact identity and safe next action; camera must receive no discovery-time vendor traffic |
| Preconditions | Camera is connected, or an offline diagnostic bundle is supplied |
| Trigger | Actor requests inspection or diagnostics |
| Main success scenario | 1. Reader enumerates USB. 2. It selects only the requested `0547:c003`. 3. It reports path, speed, descriptors, permissions, endpoint topology, reader version, and proven capabilities. 4. It proposes only supported next operations. |
| Extensions | Missing permission, ambiguous multiple devices, or absent camera produces a specific diagnostic and no mutation |
| Success guarantee | Identity and capability report is complete; no vendor-specific request or bulk transfer occurred |

### UC2 — Capture one full-resolution still

| Cockburn field | Specification |
|---|---|
| Scope / level | Reader plus microscope optical path / user goal |
| Primary actor | Microscope operator |
| Stakeholders | Operator wants one faithful image; reviewer wants untouched raw evidence and declared settings |
| Preconditions | Camera is identified; specimen, illumination, focus, mode, exposure, and gain are selected |
| Trigger | Operator requests a full-resolution still |
| Main success scenario | 1. Reader claims and cold-initializes the camera. 2. It applies the proven mode and controls. 3. Camera returns complete records. 4. Reader assembles and validates exactly one frame. 5. It stores raw frame, timestamp, settings, hash, and decoded image. 6. It stops and releases the device. |
| Extensions | Short or ambiguous data is retained as failed evidence and is never labelled a successful image; unsupported settings fail before USB traffic |
| Success guarantee | One complete 3664x2748 Bayer frame and reproducible decoded derivative are preserved |

<div class="diagram-shell sequence-shell" role="img" aria-label="Sequence diagram for full-resolution still capture">
<svg viewBox="0 0 1100 560" xmlns="http://www.w3.org/2000/svg">
  <defs><marker id="seq-arrow-still" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker></defs>
  <g class="sequence-participant"><rect x="25" y="20" width="150" height="55" rx="5"/><text x="100" y="53" text-anchor="middle">Operator</text><rect x="245" y="20" width="150" height="55" rx="5"/><text x="320" y="53" text-anchor="middle">Microscope</text><rect x="475" y="20" width="150" height="55" rx="5"/><text x="550" y="53" text-anchor="middle">Reader</text><rect x="705" y="20" width="150" height="55" rx="5"/><text x="780" y="53" text-anchor="middle">USB camera</text><rect x="925" y="20" width="150" height="55" rx="5"/><text x="1000" y="53" text-anchor="middle">Artifact store</text></g>
  <path class="lifeline" d="M100 75V535M320 75V535M550 75V535M780 75V535M1000 75V535"/>
  <path class="message" marker-end="url(#seq-arrow-still)" d="M100 115H320"/><text class="message-label" x="210" y="105" text-anchor="middle">place specimen; light; focus</text>
  <path class="message" marker-end="url(#seq-arrow-still)" d="M100 175H550"/><text class="message-label" x="325" y="165" text-anchor="middle">capture(mode 0, exposure, gain)</text>
  <path class="message" marker-end="url(#seq-arrow-still)" d="M550 235H780"/><text class="message-label" x="665" y="225" text-anchor="middle">claim; initialize; apply controls</text>
  <path class="message return" marker-end="url(#seq-arrow-still)" d="M780 295H550"/><text class="message-label" x="665" y="285" text-anchor="middle">complete bulk records</text>
  <rect class="activation" x="540" y="315" width="20" height="75"/><text class="message-label" x="575" y="345">assemble + validate</text><text class="message-label" x="575" y="367">decode + hash</text>
  <path class="message" marker-end="url(#seq-arrow-still)" d="M550 420H1000"/><text class="message-label" x="775" y="410" text-anchor="middle">raw + metadata + image</text>
  <path class="message return" marker-end="url(#seq-arrow-still)" d="M550 485H100"/><text class="message-label" x="325" y="475" text-anchor="middle">success and artifact paths</text>
</svg>
</div>

### UC3 — Stream a preview

| Cockburn field | Specification |
|---|---|
| Scope / level | Reader and selected application adapter / user goal |
| Primary actor | Microscope operator or scientific application |
| Stakeholders | Operator wants responsive composition/focus; application wants declared format and timing; camera needs bounded transfers |
| Preconditions | Device and preview mode are proven; one consumer and a queue/drop policy are selected |
| Trigger | Actor starts preview |
| Main success scenario | 1. Reader initializes mode 2. 2. It publishes validated timestamped frames in the declared format. 3. Operator adjusts the microscope while observing feedback. 4. Reader reports cadence, drops, and faults. 5. Actor stops; reader drains and releases cleanly. |
| Extensions | Disconnect, repeated short reads, or parser loss enters bounded recovery; a slow consumer follows the declared drop/back-pressure policy |
| Success guarantee | Every delivered frame is complete and attributable; stop does not strand the camera |

### UC4 — Operate camera controls

| Cockburn field | Specification |
|---|---|
| Scope / level | Reader control surface / subfunction supporting capture and preview |
| Primary actor | Microscope operator or application |
| Stakeholders | Operator wants predictable brightness; developer wants only evidence-backed writes; microscope specimen must not be confused with control effects |
| Preconditions | Camera is initialized; control, units, and safe range are advertised |
| Trigger | Actor reads or changes exposure or gain |
| Main success scenario | 1. Reader reports current value and range. 2. Actor requests an in-range value. 3. Reader executes the proven write plan. 4. It discards the known buffered pre-control record. 5. A read-back or changed frame verifies effect. 6. Metadata carries the applied value. |
| Extensions | Unknown, out-of-range, or unsafe operations are rejected before USB traffic; unverifiable writes are reported as provisional, not successful |
| Success guarantee | Applied state and resulting frame association are explicit |

<div class="diagram-shell sequence-shell" role="img" aria-label="Sequence diagram for preview and control interaction">
<svg viewBox="0 0 1100 650" xmlns="http://www.w3.org/2000/svg">
  <defs><marker id="seq-arrow-preview" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker></defs>
  <g class="sequence-participant"><rect x="25" y="20" width="150" height="55" rx="5"/><text x="100" y="53" text-anchor="middle">Operator</text><rect x="245" y="20" width="150" height="55" rx="5"/><text x="320" y="53" text-anchor="middle">Application</text><rect x="475" y="20" width="150" height="55" rx="5"/><text x="550" y="53" text-anchor="middle">V4L2 adapter</text><rect x="705" y="20" width="150" height="55" rx="5"/><text x="780" y="53" text-anchor="middle">Reader</text><rect x="925" y="20" width="150" height="55" rx="5"/><text x="1000" y="53" text-anchor="middle">USB camera</text></g>
  <path class="lifeline" d="M100 75V625M320 75V625M550 75V625M780 75V625M1000 75V625"/>
  <path class="message" marker-end="url(#seq-arrow-preview)" d="M320 120H550"/><text class="message-label" x="435" y="110" text-anchor="middle">open preview</text>
  <path class="message" marker-end="url(#seq-arrow-preview)" d="M550 175H780"/><text class="message-label" x="665" y="165" text-anchor="middle">start(mode 2)</text>
  <path class="message" marker-end="url(#seq-arrow-preview)" d="M780 230H1000"/><text class="message-label" x="890" y="220" text-anchor="middle">initialize + start</text>
  <rect class="sequence-frame" x="290" y="260" width="745" height="145" rx="4"/><text class="frame-label" x="305" y="282">loop complete frames</text>
  <path class="message return" marker-end="url(#seq-arrow-preview)" d="M1000 315H780"/><text class="message-label" x="890" y="305" text-anchor="middle">bulk record</text>
  <path class="message return" marker-end="url(#seq-arrow-preview)" d="M780 355H550"/><text class="message-label" x="665" y="345" text-anchor="middle">timestamped YUYV</text>
  <path class="message return" marker-end="url(#seq-arrow-preview)" d="M550 390H320"/><text class="message-label" x="435" y="380" text-anchor="middle">frame + cadence status</text>
  <path class="message" marker-end="url(#seq-arrow-preview)" d="M100 455H780"/><text class="message-label" x="440" y="445" text-anchor="middle">set exposure/gain</text>
  <path class="message" marker-end="url(#seq-arrow-preview)" d="M780 505H1000"/><text class="message-label" x="890" y="495" text-anchor="middle">proven bounded writes</text>
  <path class="message return" marker-end="url(#seq-arrow-preview)" d="M780 555H100"/><text class="message-label" x="440" y="545" text-anchor="middle">applied value + verified frame</text>
  <path class="message" marker-end="url(#seq-arrow-preview)" d="M320 605H780"/><text class="message-label" x="550" y="595" text-anchor="middle">close; drain; release</text>
</svg>
</div>

### UC5 — Use the camera in an ordinary application

| Cockburn field | Specification |
|---|---|
| Scope / level | OS camera adapter / user goal |
| Primary actor | Scientific application |
| Stakeholders | Application wants a standard source; operator wants no USB knowledge; reader must remain the only protocol owner |
| Preconditions | Reader works directly; adapter advertises a supported format and resolution; permissions are satisfied |
| Trigger | Application opens the virtual or standard camera source |
| Main success scenario | 1. Adapter starts one reader session. 2. It converts complete frames without duplicating protocol logic. 3. Application negotiates and receives frames. 4. Controls remain available through the declared surface. 5. Application closes; adapter and reader clean up. |
| Extensions | Unsupported negotiation fails explicitly; application crash is detected and resources are released for the next session |
| Success guarantee | A named ordinary application consumes real camera frames and later sessions still work |

### UC6 — Recover from interruption

| Cockburn field | Specification |
|---|---|
| Scope / level | Reader lifecycle / user goal |
| Primary actor | Microscope operator; interruption is the initiating event |
| Stakeholders | Operator wants a short, safe path back to capture; support engineer wants the last proven state and cause |
| Preconditions | A reader operation is active or has failed; recovery policy is bounded |
| Trigger | Unplug, USB reset, timeout, parser loss, process exit, or application crash |
| Main success scenario | 1. Reader records the fault and last proven state. 2. It cancels/drains transfers and releases resources. 3. On reappearance it matches the exact device path or explicit selection. 4. It performs the full initialization sequence. 5. It resumes only after a newly validated frame. |
| Extensions | If recovery budget expires, reader exits with a specific repair action; it never retries forever or guesses a reset/write sequence |
| Success guarantee | Camera is either usable through a fresh proven session or safely released with actionable diagnostics |

<div class="diagram-shell sequence-shell" role="img" aria-label="Sequence diagram for bounded recovery after interruption">
<svg viewBox="0 0 1040 600" xmlns="http://www.w3.org/2000/svg">
  <defs><marker id="seq-arrow-recovery" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker></defs>
  <g class="sequence-participant"><rect x="35" y="20" width="160" height="55" rx="5"/><text x="115" y="53" text-anchor="middle">Operator / app</text><rect x="300" y="20" width="160" height="55" rx="5"/><text x="380" y="53" text-anchor="middle">Reader</text><rect x="565" y="20" width="160" height="55" rx="5"/><text x="645" y="53" text-anchor="middle">USB subsystem</text><rect x="830" y="20" width="160" height="55" rx="5"/><text x="910" y="53" text-anchor="middle">Camera</text></g>
  <path class="lifeline" d="M115 75V575M380 75V575M645 75V575M910 75V575"/>
  <path class="message return" marker-end="url(#seq-arrow-recovery)" d="M910 125H645"/><text class="message-label" x="777" y="115" text-anchor="middle">disconnect / timeout</text>
  <path class="message return" marker-end="url(#seq-arrow-recovery)" d="M645 175H380"/><text class="message-label" x="512" y="165" text-anchor="middle">bounded transfer failure</text>
  <rect class="activation" x="370" y="195" width="20" height="90"/><text class="message-label" x="405" y="225">record state</text><text class="message-label" x="405" y="247">cancel, drain, release</text>
  <path class="message return" marker-end="url(#seq-arrow-recovery)" d="M380 315H115"/><text class="message-label" x="247" y="305" text-anchor="middle">recovering / specific diagnosis</text>
  <path class="message" marker-end="url(#seq-arrow-recovery)" d="M115 370H645"/><text class="message-label" x="380" y="360" text-anchor="middle">camera reconnected or retry requested</text>
  <path class="message" marker-end="url(#seq-arrow-recovery)" d="M380 425H645"/><text class="message-label" x="512" y="415" text-anchor="middle">match exact device; claim</text>
  <path class="message" marker-end="url(#seq-arrow-recovery)" d="M380 475H910"/><text class="message-label" x="645" y="465" text-anchor="middle">full proven initialization</text>
  <path class="message return" marker-end="url(#seq-arrow-recovery)" d="M910 525H380"/><text class="message-label" x="645" y="515" text-anchor="middle">new complete validated frame</text>
  <path class="message return" marker-end="url(#seq-arrow-recovery)" d="M380 565H115"/><text class="message-label" x="247" y="555" text-anchor="middle">session restored</text>
</svg>
</div>

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

## Dependency Graph {#dependency-graph}

Arrows run from prerequisite to dependent. D80 and D90 branch after the core
reader and converge at D100; the owner-approved macOS application deferral is
the recorded D90 output for this Linux-first release. Select any node to jump
to its task contract. Each contract links back here and to its immediate graph
neighbors.

<div class="plan-graph-wrap">
<div class="plan-graph-toolbar" role="group" aria-label="Dependency graph controls">
  <button type="button" data-graph-action="fit-width" aria-pressed="true">Fit width</button>
  <button type="button" data-graph-action="fit-diagram" aria-pressed="false">Fit diagram</button>
  <button type="button" data-graph-action="actual" aria-pressed="false">Actual size</button>
  <button type="button" data-graph-action="fullscreen" aria-pressed="false">Full screen</button>
  <span class="legend" aria-label="Task state legend">
    <span class="complete"><i></i>Complete</span>
    <span class="active"><i></i>Active</span>
    <span class="blocked"><i></i>Blocked</span>
    <span class="proposed"><i></i>Proposed/deferred</span>
  </span>
</div>
<div class="diagram-shell plan-graph" data-graph-mode="fit-width" role="img" aria-label="Clickable dependency graph from D00 start to D120 exit">
<svg viewBox="0 0 1220 1510" xmlns="http://www.w3.org/2000/svg">
  <defs><marker id="plan-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker></defs>
  <path class="graph-edge" d="M610 130V170M610 260V300M610 390V430M610 520V560M610 650V690M610 780V820M610 910V950"/>
  <path class="graph-edge" d="M610 1040V1080H350V1110M610 1040V1080H870V1110"/>
  <path class="graph-edge" d="M350 1200V1230H610V1260M870 1200V1230H610V1260M610 1350V1368H350V1390"/>
  <a class="graph-node complete" href="#d00"><rect x="430" y="40" width="360" height="90" rx="8"/><text class="node-id" x="450" y="69">D00 · START</text><text class="node-label" x="610" y="96" text-anchor="middle">Preserve physical and USB baseline</text><text class="node-state" x="770" y="119" text-anchor="end">COMPLETE</text></a>
  <a class="graph-node complete" href="#d10"><rect x="430" y="170" width="360" height="90" rx="8"/><text class="node-id" x="450" y="199">D10</text><text class="node-label" x="610" y="226" text-anchor="middle">Separate Windows transport generations</text><text class="node-state" x="770" y="249" text-anchor="end">COMPLETE</text></a>
  <a class="graph-node complete" href="#d20"><rect x="430" y="300" width="360" height="90" rx="8"/><text class="node-id" x="450" y="329">D20</text><text class="node-label" x="610" y="356" text-anchor="middle">Classify requests and call order</text><text class="node-state" x="770" y="379" text-anchor="end">COMPLETE</text></a>
  <a class="graph-node complete" href="#d30"><rect x="430" y="430" width="360" height="90" rx="8"/><text class="node-id" x="450" y="459">D30</text><text class="node-label" x="610" y="486" text-anchor="middle">Build dry-run protocol fixtures</text><text class="node-state" x="770" y="509" text-anchor="end">COMPLETE</text></a>
  <a class="graph-node complete" href="#d40"><rect x="430" y="560" width="360" height="90" rx="8"/><text class="node-id" x="450" y="589">D40</text><text class="node-label" x="610" y="616" text-anchor="middle">Resolve first safe live response</text><text class="node-state" x="770" y="639" text-anchor="end">COMPLETE</text></a>
  <a class="graph-node complete" href="#d50"><rect x="430" y="690" width="360" height="90" rx="8"/><text class="node-id" x="450" y="719">D50</text><text class="node-label" x="610" y="746" text-anchor="middle">Recover initialization, modes, controls</text><text class="node-state" x="770" y="769" text-anchor="end">COMPLETE</text></a>
  <a class="graph-node active" href="#d60"><rect x="430" y="820" width="360" height="90" rx="8"/><text class="node-id" x="450" y="849">D60</text><text class="node-label" x="610" y="876" text-anchor="middle">Capture, parse, and decode frames</text><text class="node-state" x="770" y="899" text-anchor="end">ACTIVE · OPTICAL CALIBRATION</text></a>
  <a class="graph-node complete" href="#d70"><rect x="430" y="950" width="360" height="90" rx="8"/><text class="node-id" x="450" y="979">D70</text><text class="node-label" x="610" y="1006" text-anchor="middle">Build operable reader core</text><text class="node-state" x="770" y="1029" text-anchor="end">COMPLETE · ALPHA</text></a>
  <a class="graph-node complete" href="#d80"><rect x="170" y="1110" width="360" height="90" rx="8"/><text class="node-id" x="190" y="1139">D80</text><text class="node-label" x="350" y="1166" text-anchor="middle">Build Linux application bridge</text><text class="node-state" x="510" y="1189" text-anchor="end">COMPLETE · ALPHA</text></a>
  <a class="graph-node proposed" href="#d90"><rect x="690" y="1110" width="360" height="90" rx="8"/><text class="node-id" x="710" y="1139">D90</text><text class="node-label" x="870" y="1166" text-anchor="middle">Build macOS application bridge</text><text class="node-state" x="1030" y="1189" text-anchor="end">DEFERRED · READER COMPLETE</text></a>
  <a class="graph-node active" href="#d100"><rect x="430" y="1260" width="360" height="90" rx="8"/><text class="node-id" x="450" y="1289">D100</text><text class="node-label" x="610" y="1316" text-anchor="middle">Stability, fault, application acceptance</text><text class="node-state" x="770" y="1339" text-anchor="end">ACTIVE · LINUX</text></a>
  <a class="graph-node active" href="#d110"><rect x="170" y="1390" width="360" height="90" rx="8"/><text class="node-id" x="190" y="1419">D110</text><text class="node-label" x="350" y="1446" text-anchor="middle">Package source, fixtures, operations</text><text class="node-state" x="510" y="1469" text-anchor="end">ACTIVE · ALPHA</text></a>
  <a class="graph-node proposed" href="#d120"><rect x="690" y="1390" width="360" height="90" rx="8"/><text class="node-id" x="710" y="1419">D120 · EXIT</text><text class="node-label" x="870" y="1446" text-anchor="middle">Accept release and residual risks</text><text class="node-state" x="1030" y="1469" text-anchor="end">PROPOSED</text></a>
  <path class="graph-edge" d="M530 1435H690"/>
</svg>
</div>
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
| D110 | Package source and operations | D100 | Active; alpha-7 released and independently verified | Public GitHub repository, Apache-2.0 license, udev/V4L2 operations, CI, two modes, bounded initial recovery, optical and calibration procedures, measured output cadence, rendered evidence, permanent publication boundary, tested install/removal, validation record, and report links |
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
[firmware-discovery evidence](../evidence/firmware-discovery.html). This bounded
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
[Micro-Manager application precedent](../evidence/micromanager-application-precedent.html).

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
[targeted Ghidra evidence](../evidence/ghidra-targeted-decompilation.html).

This substantially improves maintainability and cross-checks the current C17
implementation, but does not yet explain the physical-cold `0x02` timeout.
The VirtualHere trace therefore remains the evidence gate.

## Task Contracts

<div class="task-controls" role="group" aria-label="Filter task contracts">
  <button type="button" data-task-filter="all" aria-pressed="true">All tasks</button>
  <button type="button" data-task-filter="active" aria-pressed="false">Active</button>
  <button type="button" data-task-filter="ready" aria-pressed="false">Ready</button>
  <button type="button" data-task-filter="complete" aria-pressed="false">Complete</button>
  <button type="button" data-task-filter="proposed" aria-pressed="false">Proposed</button>
  <button type="button" data-task-filter="blocked" aria-pressed="false">Blocked</button>
  <span class="task-progress" aria-live="polite"></span>
</div>

::: {.task-card data-state="complete"}
<!-- task: D00; depends: none; state: complete -->
### D00 — Preserve Physical and USB Baseline {#d00}

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: START</span><span>Downstream: <a href="#d10">D10</a></span></p>

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

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: <a href="#d00">D00</a></span><span>Downstream: <a href="#d20">D20</a></span></p>

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

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: <a href="#d10">D10</a></span><span>Downstream: <a href="#d30">D30</a></span></p>

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

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: <a href="#d20">D20</a></span><span>Downstream: <a href="#d40">D40</a></span></p>

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

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: <a href="#d30">D30</a></span><span>Downstream: <a href="#d50">D50</a></span></p>

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

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: <a href="#d40">D40</a></span><span>Downstream: <a href="#d60">D60</a></span></p>

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

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: <a href="#d50">D50</a></span><span>Downstream: <a href="#d70">D70</a></span></p>

| Field | Contract |
|---|---|
| State | Active; coherent preview/full-resolution images, optical gain, neutral-background white balance, settings-bound user-space flat-field implementation, real-frame correction plumbing, and corrected-stream V4L2 preflight pass; valid physical flat calibration, final known-target phase/color, and live-camera V4L2 execution remain |
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
The [field-uniformity note](../evidence/field-illumination-correction.html) records
a Köhler alignment and relay-isolation checklist plus a per-Bayer-plane
dark/flat correction that can run before demosaic or V4L2 output. Public commit
`1dc096b` implements that correction as a dependency-free C17 tool and an
optional V4L2 bridge stage. Its complete suite passes on macOS and the Pi. A
synthetic Pi preflight corrected six full 1280x960 GRBG frames, converted them
to YUYV, had a separate application consume all six through the temporary
loopback, and cleaned up; 60 corrected preview frames measured approximately
225 frames/s. The [flat-field/V4L2 record](../evidence/flat-field-v4l2-preflight.html)
separates that software proof from the still-open physical dark/flat capture.
Public commit `6eb68a7` records exposure and gain in new maps and makes the
V4L2 bridge reject unknown or mismatched settings before opening the camera or
creating a loopback device. A real Mac-cable diagnostic then captured 24 exact
250-ms/gain-0 frames and corrected eight of them with an intentionally invalid
self-flat plus an illuminated 1-ms proxy dark. Its 3x3 max/min region ratio
fell from 1.336910 to 1.001023, proving full-size pixel plumbing while also
showing that a self-flat removes the specimen scene. The
[physical self-test](../evidence/macos-physical-flat-field-self-test.html)
therefore leaves true same-settings blocked darks and translated/defocused
blank flats explicitly open.
Public commit `176ef90` now makes that hands-on gate reproducible. Its exact
token-gated helper refuses existing destinations, locks settings, prompts for
blocked darks and separately repositioned flat batches, withholds a fresh blank
and real specimen for validation, verifies byte counts, renders before/after
frames, and hashes the completed bundle. EOF, signals, or failures leave an
incomplete marker. The [guided-session evidence](../evidence/guided-flat-field-capture-session.html)
records USB-free end-to-end passes on Apple Silicon and exact-commit Raspberry
Pi AArch64; no camera move was needed for that validation.
An inert exact-commit harness remains staged to capture both modes and have
FFmpeg consume six camera frames through `/dev/video42` after the cable move.
:::

::: {.task-card data-state="complete"}
<!-- task: D70; depends: D60; state: complete -->
### D70 — Build the Operable Reader Core {#d70}

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: <a href="#d60">D60</a></span><span>Downstream: <a href="#d80">D80</a>, <a href="#d90">D90</a></span></p>

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
[portable reader evidence](../evidence/offline-reader-session.html) and
[public live-validation evidence](../evidence/public-release-live-validation.html).

Happy-day steps:

1. Separate transport, protocol, parser, decoder, and public API modules.
2. Implement inspect, still, stream, controls, replay, and diagnostics commands.
3. Add bounded queues, structured errors, stop, close, and reconnect.
4. Prove source and binary portability on both target operating systems.
:::

::: {.task-card data-state="complete"}
<!-- task: D80; depends: D70; state: complete -->
### D80 — Build the Linux Application Bridge {#d80}

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: <a href="#d70">D70</a></span><span>Downstream: <a href="#d100">D100</a></span></p>

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
evidence](../evidence/linux-v4l2-replay-bridge.html) and report milestone.

Happy-day steps:

1. Choose the smallest standard path and document the decision.
2. Translate reader frames and timestamps without copying protocol logic.
3. Prove application negotiation, stream lifecycle, and slow-consumer behavior.
4. Verify clean removal and camera reuse after application failure.
:::

::: {.task-card data-state="proposed"}
<!-- task: D90; depends: D70; state: proposed -->
### D90 — Build the macOS Application Bridge {#d90}

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: <a href="#d70">D70</a></span><span>Downstream: <a href="#d100">D100</a></span></p>

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
validation](../evidence/macos-native-cable-validation.html) and [relay
validation](../evidence/macos-virtualhere-live-validation.html).
:::

::: {.task-card data-state="active"}
<!-- task: D100; depends: D80,D90; state: active -->
### D100 — Prove Stability, Fault Handling, and Application Acceptance {#d100}

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: <a href="#d80">D80</a>, <a href="#d90">D90</a></span><span>Downstream: <a href="#d110">D110</a></span></p>

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

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: <a href="#d100">D100</a></span><span>Downstream: <a href="#d120">D120</a></span></p>

| Field | Contract |
|---|---|
| State | Active; public alpha-7 packages the reader, calibrated-field tooling, measured output cadence, rendered evidence, permanent publication-boundary enforcement, and tested install/removal while residual physical validation continues |
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

The current annotated prerelease
[`v0.2.0-alpha.7`](https://github.com/la3lma/tucsen-tca-camera/releases/tag/v0.2.0-alpha.7)
resolves to exact commit `72f6e63`. Independent main and tag CI pass on Ubuntu
and macOS, an exact-commit Raspberry Pi AArch64 worktree passes the complete
suite, and the downloaded tag archive passes the complete suite outside a Git
checkout. Alpha 7 packages settings-bound dark/flat correction, the optional
corrected V4L2 path, guided physical calibration, monotonic frame timestamps,
delivered-cadence analysis, rendered evidence, and permanent full-history
publication-boundary enforcement. See the
[alpha-7 release evidence](../evidence/public-release-alpha7.html).

The current [release acceptance audit](../evidence/release-acceptance-audit.html)
marks the Linux reader/API, preview endurance, application bridge, direct-cable
Apple Silicon reader path, safety, reproducibility, and legal-hygiene
requirements as passed. D120 remains open for physical cable reconnect and
optical/color validation. AVFoundation remains an explicit Linux-first
deferral rather than an exit blocker.
:::

::: {.task-card data-state="proposed"}
<!-- task: D120; depends: D110; state: proposed -->
### D120 — Accept the Release and Residual Risks {#d120}

<p class="task-nav"><a href="#dependency-graph">↑ Dependency graph</a><span>Upstream: <a href="#d110">D110</a></span><span>Downstream: EXIT</span></p>

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
| E-001 | Physical enclosure and lack of visible model marking are documented | [Owner photographs](../evidence/photos/index.html) | VERIFIED |
| E-002 | Device is `0547:c003`, high-speed USB 2.0, one `0xff` interface, bulk IN `0x82`, 512-byte packets | [Device identity](../evidence/device-identity.html) and Pi enumeration | VERIFIED |
| E-003 | Linux opens and safely claims/releases interface 0 without a transfer-capable probe | [Safe libusb probe](../evidence/safe-libusb-probe.html) | VERIFIED |
| E-004 | IOCTL `0x222059` has distinct 2011 `0xc0` and 2013 direction-aware mappings; both copy request/value/index record offsets | [Windows IOCTL handler analysis](../evidence/tucsen-driver-ioctl-handler.html) | VERIFIED |
| E-005 | DLL contains requests `b3`, `b4`, `b5`, `b6`, `b7`, `b8`, `ba`, `bb`, `bd`, `be` | [Static protocol map](../evidence/ts1000-static-protocol-map.html) | VERIFIED |
| E-006 | Later-lineage `b3` is a capture trigger | Static call proximity only | INFERRED / OPEN |
| E-007 | Initialization, response semantics, frame dimensions, encoding, and controls are known | No accepted evidence yet | OPEN |
| E-008 | Reader streams into standard Linux/macOS applications | No implementation yet | OPEN |
| E-009 | Official software maps TCA-10.0N `0547:c003` to TSView6/7; its TCA DLL exposes a fixed `0x11/0x3ff0` register read and open/close prefix | [TSView7 TCA protocol map](../evidence/tsview7-tca-protocol-map.html) | VERIFIED |
| E-010 | Nine bounded Linux trials failed without loss of enumeration; the final physical-cold run used the corrected TCA tuple and timed out on open/read/close while both health checks passed | [Live control trials](../evidence/live-control-trials.html) | VERIFIED NEGATIVE |
| E-011 | No standalone C003 firmware/updater was found in the official surfaces and recovered packages inspected; this remains a bounded search result | [Firmware discovery](../evidence/firmware-discovery.html) | VERIFIED NEGATIVE / NON-GATING |
| E-012 | Historical open-source inventory names IS1000 C003, but its implemented driver targets 4D88 and must not be replayed against this camera | [Open-source prior art](../evidence/open-source-prior-art.html) | VERIFIED BOUNDARY |
| E-013 | TSView7 ignores the `0x02` wrapper result, then validates 80 even registers `0x0000`–`0x009e` with `0x11`; the Linux probe stopped earlier than the vendor path | [TCA startup validation](../evidence/tsview7-tca-startup-validation.html) | VERIFIED STATIC |
| E-014 | All eight USBPcap roots were captured; only QEMU `0627:0001` HIDs appeared, proving CocoaSPICE usbredir bypasses the Windows filter and requires a lower observation point | [Windows trace bench](../evidence/windows-trace-bench.html) | VERIFIED NEGATIVE INSTRUMENTATION |
| E-015 | TSView7 reads one byte per pixel from the bulk pipe using four overlapped lanes; five fixed modes range from 640x480 to 3664x2748 and have deterministically recovered chunk sizes | [TCA acquisition map](../evidence/tsview7-tca-acquisition-map.html) and offline geometry fixture | VERIFIED STATIC |
| E-016 | The first portable C17 frame-core slice reproduces the five mode geometries and assembles exact-length frames across arbitrary fragments while rejecting short/overflow cases; native macOS and Pi tests pass | [Offline frame-core verification](../evidence/offline-frame-core.html) | VERIFIED OFFLINE |
| E-017 | Byte-accurate x86 emulation of the matching TSView7 DLL confirms register addresses occupy `wIndex`, recovers the obfuscated `0x0a` fixed-mode writes, and passes deterministic golden tests without a host USB API | [TCA initialization emulation](../evidence/tsview7-tca-emulated-init.html) | VERIFIED EMULATED / NOT LIVE |
| E-018 | Portable C17 modules encode the corrected open/read/close records and all five fixed-mode initialization plans, then execute them through a fail-fast transport contract; golden and fault-injection tests cover all 154 writes and every mode-4 failure boundary on macOS and Pi without USB imports | [Offline protocol-plan verification](../evidence/offline-protocol-plan.html) | VERIFIED OFFLINE / NOT LIVE |
| E-019 | Emulated TSView7 conversion identifies GRBG-to-BGR24 memory conventions; a portable explicit-pattern decoder and exact-frame replay CLI pass macOS/Pi tests and feed a synthetic RGB24 stream into FFmpeg | [Offline image pipeline](../evidence/offline-image-pipeline.html) | VERIFIED OFFLINE / SYNTHETIC |
| E-020 | Static analysis and offline DLL emulation separate sensor controls from host processing, recover exposure units/limits, analog-gain encoding, and four frame-speed PLL plans; a portable C17 planner passes golden tests on macOS and Pi | [TCA control reconstruction](../evidence/tsview7-tca-controls.html) | VERIFIED OFFLINE / NOT LIVE |
| E-021 | Offline DLL execution confirms full-chunk requests, four-lane rotation, and the intentional final-remainder completion for every fixed mode; a portable staged scheduler matches those semantics and cancels all outstanding reads on every injected submit/completion/unexpected-length failure; sanitizer and native Pi tests pass without USB imports | [Offline capture scheduler](../evidence/offline-capture-scheduler.html) and [DLL emulation](../evidence/tsview7-tca-emulated-init.html) | VERIFIED EMULATED + OFFLINE / NOT LIVE |
| E-022 | The one-shot D40 harness pinned the reviewed v2 probe hash and captured before/after identity, kernel, safe-claim, raw result, status, and hashes after an owner-confirmed physical cold cycle | [Cold-session harness](../evidence/cold-probe-harness.html) | EXECUTED ONCE / VERIFIED |
| E-023 | On a new USB instance after physical cold power, corrected open/read/close all timed out; before/after descriptors and interface claims passed, identity was byte-identical, and no kernel fault occurred | [D40 physical-cold result](../evidence/d40-cold-result.html) | VERIFIED NEGATIVE / TERMINAL LINUX BRANCH |
| E-024 | With Secure Boot disabled only in the offline VM and Windows test mode active, the 2011 Tucsen driver reports `Started`; TSView7 discovers the camera and reaches a ready control window with resolution, snapshot, record, white-balance, exposure, and property controls | [Windows trace bench](../evidence/windows-trace-bench.html) | VERIFIED LIVE WINDOWS |
| E-025 | After Windows initialized the still-powered camera, macOS libusb captured exactly 307,200 bytes as 81,920 + 81,920 + 81,920 + 61,440; ten `0x88` marker bytes begin every block and GRBG replay yields the expected taped-sensor dark image | [Working Windows reference and direct host capture](../evidence/windows-reference-live-capture.html) | VERIFIED LIVE DATA PLANE |
| E-026 | The installed working `TS1000.dll` and `Tucsen64.sys` hashes match the analyzed purchase-era TCA pair, and the INF explicitly identifies `0547:c003` as TCA-10.0-N | [Working Windows reference and direct host capture](../evidence/windows-reference-live-capture.html) | VERIFIED LINEAGE |
| E-027 | Windows `usbip-win2` attached the camera and received valid descriptors, but its repeated 18-byte device-descriptor read timed out after 5.004272 seconds before `SET_CONFIGURATION`; the immutable usbmon capture is preserved and the transport branch is closed | [USB/IP result and VirtualHere fallback](../evidence/virtualhere-trace-bench.html) | VERIFIED NEGATIVE TRANSPORT |
| E-028 | Headless Ghidra 12.1.4 independently confirms the TCA command ABI, register read/write wrappers, four implemented driver IOCTLs, ordinary KMDF configuration, and split bulk-URB path; it finds no prepare-hardware firmware loader and shows ignored IOCTL `0x22208a` cannot hide a USB transaction | [Targeted Ghidra decompilation](../evidence/ghidra-targeted-decompilation.html) | VERIFIED STATIC / NOT LIVE |
| E-029 | A portable C17 startup module emits all 80 even-register validation reads and checks the extracted expected signature with deterministic first-mismatch reporting; tests pass on macOS and the Ubuntu ARM64 bench without USB imports | [Offline startup-signature core](../evidence/offline-startup-signature.html) | VERIFIED OFFLINE / NOT LIVE |
| E-030 | A 2014 UCL thesis documents exact-model TCA-10.0-N live view and 80-hour time-lapse use in Micro-Manager 1.4; the contemporary public adapter tree has generic TWAIN/OpenCV adapters but no legacy Tucsen-specific adapter, so the application precedent is verified while its transport path remains unresolved | [Historical Micro-Manager application precedent](../evidence/micromanager-application-precedent.html) | VERIFIED APPLICATION PRECEDENT / PATH OPEN |
| E-031 | The live-captured mode-4 Bayer8 frame was decoded and presented through a removable 640x480 YUYV V4L2 loopback on Ubuntu ARM64; v4l2-ctl and FFmpeg each consumed three exact-size frames across a remove/recreate cycle, and a packaged reader-core bridge reproduced the capture hash while refusing existing setups and cleaning up its device/module | [Linux V4L2 replay bridge](../evidence/linux-v4l2-replay-bridge.html) | VERIFIED APPLICATION BOUNDARY / REPLAY ONLY |
| E-032 | A transport-neutral C17 reader implements the planned lifecycle, exact frame/decode metadata, bounded latest/lossless queues, validated controls, structured diagnostics, fault/close/reopen, inspect, and replay; strict native tests pass on macOS and Ubuntu ARM64, sanitizer execution passes, and the live-captured fixture decodes byte-identically on both | [Portable reader session and CLI](../evidence/offline-reader-session.html) | VERIFIED OFFLINE CORE / COLD LIVE COMPLETION OPEN |
| E-033 | An opt-in libusb backend connects the portable reader to the previously verified warm mode-4 data plane; native ARM64 Linux and Apple Silicon binaries import only the exact descriptor/open/claim/release plus bulk-transfer allowlist, pass inert-token and fault-injection tests covering the exact schedule, short/zero/error paths, no-retry behavior, state guards, and partial raw preservation, and contain no control/reset/configuration/alternate-setting path; a separately token-gated Linux script is ready to feed decoded frames into a temporary V4L2 node while preserving raw bytes; live execution remains deferred until a known-good warm handoff exists | [Warm-state libusb reader backend](../evidence/warm-reader-backend.html) | VERIFIED BUILD + STATIC SAFETY / WARM LIVE RUN PENDING |
| E-034 | A separately compiled operable backend composes the warm reader with checked exposure, normalized-gain, and eleven-write/two-delay frame-speed plans; injected native tests on Apple Silicon and ARM64 Linux verify exact tuples, delays, configuration guards, fail-fast timeout/short/ack/sleep reporting, and no state update after a partial failed plan; a separately named inert-by-default CLI can apply exactly one prevalidated control and exit without starting acquisition; the read-only streaming binary remains unchanged and physical control execution is pending the known-good warm handoff | [Opt-in operable libusb control backend](../evidence/operable-control-backend.html) | VERIFIED OFFLINE CONTROL TRANSPORT + CLI / LIVE CONTROL PENDING |
| E-035 | A deterministic usbmon extractor correlates submit/completion URBs and preserves timing, setup fields, statuses, lengths, and payloads; synthetic vendor-control/bulk tests and the preserved USB/IP capture pass on macOS and ARM64 Linux, with the latter independently reproducing ten standard-control pairs, one 5.004272-second `-104` failure, no vendor request, and no bulk transfer | [Deterministic usbmon trace extractor](../evidence/usbmon-trace-extractor.html) | VERIFIED OFFLINE TRACE ANALYSIS / VIRTUALHERE CAPTURE PENDING |
| E-036 | The official 2026 AmScope ARM64 Linux and Windows packages were downloaded project-locally, hash-pinned, and extracted without execution; neither tree names C003/TCA/IS1000, both current 232-entry Windows INFs omit `0547:c003`, and no standalone firmware/updater file was found; the Linux package's vendor-wide udev rule is permission evidence only, not a compatibility claim | [Updated-firmware discovery](../evidence/firmware-discovery.html) | VERIFIED STATIC NEGATIVE / NON-GATING |
| E-037 | A USB-inert semantic stage consumes only paired trace TSV, labels recovered TCA open/close/state/read/write and endpoint-`0x82` bulk events, reverses write XOR encoding, decodes big-endian read values, validates status/length/acknowledgement, and preserves unknown vendor requests as unclassified; synthetic tests pass and the USB/IP negative trace remains ten standard controls with one transport error | [Deterministic usbmon extractor and TCA annotator](../evidence/usbmon-trace-extractor.html) | VERIFIED OFFLINE TRACE SEMANTICS / VIRTUALHERE CAPTURE PENDING |
| E-038 | A USB-free C generator composes the existing open, 80-read signature, and fixed-mode plans into a 120-control mode-4 Ready expectation; a deterministic TSV comparator aligns captured controls and validates response patterns without generating USB operations; strict tests and the USB/IP negative-trace comparison are byte-identical on Apple Silicon and AArch64 Linux | [Modeled TCA trace plan and comparator](../evidence/tca-trace-plan-comparator.html) | VERIFIED OFFLINE COMPARISON / SUCCESSFUL TRACE PENDING |
| E-039 | Both post-reboot UTM USB paths failed without harming enumeration; the camera was moved cold to `rpios-17`, where exact-device identity, `usbmon3`, pinned VirtualHere inputs, and Windows-side discovery through the UTM gateway relay are live; the v4 handoff ISO removes boot-specific addressing and verifies its embedded sources byte-for-byte | [VirtualHere fallback trace bench](../evidence/virtualhere-trace-bench.html) | VERIFIED LIVE INFRASTRUCTURE / DEVICE ATTACH PENDING |
| E-040 | The completed Windows reference capture contains 744 paired operations (25 standard controls, 191 vendor controls, 528 bulk transfers), no pairing gaps, and no semantic validation issue; it exposes the seven-command cold-start sequence and three-read 1280×960 frame schedule | Preserved VirtualHere session under `work/trace-captures/virtualhere-session-pi-20261003T120230Z/` | VERIFIED LIVE REFERENCE TRACE |
| E-041 | Native ARM64 Linux reproduces only those seven startup commands, accepts their trace-confirmed stalled IN data stages, validates three `0x88` markers per frame, streams continuous 1280×960 Bayer8, and applies bounded exposure/gain writes without Windows or a camera-specific kernel driver | Report current milestone and [public validation](../evidence/public-release-live-validation.html) | VERIFIED LIVE LINUX COLD START + CONTROLS |
| E-042 | A foreground bridge converts the live physical Bayer stream to a temporary 1280×960 YUYV V4L2 device; `v4l2-ctl` reports the intended format, FFmpeg consumes three frames, and cleanup removes only the loopback created for the session | Report current milestone and V4L2 work bundle | VERIFIED LIVE APPLICATION BOUNDARY |
| E-043 | The exact public reader commit passes a 30-frame controlled capture, ten independent open/init/ten-frame/close processes (100/100 frames), and a 14,400-frame/2,410-second continuous run with flat sampled memory; Ubuntu and macOS CI pass | [Public release live validation](../evidence/public-release-live-validation.html) | VERIFIED REOPEN + ENDURANCE |
| E-044 | Recovered selector `b4/c0`, 3664×2748 geometry, and formula `((pixels >> 9) + 1) << 9` predicted a 10,068,992-byte frame; the guarded physical probe received that exact length with all twenty markers, and mode-2 recovery captured three frames | [Guarded full-resolution probe](../evidence/full-resolution-probe.html) | VERIFIED LIVE FULL RESOLUTION + RECOVERY |
| E-045 | The public two-mode reader candidate captured three consecutive frames in mode 0 and then mode 2 with exact raw/application byte counts; its mode-aware exposure conversion programmed 324 and 834 lines respectively at 100 ms | [Public release live validation](../evidence/public-release-live-validation.html) | VERIFIED LIVE PUBLIC READER BOTH MODES |
| E-046 | Exact tag `v0.2.0-alpha.1` was terminated with `SIGKILL` during mode-2 capture after its complete first-frame flush; without a USB reset or power cycle, a new tagged process immediately reopened and captured three frames | [Public release live validation](../evidence/public-release-live-validation.html) | VERIFIED PROCESS-DEATH RECOVERY |
| E-047 | Official stable 2026 and legacy 2025 ToupCam SDK packages support Linux/macOS/Windows and ship Python bindings, but their 1,768- and 1,600-pair explicit Windows USB tables omit `0547:c003`; the Python module is a thin proprietary-library wrapper and the vendor-wide Linux udev rule is permission evidence, not device support | [Existing Linux driver candidates](../evidence/existing-linux-driver-candidates.html) | VERIFIED STATIC NEGATIVE / API INSPIRATION |
| E-048 | Micro-Manager's AmScope adapter is Windows-only MU-series/ToupCam code for a different family, while its Linux Video4Linux adapter matches the project's proven YUYV loopback; Pycro-Manager can add acquisition/stage automation only above a working MMCore adapter, and Fiji/MIST remain downstream tile-stitching candidates | [Microscopy application stack](../evidence/microscopy-application-stack.html) | VERIFIED ARCHITECTURE / LIVE MM TEST PENDING |
| E-049 | With the camera connected, a controlled Pi reboot changed the Linux boot ID and USB device instance; public main commit `71fdae1` rebuilt and passed its tests, then cold-opened the re-enumerated `0547:c003` camera and captured three exact-size mode-2 frames with controls and exit zero | [Public release live validation](../evidence/public-release-live-validation.html) | VERIFIED LIVE HOST-REBOOT RECOVERY |
| E-050 | A line-by-line readiness audit distinguishes the useful Linux alpha from final acceptance: streaming, reader/API, Linux application bridge, portable macOS reader, and the non-functional requirements pass, while physical cable reconnect and optical/color checks remain open | [Release acceptance audit](../evidence/release-acceptance-audit.html) | VERIFIED AUDIT; EXIT OPEN |
| E-051 | The Apple Silicon public reader cold-initialized the physical `0547:c003` camera through a one-device Pi relay, applied exposure and gain, captured three exact-size mode-2 frames, and exited zero | [Apple Silicon relay validation](../evidence/macos-virtualhere-live-validation.html) | VERIFIED LIVE MACOS READER |
| E-052 | Returning ownership from macOS to Linux reproduced one marker-invalid leading warm-up frame; public alpha-2 preserved it once, discarded it under a two-frame limit, delivered three valid frames in the same process, and kept later marker loss fatal | [Apple Silicon relay validation](../evidence/macos-virtualhere-live-validation.html) | VERIFIED BOUNDED HAND-BACK RECOVERY |
| E-053 | Public commit `a61c044` adds a no-dependency Bayer statistics/focus utility and reproducible microscope procedure; Ubuntu/macOS CI passed, the exact Pi commit passed every test, and a fresh physical covered-sensor capture produced exact mode-2 byte counts, `frames=1 status=ok`, and a valid JSON analysis | [Optical validation tooling](../evidence/optical-validation-tooling.html) | VERIFIED TOOLING + LIVE DARK-FRAME ANALYSIS / OPTICS OPEN |
| E-054 | Public commit `fb502c1` installs and removes exactly the reader, V4L2 helper, and frame analyzer under `PREFIX`/`DESTDIR`; a staged test proves an unrelated same-directory sentinel survives, and the complete suite passes on Apple Silicon, the Pi, Ubuntu CI, and macOS CI | [Package operations](../evidence/package-operations.html) | VERIFIED INSTALL/REMOVE OPERATIONS |
| E-055 | Annotated public prerelease `v0.2.0-alpha.3` resolves to commit `3c16d2a`; independent main/tag Ubuntu and macOS CI runs pass, the downloaded public source archive passes every test outside a Git checkout, and the exact-tag Pi build passed every test before a controlled physical mode-2 capture and analysis completed with exact byte counts and exit zero | [Public alpha-3 release](../evidence/public-release-alpha3.html) | VERIFIED PUBLIC ARCHIVE + EXACT-TAG LIVE CAPTURE |
| E-056 | An inert exact-alpha-3 reconnect harness is staged on the Pi, requires observation of device count zero before re-enumeration, and will verify a three-frame capture, exact sizes/status, first-frame analysis, and evidence hashes without reset, deauthorization, or speculative control requests | [Physical reconnect harness](../evidence/physical-reconnect-harness.html) | PREPARED + INERT-VERIFIED / PHYSICAL ACTION OPEN |
| E-057 | Exact public alpha-3 on Apple Silicon directly claimed USB `0547:c003`, applied gain/exposure, captured three preview frames, one full-resolution frame, and a fresh-process preview reopen with exact sizes and analysis; the first cold-attach invocation failed closed on a single one-byte control response before all subsequent startup controls returned the reference stall | [Native-cable Apple Silicon validation](../evidence/macos-native-cable-validation.html) | VERIFIED DIRECT READER / COLD-ATTACH TRANSIENT RECORDED |
| E-058 | Microscope imagery and 0.983 autocorrelation at a 524,288-byte lag exposed the old multi-request assembly error; single-request probes proved one prefix per complete record and yielded coherent 1280x960 and 3664x2748 images | [Optical frame-layout correction](../evidence/first-optical-capture.html) | VERIFIED LIVE OPTICAL / READER CORRECTED |
| E-059 | At 100 ms, corrected gain 0..320 produced monotonic mean intensity 14.67..154.88; gain 256 yielded negligible clipping, and a 16-frame run produced 16 distinct hashes plus multi-resolution PNGs and an H.264 proof clip | [Optical frame-layout correction](../evidence/first-optical-capture.html) | VERIFIED LIVE CONTROLS + MOTION SEQUENCE |
| E-060 | Mode-0 record N `[512,end)` plus record N+1 `[320,512)` produced three distinct complete 3664x2748 frames without the false left strip; neutral slide regions independently yielded approximately R/G/B `0.87/1.0/2.0` in both modes | [Optical frame-layout correction](../evidence/first-optical-capture.html) | VERIFIED LIVE FULL-FRAME ASSEMBLY + IN-SITU WHITE BALANCE |
| E-061 | After a change to 10x made the old settings nearly fully clipped, a gain-zero sweep found an unclipped 250-ms preview and complete full-resolution still; public alpha-6 at commit `0fded6e` emits ratio-preserving FFmpeg-safe white-balance gains | [Optical capture and 10x recovery](../evidence/first-optical-capture.html) | VERIFIED LIVE OPTICAL RECOVERY + RELEASE |
| E-062 | Exact public alpha-6 builds and passes every test on `rpios-17`; a synthetic 1280x960 YUYV producer/consumer preflight passed six exact frames through the generic loopback and cleaned it up, and a static-tested inert harness is staged to verify both optical modes plus six ordinary V4L2-consumed camera frames after the cable move | [Pi alpha-6 optical preparation](../evidence/pi-alpha6-linux-optical-preparation.html) | GENERIC V4L2 VERIFIED + CAMERA HARNESS PREPARED / CAMERA MOVE OPEN |
| E-063 | Equal 256x192 regions in the 10x blank-field preview range from mean luma 134.0 at bottom-left to 193.9 at top-middle, showing asymmetric field nonuniformity rather than simple radial falloff; an optical alignment/isolation checklist and calibrated per-Bayer-plane dark/flat correction are now specified | [Field illumination correction](../evidence/field-illumination-correction.html) | MEASURED DIAGNOSIS + CORRECTION PLAN |
| E-064 | Public commit `1dc096b` implements per-pixel fixed-point dark subtraction and independent R/G1/G2/B flat gains before demosaic; on the Pi, six synthetic corrected 1280x960 frames traversed FFmpeg and a temporary V4L2 loopback to a separate consumer, cleanup passed, and 60-frame filter throughput measured about 225 fps | [User-space flat-field and V4L2 preflight](../evidence/flat-field-v4l2-preflight.html) | VERIFIED SOFTWARE + GENERIC APPLICATION BOUNDARY / PHYSICAL FLAT OPEN |
| E-065 | Public commit `6eb68a7` stores exposure/gain provenance in new `TCAFF01` maps and rejects unknown or mismatched V4L2 settings before mutation; a real Mac-cable run captured 24 exact physical frames and applied a full-size self-flat diagnostic to eight frames, reducing the 3x3 max/min ratio from 1.336910 to 1.001023 while correctly demonstrating that a self-flat erases specimen structure and cannot be accepted as optical calibration | [Apple Silicon physical flat-field pipeline self-test](../evidence/macos-physical-flat-field-self-test.html) | VERIFIED PHYSICAL-SIZE PLUMBING + SETTINGS GUARD / TRUE DARK + BLANK FLAT OPEN |
| E-066 | Public commit `176ef90` provides an exact-token, inert-by-default guided session that locks settings, separates blocked-dark/repositioned-flat/fresh-blank/specimen phases, verifies raw/Bayer byte counts, marks partial sessions, builds/applies/inspects the map, renders four PNGs, and hashes the bundle; a USB-free dynamic test using the real corrector and analyzer passes on Apple Silicon and an exact public clone on Raspberry Pi AArch64 | [Guided physical flat-field capture session](../evidence/guided-flat-field-capture-session.html) | VERIFIED WORKFLOW + PORTABILITY / OPERATOR-ASSISTED OPTICAL RUN OPEN |
| E-067 | Public commit `064cf31` records one monotonic timestamp after every accepted Bayer-frame write; direct-Mac physical runs delivered 17.3466 fps at 1280x960/requested 1 ms, 9.5057 fps at 1280x960/250 ms, and 2.7911 fps at 3664x2748/250 ms, with every frame hash distinct | [Apple Silicon measured delivered-frame cadence](../evidence/macos-measured-frame-cadence.html) | VERIFIED LIVE OUTPUT CADENCE / SENSOR INTEGRATION AND LINUX CONSUMER TIMING NOT CLAIMED |
| E-068 | Public commit `064cf31` renders every evidence record as HTML, supplies evidence and photo indexes, checks all internal site targets, and adds a full-history CI denylist; a fresh current-tree and object-history audit found no raw disassembly, Ghidra state/export, vendor binary, firmware, packet capture, or private-work artifact | [Public evidence site and permanent publication boundary](../evidence/public-evidence-site-and-boundary.html) | VERIFIED LIVE SITE + CLEAN PUBLIC HISTORY |
| E-069 | Annotated prerelease `v0.2.0-alpha.7` resolves to exact commit `72f6e63`; independent main and tag CI pass on Ubuntu/macOS, the exact commit passes the full Raspberry Pi AArch64 suite, and the downloaded public tag archive passes the full suite outside a Git checkout | [Public alpha-7 release](../evidence/public-release-alpha7.html) | VERIFIED PUBLIC RELEASE + PI + ARCHIVE |

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

> **Current recommendation:** keep the evidence-backed userspace protocol fixed.
> On the present Mac-mounted optical bench, run the public guided flat-field
> session and follow each prompt literally: block illumination for darks,
> translate or defocus between flat batches, then reserve a fresh blank and
> real specimen for validation. The helper locks exposure/gain/phase, builds a
> settings-bound map, and retains raw/corrected frames and hashes together. At
> the next convenient cable move,
> run the staged live Linux V4L2 acceptance so an ordinary application consumes
> the corrected camera stream and consumer-side cadence/drop behavior is recorded. Known-target
> color/focus work remains the D60 exit gate; firmware discovery and
> AVFoundation remain non-gating fallbacks.

</main>
