# Field illumination nonuniformity and correction plan

Date: 2026-10-04

## Observation

The 10x, 250-ms, gain-zero, white-balanced preview has a bright center/upper
field and darker lower/left edges. Equal 256x192 regions measured from
`optical-10x-preview-mode2-white-balanced.png` give:

| Region | Mean luma |
|---|---:|
| center | 178.3 |
| top-left | 165.7 |
| top-middle | 193.9 |
| top-right | 184.6 |
| left-middle | 152.1 |
| right-middle | 175.7 |
| bottom-left | 134.0 |
| bottom-middle | 149.8 |
| bottom-right | 157.6 |

The top-middle/bottom-left ratio is about 1.45 and center/bottom-left about
1.33. This is not merely symmetric radial vignetting. Lamp/condenser centering,
low-power condenser coverage, and camera-relay/image-circle clipping are the
first hypotheses. The values describe this scene, not a calibrated flat.

## Optical alignment checklist

1. Use a clean blank slide and keep the camera preview visible.
2. Establish Köhler illumination: focus the specimen; close the field
   diaphragm; focus its edge with condenser height; center it with the
   condenser screws; open it just beyond the camera field.
3. Inspect the objective rear aperture if possible. Center and focus the lamp
   filament/collector image so it fills the condenser aperture evenly. Set the
   condenser aperture to about 70–80% of the objective rear aperture; do not
   use it as the main brightness control.
4. Check the microscope's documented low-power condenser arrangement for 10x.
   Lower or swing out a top lens only when that condenser design calls for it.
5. Reseat and center the photo port, C-mount adapter, and relay lens. Check that
   the relay covers the sensor and no stop, reducer, filter, or extension clips
   the image circle.
6. Clean accessible condenser, field-lens, objective, and adapter surfaces.
   Use lamp voltage or a heat-safe neutral-density filter for brightness after
   alignment.
7. Rotate the camera/adapter 180 degrees and recapture the blank. A rotating
   pattern implicates relay/camera geometry; a fixed pattern implicates the
   illumination path. Compare another objective/condenser setting as well.

## Calibrated postprocessing

Acquire 16–64 dark frames with light blocked and 16–64 translated or defocused
blank-field frames, using the same objective, condenser, lamp voltage,
exposure, gain, full sensor area, and binning as acquisition. For each Bayer
plane `c` (R, G1, G2, B), compute in floating point:

```text
C_c(x,y) = (I_c(x,y) - D_c(x,y))
           * median(F_c - D_c) / max(F_c(x,y) - D_c(x,y), epsilon)
```

Apply global white balance after this correction and clip only at final output.
A smoothed 2D flat corrects the illumination envelope while retaining dust; an
unsmoothed flat can also remove fixed dust shadows. Because the measured field
is asymmetric, use a 2D map rather than a radial-only model. Large-kernel
background division is an approximation when no flat exists. Rolling-ball
subtraction, homomorphic filtering, and CLAHE can improve appearance but may
distort quantitative intensity and should be labeled accordingly.

Recalibrate after changes to objective, condenser, camera adapter, lamp voltage,
or other optical-path elements. Preserve original frames, calibrations,
settings, and hashes. A precomputed correction map can run in user space before
demosaicing or V4L2 output; it does not require a kernel driver.

## References

- Nikon MicroscopyU, “Microscope Alignment for Köhler Illumination”:
  <https://www.microscopyu.com/tutorials/kohler>
- Nikon MicroscopyU, “Conjugate Planes in Optical Microscopy”:
  <https://www.microscopyu.com/microscopy-basics/conjugate-planes-in-optical-microscopy>
- Micro-Manager, “Flat-Field Correction”:
  <https://micro-manager.org/Flat-Field_Correction>
