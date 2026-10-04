# Apple Silicon physical flat-field pipeline self-test

Date: 2026-10-04

## Scope and result

This is a real-camera transport and correction-pipeline test, not a valid
optical calibration. The AmScope/Tucsen `0547:c003` camera remained mounted on
the microscope and connected directly to the Apple Silicon workstation. The
public reader captured exact 1280x960 Bayer records, and the public
`tca-flat-field` implementation calibrated and applied a full-size per-pixel
map without changing frame geometry or losing frames.

The deliberately invalid reference set used the illuminated specimen scene as
its own "flat." As expected, applying that map suppresses the scene as well as
the illumination gradient. This is useful evidence that the physical-size
reader, map builder, and filter agree pixel-for-pixel; it is not evidence that
the resulting image is scientifically or aesthetically usable.

## Physical capture

At 250-ms exposure and normalized gain 0, `tca-camera` captured 24 complete
preview frames:

```text
device record bytes:       1,229,312
Bayer bytes per frame:     1,228,800
24-frame Bayer stream:    29,491,200
reader result:             frames=24 status=ok
```

The first 16 frames were used as the intentionally invalid self-flat and the
last eight as input. A second physical run at 1-ms exposure and gain 0 captured
16 complete frames while the microscope illumination remained on. Its first
frame had mean 10.684, median 11, minimum 9, maximum 13, and no zero or
saturated pixels. This is therefore an **illuminated low-exposure proxy**, not
a blocked-light dark reference and not a substitute for a same-settings dark.

The first 250-ms input frame had mean 153.116, median 167, p99 211, and no zero
or saturated pixels. Its 3x3 equal-area region means were:

```text
152.681433  172.238378  171.766371
140.207475  161.901083  162.609617
128.833172  140.616320  147.098112
```

The maximum/minimum region ratio was 1.336910, consistent with the previously
observed asymmetric illumination field.

## Diagnostic correction

A first calibration combined the 16 self-flat frames with a synthetic all-zero
dark. A second calibration combined them with the 16 illuminated 1-ms proxy
frames. The latter reported Bayer-plane flat-minus-dark reference levels of
182.3125, 159.0, 164.0625, and 73.9375 for R, G1, G2, and B, with ten invalid
blue-plane pixels and no invalid pixels in the other planes. It corrected all
eight input frames with `frames=8 ... status=ok`.

The first proxy-dark-corrected frame had mean 144.841, median 162, p99 186,
ten zero pixels corresponding to the rejected blue-plane positions, and no
saturated pixels. Its 3x3 region means were:

```text
144.820232  144.780621  144.906418
144.828206  144.772563  144.898507
144.849773  144.788510  144.920660
```

The maximum/minimum ratio fell from 1.336910 to 1.001023. That near-uniform
output is the expected failure mode of calibrating against the same static
scene: the correction divides away both shading and specimen structure. It
proves the full-size correction math and stream plumbing, while simultaneously
demonstrating why a translated, defocused, or otherwise feature-free blank is
mandatory.

## Provenance hardening prompted by the test

The original `TCAFF01` maps recorded geometry, Bayer phase, frame counts, and
gain limits, but not the exposure and camera gain at acquisition. The two
diagnostic maps therefore inspect as `exposure_ms: null` and
`camera_gain: null`. Public commit `6eb68a7` reuses the final four reserved
header bytes to store both values while keeping old maps readable and direct
application byte-compatible.

New calibrations can record `--exposure-ms` and `--camera-gain`; the Linux
`tca-v4l2` bridge now rejects a map unless its geometry, Bayer phase, exposure,
and gain match the requested camera controls. A Raspberry Pi synthetic
end-to-end preflight with a 100-ms/gain-20 map delivered six corrected frames
through `/dev/video43` and cleaned up the temporary node and module. A
deliberate 101-ms request failed with status 65 before creating a raw file,
device node, loading the module, or touching the camera. Native macOS and Linux
tests and GitHub CI all pass commit `6eb68a7`.

## Required physical calibration

The next optically meaningful run must keep objective, condenser, lamp voltage,
relay, sensor area, Bayer phase, exposure, and gain fixed, then acquire:

1. 16-64 dark frames with illumination physically blocked;
2. 16-64 blank-field frames without clipping, translating or defocusing the
   blank between frames so specimen detail cannot enter the map; and
3. a fresh blank plus a real specimen for quantitative before/after checks.

The map must be built with the same exposure and gain that the V4L2 bridge will
request. Any optical-path or acquisition-setting change requires a new map.

## Preserved evidence

The working set is retained under
`work/macos-physical-flatfield-selftest.64WGMP/`. Selected SHA-256 hashes are:

```text
3717fdb97304b7de23370bd33033689986bbdbaeeaad3ab481b79672a4237f03  first-device-frame.raw
22226d313db179cb8a5fdd0353a6a028fd8e345a2204b9b259ce01435d285e96  twenty-four-frames.bayer
fcaa0c2916d50021a502bfbe00966290eef875e35e8149b373839b150e414732  illuminated-1ms-proxy-dark-sixteen.bayer
b88eb92558bbda82e1ab8481db0413212a99bd694bd3f1e57aff118447dcee63  self-flat-proxy-dark-grbg.tca-flat
2bfafe86a522607882ff108f7a5c7b2353082cd0579afd2927903ea7eb2665d8  eight-proxy-dark-corrected-frames.bayer
d376a0b058be8d7600fb008ca6eab4828790fd37668cc020e0a13e1c41cad2c5  input-frame-1.stats.json
f9ba9dfc454c4ca12e081c623d1c235b4f8f883d4059389ccae4dd30f7d6ad34  proxy-dark-frame-1.stats.json
95830256e830077197a58ae7e3126d372257ef8f31dbbf1f4aac3a414528c511  proxy-dark-corrected-frame-1.stats.json
014aaa740f66d7c6853ab2bde78a92d62c9cd4ff1e6bf1e6e366a0a405806743  input-frame-1.png
2501a266b7a36f3998ad24475688e2b5e4657aa1f2a0efa57bd2a47101da17d9  proxy-dark-corrected-frame-1.png
```
