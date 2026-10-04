# Tucsen TCA camera userspace reader

Early, independently developed userspace support for the legacy AmScope/Tucsen
USB microscope camera identified as `0547:c003` (`10MP CMOS Camera`, commonly
sold as TCA-10.0N/IS1000-family hardware).

**Project map:** [live Docstack](https://la3lma.github.io/tucsen-tca-camera/docstack/)
· [PDF investigation report](https://la3lma.github.io/tucsen-tca-camera/report/microscope-window-sensor.pdf)
· [rendered evidence index](https://la3lma.github.io/tucsen-tca-camera/evidence/)
· [source and releases](https://github.com/la3lma/tucsen-tca-camera)

The reader cold-initializes the camera with `libusb`, captures 1280×960 preview
or 3664×2748 full-resolution Bayer8 frames, validates and removes each device
record framing, and exposes bounded exposure and gain controls. A Raspberry Pi 5 has
completed a 14,400-frame preview endurance run, captured consecutive full-size
frames, and fed the preview stream through FFmpeg and a temporary V4L2 camera
device. No vendor driver and no camera-specific kernel module are required.

> **Alpha hardware support:** one physical camera has been tested. Microscope
> images are now spatially coherent in both modes, but final color/Bayer-phase
> confirmation and image-quality calibration remain open. Preserve
> raw frames and report your hardware identity when testing another unit.

## Full report, Docstack, and research record

The [live Docstack](https://la3lma.github.io/tucsen-tca-camera/docstack/)
tracks the evidence gates, open work, and exact supporting records. The
[current PDF report](https://la3lma.github.io/tucsen-tca-camera/report/microscope-window-sensor.pdf)
contains the narrative investigation, device identification, recovered
protocol, driver comparisons, and optical results. The published
[Journal of Bjorn entry](https://la3lma.github.io/journal-of-bjorn/papers/microscope-window-sensor.html)
provides a journal-level landing page without replacing these stable project
URLs.

Reproducible physical checks and their evidence hashes are summarized in the
[validation record](docs/validation.md).

Raw disassemblies, Ghidra databases, vendor binaries/drivers, firmware, and
packet captures are deliberately kept out of this public repository. The
[public publication boundary](PUBLICATION_POLICY.md) is CI-enforced against
both the current tree and the complete public Git filename history.

The remaining microscope-mounted checks have a reproducible
[optical validation procedure](docs/optical-validation.md), including Bayer
phase, orientation, exposure/gain sweeps, focus scoring, and a full-resolution
still.

## Supported state

| Capability | Status |
|---|---|
| Raspberry Pi / AArch64 Linux cold start | Verified live |
| Continuous 1280×960 Bayer8 capture | Verified live |
| Exposure and analog gain response | Optically verified live |
| FFmpeg/stdout pipeline and packaged view/record helper | Verified live |
| Optional `/dev/video*` through `v4l2loopback` | Verified live |
| Connected-camera Pi reboot and cold reopen | Verified live |
| Apple Silicon build | Verified |
| Apple Silicon libusb capture through Pi relay | Verified live |
| Native-cable capture on Apple Silicon macOS | Verified live in modes 0 and 2 |
| Full 3664×2748 Bayer8 capture | Verified live |
| Spatially coherent optical capture | Verified live in both modes |
| Neutral-background white-balance estimation | Verified optically |
| Final Bayer phase and color-target calibration | In progress |

## Build

Linux packages:

```sh
sudo apt install build-essential pkg-config libusb-1.0-0-dev python3
make
make test
```

macOS packages:

```sh
brew install libusb pkg-config
make
make test
```

On Apple Silicon, an older Intel Homebrew tree under `/usr/local` can cause
`pkg-config` to select an `x86_64` libusb while the compiler produces an
`arm64` reader. If the linker reports that architecture mismatch, install or
locate a native libusb and point this build only at its package metadata:

```sh
make clean all test \
  LIBUSB_PKG_CONFIG_PATH=/path/to/native/lib/pkgconfig
```

A standard native Homebrew installation normally uses
`/opt/homebrew/opt/libusb/lib/pkgconfig`. This override does not modify the
shell's global package search path or either Homebrew installation.

The camera-specific implementation is entirely userspace code. On a headless
Linux system, either run with appropriate USB permissions or install the
optional rule in [`udev/99-tucsen-tca-camera.rules`](udev/99-tucsen-tca-camera.rules).

## Install and remove

Install the reader, FFmpeg and V4L2 helpers, frame and timing analyzers,
white-balance estimator, and flat-field calibration/filter tool under the
selected prefix:

```sh
sudo make install PREFIX=/usr/local
```

Verify that the installed bridge resolves its sibling reader and flat-field
tool without opening the camera or loading a kernel module:

```sh
tca-v4l2 --diagnose-install
tca-camera --version
```

`tca-camera --version` is built from the repository's `VERSION` file. Debian
packages install the same marker under
`/usr/share/doc/tucsen-tca-camera/VERSION`; the test suite rejects a mismatch
between that upstream version, the CLI, and the Debian package version.

The diagnostic prints both resolved executable paths and
`NO USB TRANSFER SENT`. Source-tree use continues to prefer the locally built
programs, while an installed `tca-v4l2` automatically uses the programs beside
it in `PREFIX/bin`. `TCA_CAMERA_READER` and `TCA_FLAT_FIELD_TOOL` remain
explicit overrides for development and testing.

Remove exactly those seven installed programs:

```sh
sudo make uninstall PREFIX=/usr/local
```

Packagers can set `DESTDIR` for a staged install or removal. These targets do
not modify the optional udev rule or distribution-managed `v4l2loopback`
package.

### Debian binary package

The [alpha-11 prerelease](https://github.com/la3lma/tucsen-tca-camera/releases/tag/v0.2.0-alpha.11)
provides a checksum-pinned 64-bit Raspberry Pi OS / Debian development package
named `tucsen-tca-camera_0.2.0.alpha11-1_arm64.deb`. Its internal Debian
version is `0.2.0~alpha11-1`; GitHub normalizes the tilde in the downloadable
asset filename to a dot. The direct-camera Raspberry Pi V4L2 acceptance run is
still explicitly open, so consult the release notes before installation.

On Debian, Ubuntu, Raspberry Pi OS, and derivatives, build an
architecture-native package without root access:

```sh
make deb
```

The package is written under `dist/`, refuses to overwrite an existing file,
and is reproducible for the same source, toolchain, and
`SOURCE_DATE_EPOCH`. It installs the seven programs under `/usr/bin`, the
exact `0547:c003` udev rule, public documentation, and package metadata. The
build itself does not install anything, open the camera, or load a kernel
module. Installation and removal ask udev to reload its rules when `udevadm`
is present; this never resets or opens a USB device. Inspect and install it
with:

```sh
dpkg-deb --info dist/tucsen-tca-camera_*.deb
sudo apt install ./dist/tucsen-tca-camera_*.deb
tca-v4l2 --diagnose-install
```

The core reader remains a userspace libusb program. FFmpeg, V4L2 utilities,
and `v4l2loopback` are recommended application-bridge packages; the
camera-specific package does not supply a kernel driver. Reconnect the camera
after installation so the packaged udev rule is applied. Remove the package
with `sudo apt remove tucsen-tca-camera`.

## Capture

Capture three frames while preserving the first untouched device frame:

```sh
mkdir -p capture
./build/tca-camera capture \
  --frames 3 \
  --raw-first capture/first-device-frame.raw \
  --bayer capture/three-frames.bayer \
  --timestamps capture/three-frames-timestamps.csv \
  --exposure-ms 400 \
  --gain 20
```

Mode 2 (1280×960) is the default. Add `--mode 0` for 3664×2748 capture:

```sh
./build/tca-camera capture \
  --frames 1 --mode 0 \
  --raw-first capture/full-device-frame.raw \
  --bayer capture/full-frame.bayer \
  --exposure-ms 100 --gain 20
```

`--frames 0` streams until interrupted. Bayer output can be `-` for stdout:

```sh
./build/tca-camera capture \
  --frames 0 --raw-first first-device-frame.raw --bayer - \
  --exposure-ms 400 --gain 20 \
| ffplay -f rawvideo -pixel_format bayer_grbg8 \
    -video_size 1280x960 -framerate 6 -i -
```

The Bayer phase is still provisional. For a lossless still at the native
preview resolution, or a scaled still from the same full frame:

```sh
ffmpeg -hide_banner -loglevel error -f rawvideo \
  -pixel_format bayer_grbg8 -video_size 1280x960 \
  -i capture/one-frame.bayer -frames:v 1 capture/still-1280x960.png

ffmpeg -hide_banner -loglevel error -f rawvideo \
  -pixel_format bayer_grbg8 -video_size 1280x960 \
  -i capture/one-frame.bayer -frames:v 1 \
  -vf scale=800:600 capture/still-800x600.png
```

Capture a motion sequence directly to a broadly playable MP4 file:

```sh
./build/tca-camera capture \
  --frames 0 --raw-first capture/stream-first-device.raw --bayer - \
  --exposure-ms 100 --gain 256 \
| ffmpeg -hide_banner -loglevel warning \
    -f rawvideo -pixel_format bayer_grbg8 \
    -video_size 1280x960 -framerate 6 -i - \
    -vf scale=640:480 -c:v libx264 -pix_fmt yuv420p capture/stream.mp4
```

Raw Bayer carries no embedded timestamps. Add `--timestamps FILE.csv` to write
one `CLOCK_MONOTONIC` capture-completion timestamp per assembled frame. The
sidecar uses `frame,monotonic_ns` columns and is flushed after every row so a
bounded or interrupted run retains its measurements. It is never sent to the
camera and cannot share a path with either image output. Without that sidecar,
`-framerate` only sets the recording/playback time base; it is not a
measurement of the camera's delivered frame rate. Use
`Ctrl-C` to stop an unbounded capture cleanly. On Linux, the V4L2 bridge below
lets ordinary camera applications consume the same corrected live stream.
On the tested microscope, 100 ms with gain 256 was bright with only about
0.0007% saturated raw pixels; illumination and specimens will require their
own settings.

Validate a completed sidecar and summarize its measured cadence:

```sh
scripts/tca-timing-stats capture/three-frames-timestamps.csv \
  --json capture/three-frames-timing.json
```

The analyzer rejects a wrong header, missing or repeated frame numbers,
non-monotonic timestamps, fewer than two frames, and output overwrite.

### One-command live view and recording

`tca-ffmpeg` packages the ordinary-application pipelines above without hiding
the raw evidence or camera settings. It works from the source tree or after
`make install` on both Linux and macOS. Open a live FFplay window with:

```sh
mkdir -p capture
scripts/tca-ffmpeg --view capture/view-first-device.raw 250 0 2 10
```

The final four values are exposure milliseconds, normalized gain, mode, and
the viewer time-base FPS. Close the FFplay window or press `Ctrl-C` to stop the
reader. The first untouched device record remains in the named raw file.

Record a bounded, broadly playable H.264 MP4 and retain measured producer
timestamps with:

```sh
scripts/tca-ffmpeg --record \
  capture/record-first-device.raw \
  capture/record.mp4 \
  capture/record-timestamps.csv \
  60 250 0 2 10
```

Here `60` is the exact frame count. Every output path must be new. Mode 2
allows 2–600 frames and defaults to a 10-fps media time base; mode 0 allows
2–30 complete 3664×2748 frames and defaults to 3 fps. These FPS values describe
playback/encoding time base, while the CSV records actual frame completion
times. Run `tca-timing-stats` on that CSV for measured cadence.

The helper contains no USB protocol and cannot issue arbitrary requests. Its
no-argument and `--diagnose-install` paths are explicitly USB-inert. On Linux,
use `tca-v4l2` instead when an application requires a discoverable
`/dev/video*` camera rather than a viewer or recording file.

Current controls are intentionally narrow and mode-aware:

- `--exposure-ms 1..480` in mode 2, or `1..1236` in mode 0
- `--gain 0..320`

The reader refuses unknown or duplicate options, refuses to overwrite output
files, and exposes no arbitrary USB request facility. If ownership has just
returned from another host, it may discard at most two prefix-invalid initial
warm-up frames before delivering frame zero. Each discard is logged, the first
untouched device frame remains preserved, and any prefix loss after delivery
begins is fatal.

When exposure or gain is requested, the device already has one record buffered
under its preceding settings. The reader consumes that record before publishing
frame zero, while preserving it in `--raw-first` for diagnosis. A one-frame
capture therefore reflects the requested controls rather than the stale buffer.

One headerless Bayer frame can be checked without NumPy or OpenCV:

```sh
scripts/tca-frame-stats capture/one-frame.bayer --mode 2
```

For a multi-frame stream, extract one exact frame first. The utility reports
SHA-256, dimensions, intensity percentiles, clipping, four sensor-parity
planes, and a phase-independent Laplacian focus score.

### White balance from the illuminated slide

If a blank part of the slide should be neutral, estimate channel multipliers
directly from that region. This incorporates the actual lamp temperature,
condenser, microscope optics, color filters, and sensor response:

```sh
scripts/tca-white-balance capture/one-frame.bayer --mode 2 \
  --phase grbg --roi 448,48,576,240
```

The JSON result includes raw channel medians, ideal gains, FFmpeg-safe gains,
and a `colorchannelmixer` filter. If an ideal gain exceeds FFmpeg's 2.0 limit,
the utility scales all three FFmpeg gains together so their chromatic ratios
remain unchanged. Apply the reported filter after Bayer conversion; for
example, the tested tungsten-lit field produced approximately red `0.87`,
green `1.0`, and blue `2.0`:

```sh
ffmpeg -f rawvideo -pixel_format bayer_grbg8 -video_size 1280x960 \
  -i capture/one-frame.bayer \
  -vf 'colorchannelmixer=rr=0.87:gg=1.0:bb=2.0' \
  -frames:v 1 capture/white-balanced.png
```

This makes the reference region chromatically neutral; it does not brighten
gray into display white. Exposure, gain, or a separate tone curve controls
brightness. Re-estimate after changing the lamp, condenser, optical path, or
camera gain substantially.

### Flat-field illumination correction

Optical alignment should remove as much field nonuniformity as possible first.
Residual multiplicative shading can then be calibrated without changing the
camera protocol or adding a kernel driver. Capture full-frame, unbinned dark
and flat streams at the same mode, objective, condenser, lamp voltage,
exposure, and gain used for imaging. Average 16–64 frames where practical;
translate or defocus the blank field between flat frames so specimen features
do not become part of the map.

The repository includes an inert-by-default guided session for the physical
part of that procedure. It refuses an existing output directory, locks one
exposure/gain/phase tuple, prompts separately for blocked darks, repositioned
flat batches, a fresh validation blank, and a real specimen, then builds the
map, corrects both validation frames, renders before/after PNGs, records
statistics, and hashes the complete bundle. With no token it sends no USB
transfer and changes no file:

```sh
tools/run_flat_field_capture_session.sh

tools/run_flat_field_capture_session.sh \
  --run-flat-field-capture-session \
  --output capture/10x-flat-session \
  --exposure-ms 250 --gain 0 --phase grbg
```

Do not press Enter at the dark prompt until illumination is physically blocked.
Do not use the specimen scene itself as a flat. The default four flat batches
make the required translation/defocus step explicit between groups of frames.

For example, after capturing 32-frame mode-2 streams as `darks.bayer` and
`flats.bayer`, create and inspect a calibration:

```sh
./build/tca-flat-field calibrate --mode 2 --phase grbg \
  --dark capture/darks.bayer --dark-frames 32 \
  --flat capture/flats.bayer --flat-frames 32 \
  --exposure-ms 250 --camera-gain 0 \
  --output capture/10x-mode2.tca-flat

./build/tca-flat-field inspect \
  --calibration capture/10x-mode2.tca-flat
```

The calibration stores a fixed-point mean dark level and gain for every Bayer
pixel. Each of R, G1, G2, and B is normalized to its own median flat signal, so
spatial shading is removed without silently performing white balance. Apply it
to one or more concatenated Bayer frames:

```sh
./build/tca-flat-field apply \
  --calibration capture/10x-mode2.tca-flat \
  --input capture/preview.bayer \
  --output capture/preview-flat-corrected.bayer
```

Input and output may be `-`, allowing the corrector to sit between the reader
and FFmpeg. It rejects truncated frames, refuses to overwrite files, and emits
only corrected Bayer bytes on standard output. Preserve the raw acquisition
and the calibration alongside any corrected derivative.

## Optional V4L2 camera

Install the distribution-maintained generic loopback module:

```sh
sudo apt install ffmpeg time v4l-utils v4l2loopback-dkms
scripts/tca-v4l2 --serve first-device-frame.raw
```

This creates `/dev/video42` by default, converts the 1280x960 mode-2 Bayer
stream to YUYV, and removes only the loopback device it created when stopped.
The adapter refuses to alter an existing loopback configuration. The custom
camera protocol still runs in userspace; `v4l2loopback` is an optional, generic
compatibility layer. The optional final argument selects mode 0 for a complete
3664x2748 application stream; mode 2 remains the default:

```sh
scripts/tca-v4l2 --serve capture/full-first-device.raw 42 250 0 0
```

Full-resolution YUYV frames are 20,137,344 bytes each, so applications and
storage must tolerate the larger buffers and lower physical-camera cadence.
To apply a matching calibration before demosaic and YUYV conversion:

```sh
TCA_FLAT_FIELD=capture/10x-mode2.tca-flat \
  scripts/tca-v4l2 --serve first-device-frame.raw
```

The V4L2 helper validates geometry, phase, exposure, and camera gain before
touching the camera, and retains the first unmodified device frame as before.
A mode-0 corrected stream similarly requires a 3664x2748 map captured with
the same exposure and gain.
To preserve the reader's measured producer cadence while an ordinary V4L2
application consumes the stream, add a new timestamp sidecar path:

```sh
TCA_FLAT_FIELD=capture/10x-mode2.tca-flat \
TCA_TIMESTAMPS=capture/v4l2-reader-timestamps.csv \
  scripts/tca-v4l2 --serve capture/v4l2-first-device.raw 42 250 0

scripts/tca-timing-stats capture/v4l2-reader-timestamps.csv \
  --json capture/v4l2-reader-timing.json
```

`TCA_TIMESTAMPS` is optional and does not alter the image stream. The bridge
requires a distinct, nonexistent regular-file path and passes it to the reader
as `--timestamps`; rows are flushed as frames are accepted. Consumer frame
counts and timestamps should be recorded separately by the application under
test, since the reader sidecar measures producer delivery rather than display
or recording cadence.

For the bounded final Linux application check, use the inert-by-default
acceptance harness. Running it without arguments only prints its contract. A
live run requires the exact token, a clean built worktree, exactly one attached
camera, an existing evidence parent, and pre-primed sudo credentials. The
calibration argument may be `-` for an explicitly uncorrected transport and
application test, or a valid matching map for the stricter corrected-stream
test:

```sh
tools/run_linux_v4l2_acceptance.sh

sudo -v
tools/run_linux_v4l2_acceptance.sh \
  --run-live-linux-v4l2-acceptance \
  "$PWD" - capture/evidence 42 250 0 60

# Repeat after a valid physical calibration to verify corrected delivery.
tools/run_linux_v4l2_acceptance.sh \
  --run-live-linux-v4l2-acceptance \
  "$PWD" capture/10x-mode2.tca-flat capture/evidence 42 250 0 60

# Complete full-resolution application path; final argument selects mode 0.
tools/run_linux_v4l2_acceptance.sh \
  --run-live-linux-v4l2-acceptance \
  "$PWD" capture/10x-mode0.tca-flat capture/evidence 42 250 0 6 0
```

The live path records producer timestamps, an exact bounded YUYV consumer
stream, per-frame digests, producer/consumer counts and cadence, device
metadata, cleanup status, immediate reader reuse, and a SHA-256 manifest. The
ordinary FFmpeg consumer also runs under a recorded wall-clock deadline based
on frame count and requested exposure; a stall terminates the consumer, cleans
up the bridge, and preserves the partial evidence instead of hanging. A
producer/consumer count delta is retained as bounded pipeline evidence and is
not automatically mislabeled as a dropped-frame count. The live harness
defaults to mode 2; an optional final `0` selects mode 0 and applies its
geometry, exposure range, byte counts, analyzer mode, and matching calibration
contract throughout. An uncorrected run proves physical USB-to-application
transport without claiming illumination correction; it records
`calibration_mode=uncorrected` and hashes that fact into the evidence bundle.
A later map-backed run remains required before claiming corrected physical
Linux delivery.

The same bridge can be exercised without the camera before a physical run.
This root-only, token-gated acceptance substitutes a deterministic reader,
applies a synthetic flat-field map, attaches and detaches two ordinary V4L2
consumers, deliberately slows the second consumer, checks bounded bridge-tree
RSS, and verifies device/module cleanup. It never imports libusb or sends a USB
transfer:

```sh
tools/run_v4l2_bridge_synthetic_acceptance.sh
sudo tools/run_v4l2_bridge_synthetic_acceptance.sh \
  --run-v4l2-bridge-synthetic-acceptance capture/v4l2-synthetic-evidence 44

sudo tools/run_v4l2_bridge_synthetic_acceptance.sh \
  --run-v4l2-bridge-synthetic-acceptance capture/v4l2-mode0-evidence 45 0
```

The synthetic pass proves bridge lifecycle, correction, backpressure, and
cleanup behavior on that Linux host. It does not replace the physical-camera
application run or validate optical calibration. The optional final mode
argument lets the same contract validate both supported application
geometries; mode 2 uses four normal plus eight slow frames, while mode 0 uses
two normal plus three slow frames to bound evidence size.

## Protocol and safety

The recovered wire behavior, frame layout, evidence boundary, and known
unknowns are documented in [`docs/protocol.md`](docs/protocol.md). This project
does not contain vendor binaries or firmware and does not write camera
non-volatile memory. The implementation performs no USB reset, configuration
change, alternate-setting change, or firmware upload.

## Contributing hardware results

Please include:

- output of `lsusb -v -d 0547:c003` (remove serials if present);
- platform, kernel, and libusb versions;
- the reader's stderr log;
- frame byte counts and SHA-256 hashes; and
- whether the sensor was optically exposed and mounted on a microscope.

Do not upload proprietary vendor packages or camera images containing private
material. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License and names

Licensed under the Apache License 2.0. AmScope and Tucsen are names or
trademarks of their respective owners. This independent project is not
affiliated with or endorsed by them.
