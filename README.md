# Tucsen TCA camera userspace reader

Early, independently developed userspace support for the legacy AmScope/Tucsen
USB microscope camera identified as `0547:c003` (`10MP CMOS Camera`, commonly
sold as TCA-10.0N/IS1000-family hardware).

The reader cold-initializes the camera with `libusb`, captures 1280×960 preview
or 3664×2748 full-resolution Bayer8 frames, validates and removes transport
markers, and exposes bounded exposure and gain controls. A Raspberry Pi 5 has
completed a 14,400-frame preview endurance run, captured consecutive full-size
frames, and fed the preview stream through FFmpeg and a temporary V4L2 camera
device. No vendor driver and no camera-specific kernel module are required.

> **Alpha hardware support:** one physical camera has been tested. The sensor
> was covered during protocol work, so final color/Bayer-phase confirmation
> and image-quality calibration remain open. Preserve
> raw frames and report your hardware identity when testing another unit.

## Full report and research record

The complete investigation report, including device identification, recovered
protocol evidence, driver comparisons, and the staged validation plan, is
intended for publication in the
[Journal of Bjorn](https://la3lma.github.io/journal-of-bjorn/) as
[Recovery Plan for a Legacy AmScope Microscope Camera](https://la3lma.github.io/journal-of-bjorn/papers/microscope-window-sensor.html).
The article link is reserved for the report and may return 404 until the journal
entry is published.

Reproducible physical checks and their evidence hashes are summarized in the
[validation record](docs/validation.md).

The remaining microscope-mounted checks have a reproducible
[optical validation procedure](docs/optical-validation.md), including Bayer
phase, orientation, exposure/gain sweeps, focus scoring, and a full-resolution
still.

## Supported state

| Capability | Status |
|---|---|
| Raspberry Pi / AArch64 Linux cold start | Verified live |
| Continuous 1280×960 Bayer8 capture | Verified live |
| Exposure and analog gain writes | Transport-verified live |
| FFmpeg/stdout pipeline | Verified live |
| Optional `/dev/video*` through `v4l2loopback` | Verified live |
| Connected-camera Pi reboot and cold reopen | Verified live |
| Apple Silicon build | Verified |
| Apple Silicon libusb capture through Pi relay | Verified live |
| Native-cable capture on macOS | Not yet physically tested |
| Full 3664×2748 Bayer8 capture | Verified live |
| Optical color and focus validation | Awaiting microscope setup |

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

## Capture

Capture three frames while preserving the first untouched device frame:

```sh
mkdir -p capture
./build/tca-camera capture \
  --frames 3 \
  --raw-first capture/first-device-frame.raw \
  --bayer capture/three-frames.bayer \
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
    -video_size 1280x960 -framerate 2 -i -
```

Current controls are intentionally narrow and mode-aware:

- `--exposure-ms 1..480` in mode 2, or `1..1236` in mode 0
- `--gain 0..320`

The reader refuses unknown or duplicate options, refuses to overwrite output
files, and exposes no arbitrary USB request facility. If ownership has just
returned from another host, it may discard at most two marker-invalid initial
warm-up frames before delivering frame zero. Each discard is logged, the first
untouched device frame remains preserved, and any marker loss after delivery
begins is fatal.

One headerless Bayer frame can be checked without NumPy or OpenCV:

```sh
scripts/tca-frame-stats capture/one-frame.bayer --mode 2
```

For a multi-frame stream, extract one exact frame first. The utility reports
SHA-256, dimensions, intensity percentiles, clipping, four sensor-parity
planes, and a phase-independent Laplacian focus score.

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
