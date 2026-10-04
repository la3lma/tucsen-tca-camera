# Tucsen TCA camera userspace reader

Early, independently developed userspace support for the legacy AmScope/Tucsen
USB microscope camera identified as `0547:c003` (`10MP CMOS Camera`, commonly
sold as TCA-10.0N/IS1000-family hardware).

**Project map:** [live Docstack](https://la3lma.github.io/tucsen-tca-camera/docstack/)
· [PDF investigation report](https://la3lma.github.io/tucsen-tca-camera/report/microscope-window-sensor.pdf)
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
| FFmpeg/stdout pipeline | Verified live |
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

The camera-specific implementation is entirely userspace code. On a headless
Linux system, either run with appropriate USB permissions or install the
optional rule in [`udev/99-tucsen-tca-camera.rules`](udev/99-tucsen-tca-camera.rules).

## Install and remove

Install the reader, V4L2 helper, frame and timing analyzers, white-balance
estimator, and flat-field calibration/filter tool under the selected prefix:

```sh
sudo make install PREFIX=/usr/local
```

Remove exactly those five installed programs:

```sh
sudo make uninstall PREFIX=/usr/local
```

Packagers can set `DESTDIR` for a staged install or removal. These targets do
not modify the optional udev rule or distribution-managed `v4l2loopback`
package.

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
sudo apt install ffmpeg v4l-utils v4l2loopback-dkms
scripts/tca-v4l2 --serve first-device-frame.raw
```

This creates `/dev/video42` by default, converts the mode-2 Bayer stream to YUYV, and
removes only the loopback device it created when stopped. The adapter refuses
to alter an existing loopback configuration. The custom camera protocol still
runs in userspace; `v4l2loopback` is an optional, generic compatibility layer.
To apply a matching calibration before demosaic and YUYV conversion:

```sh
TCA_FLAT_FIELD=capture/10x-mode2.tca-flat \
  scripts/tca-v4l2 --serve first-device-frame.raw
```

The V4L2 helper validates geometry, phase, exposure, and camera gain before
touching the camera, and retains the first unmodified device frame as before.

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
