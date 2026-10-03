# Tucsen TCA camera userspace reader

Early, independently developed userspace support for the legacy AmScope/Tucsen
USB microscope camera identified as `0547:c003` (`10MP CMOS Camera`, commonly
sold as TCA-10.0N/IS1000-family hardware).

The reader cold-initializes the camera with `libusb`, captures a continuous
1280×960 Bayer8 stream, validates and removes transport markers, and exposes
bounded exposure and gain controls. A Raspberry Pi 5 has captured 30
consecutive frames and fed the live stream through FFmpeg and a temporary
V4L2 camera device. No vendor driver and no camera-specific kernel module are
required.

> **Alpha hardware support:** one physical camera has been tested. The sensor
> was covered during protocol work, so final color/Bayer-phase confirmation,
> image-quality calibration, and full 10-megapixel mode remain open. Preserve
> raw frames and report your hardware identity when testing another unit.

## Supported state

| Capability | Status |
|---|---|
| Raspberry Pi / AArch64 Linux cold start | Verified live |
| Continuous 1280×960 Bayer8 capture | Verified live |
| Exposure and analog gain writes | Transport-verified live |
| FFmpeg/stdout pipeline | Verified live |
| Optional `/dev/video*` through `v4l2loopback` | Verified live |
| Apple Silicon build | Verified |
| Direct capture on macOS | Not yet physically tested |
| Full 3664×2748 mode | Not yet enabled |
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

`--frames 0` streams until interrupted. Bayer output can be `-` for stdout:

```sh
./build/tca-camera capture \
  --frames 0 --raw-first first-device-frame.raw --bayer - \
  --exposure-ms 400 --gain 20 \
| ffplay -f rawvideo -pixel_format bayer_grbg8 \
    -video_size 1280x960 -framerate 2 -i -
```

Current controls are intentionally narrow:

- `--exposure-ms 1..480`
- `--gain 0..320`

The reader refuses unknown or duplicate options, refuses to overwrite output
files, and exposes no arbitrary USB request facility.

## Optional V4L2 camera

Install the distribution-maintained generic loopback module:

```sh
sudo apt install ffmpeg v4l-utils v4l2loopback-dkms
scripts/tca-v4l2 --serve first-device-frame.raw
```

This creates `/dev/video42` by default, converts the Bayer stream to YUYV, and
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

MIT licensed. AmScope and Tucsen are names or trademarks of their respective
owners. This independent project is not affiliated with or endorsed by them.
