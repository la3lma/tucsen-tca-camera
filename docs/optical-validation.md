# Optical validation procedure

This procedure closes the remaining calibrated optical checks. Initial
microscope imagery already exposed and corrected a frame-assembly defect; the
steps below now validate color, response, focus, and the application boundary.
It does not authorize new USB commands or firmware writes.

## Required setup

- camera mounted in its intended microscope optical path;
- a clean, textured specimen for focus and a color reference with distinguishable
  red and blue regions for Bayer phase;
- stable, diffuse illumination with manual intensity control;
- Raspberry Pi or another tested Linux host with the public reader built;
- FFmpeg and the repository's `scripts/tca-frame-stats` utility; and
- enough free storage for preserved raw frames and JSON records.

Remove the protective tape only after the camera is supported and the optical
opening faces a clean environment. Do not touch the sensor window. Keep loose
adhesive, fibers, tools, and microscope adapters away from the glass.

Use a new directory and record the reader commit, host, microscope, objective,
illumination, specimen, camera orientation, and UTC time before capture.

```sh
mkdir -p capture/optical
git rev-parse HEAD > capture/optical/reader-commit.txt
uname -a > capture/optical/uname.txt
date -u +%Y-%m-%dT%H:%M:%SZ > capture/optical/start-utc.txt
```

## 1. Preview baseline

Start with moderate light, preview mode, gain 20, and 100-ms exposure:

```sh
./build/tca-camera capture \
  --frames 1 \
  --raw-first capture/optical/preview-device.raw \
  --bayer capture/optical/preview.bayer \
  --exposure-ms 100 --gain 20

scripts/tca-frame-stats capture/optical/preview.bayer \
  --json capture/optical/preview.stats.json
```

Require exact lengths of 1,229,312 device bytes and 1,228,800 Bayer bytes,
`frames=1 status=ok`, no prefix discard after frame delivery begins, and low
zero/saturated fractions. If most pixels are zero or 255, adjust illumination
or exposure before judging color or focus.

## 2. Bayer phase and orientation

Generate all four candidate interpretations from the same preserved frame:

```sh
for phase in rggb grbg gbrg bggr; do
  ffmpeg -hide_banner -loglevel error -n \
    -f rawvideo -pixel_format "bayer_${phase}8" \
    -video_size 1280x960 -i capture/optical/preview.bayer \
    -frames:v 1 "capture/optical/phase-${phase}.png"
done
```

The `-n` option deliberately refuses to overwrite an earlier rendering. Use a
fresh capture directory for a repeated session so the source frame and its
derived images cannot be mixed accidentally.

Choose the phase that renders the known red and blue reference regions with
correct hue and without swapped channels. Do not infer phase from a gray target
or from the covered-sensor dark frames. Record the chosen phase and preserve
all four candidates.

Use an asymmetric target or slide label to determine horizontal/vertical
orientation. Record rotation and mirroring separately from Bayer phase; do not
silently bake orientation into transport decoding.

### Neutral-background white balance

If a blank slide region should be neutral, select a clean ROI and estimate
channel gains without changing the preserved Bayer frame:

```sh
scripts/tca-white-balance capture/optical/preview.bayer --mode 2 \
  --phase grbg --roi 448,48,576,240 \
  > capture/optical/white-balance.json
```

Apply the emitted `ffmpeg_filter` after demosaicing. Record the ROI and gains.
This in-situ correction includes the lamp and optical path, but a neutral field
cannot by itself prove Bayer phase or establish colorimetric accuracy.

### Field-uniformity calibration

After centering the lamp, condenser, field diaphragm, and camera relay, capture
16–64 dark frames with illumination blocked and 16–64 blank-field frames at
the final optical and camera settings. Use the full sensor without binning or
ROI. Translate or defocus the blank between flat frames.

```sh
./build/tca-flat-field calibrate --mode 2 --phase grbg \
  --dark capture/optical/darks.bayer --dark-frames 32 \
  --flat capture/optical/flats.bayer --flat-frames 32 \
  --output capture/optical/10x-mode2.tca-flat
./build/tca-flat-field inspect \
  --calibration capture/optical/10x-mode2.tca-flat \
  > capture/optical/10x-mode2-flat-field.json
```

Apply the map before demosaicing, then apply global white balance. Record the
calibration hash and settings. Repeat after changing objective, condenser,
lamp voltage, relay, exposure/gain path, binning, or sensor area.

## 3. Exposure response

Hold gain, illumination, focus, and specimen fixed. Capture a conservative
preview sweep with distinct files:

```sh
for exposure in 25 50 100 200 400; do
  ./build/tca-camera capture --frames 1 \
    --raw-first "capture/optical/exposure-${exposure}ms-device.raw" \
    --bayer "capture/optical/exposure-${exposure}ms.bayer" \
    --exposure-ms "$exposure" --gain 20
  scripts/tca-frame-stats \
    "capture/optical/exposure-${exposure}ms.bayer" \
    --json "capture/optical/exposure-${exposure}ms.stats.json"
done
```

The median/mean should increase monotonically before clipping. Record the
usable interval and any exposure whose saturated fraction becomes material.
This establishes behavior, not a promise of photometric calibration.

## 4. Gain response

Choose a non-clipping exposure and hold every other variable fixed:

```sh
for gain in 0 20 64 128 192 256 320; do
  ./build/tca-camera capture --frames 1 \
    --raw-first "capture/optical/gain-${gain}-device.raw" \
    --bayer "capture/optical/gain-${gain}.bayer" \
    --exposure-ms 100 --gain "$gain"
  scripts/tca-frame-stats "capture/optical/gain-${gain}.bayer" \
    --json "capture/optical/gain-${gain}.stats.json"
done
```

Confirm a monotonic response over the useful range and note clipping, noise,
or discontinuities at the documented encoding boundaries. Do not characterize
the normalized gain number as decibels without an independent calibration.

## 5. Manual focus curve

Keep exposure, gain, light, specimen, phase, and field of view fixed. Capture
at least five named Z positions spanning visibly soft focus on both sides of
the best-looking plane. Run `tca-frame-stats` on each frame and compare
`focus.value`, the variance of a four-neighbour Laplacian over 2x2 Bayer-tile
mean intensity.

The score should have a reproducible local maximum near visual best focus.
Reject a focus series with substantial clipping or a moving specimen. The
metric is an initial autofocus candidate, not an acceptance criterion for every
specimen type.

## 6. Full-resolution still

After phase, orientation, exposure, gain, and focus are stable, capture the
same field in mode 0:

```sh
./build/tca-camera capture --frames 1 --mode 0 \
  --raw-first capture/optical/full-device.raw \
  --bayer capture/optical/full.bayer \
  --exposure-ms 100 --gain 20

scripts/tca-frame-stats capture/optical/full.bayer \
  --json capture/optical/full.stats.json
```

Require exact lengths of 10,068,992 device bytes and 10,068,672 Bayer bytes.
Render it using the accepted phase at 3664x2748 and inspect the full field for
orientation, clipping, dead rows/columns, repeated blocks, transport seams,
unexpected edge strips, and focus consistency.

## 7. Application-boundary check

Run the existing V4L2 adapter with the optically exposed camera and view or
record it in an ordinary application. Confirm that the application sees
1280x960 YUYV, starts and stops cleanly, and that exposure/gain changes made at
reader startup are visible in the image.

## Acceptance record

Preserve all raw Bayer files, untouched device frames, generated previews,
JSON statistics, stderr logs, commit/version information, and SHA-256 hashes.
Record pass/fail for:

1. preview and full-resolution byte counts and prefix validation;
2. Bayer phase, image orientation, and neutral-background white balance;
3. monotonic, bounded exposure and gain response;
4. a reproducible focus-score maximum near visual focus;
5. no visible transport seams or repeated/corrupt regions;
6. ordinary-application preview through V4L2; and
7. clean reader/application shutdown followed by immediate reopen.

Only after these checks should the report claim optical color/focus validation
or assign a final Bayer phase.
