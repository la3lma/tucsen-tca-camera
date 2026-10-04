# Candidate microscopy application stack above the C003 reader

Search date: 2026-10-03

## Scope

This note evaluates a suggested higher-level stack: ToupCam, Micro-Manager or
Pycro-Manager for acquisition and stage control, preview-stream autofocus, and
Fiji or MIST for tile stitching.  It separates camera transport support from
software that becomes useful only after a working frame source exists.

## Micro-Manager camera paths

The current Micro-Manager source was inspected at commit
`e28c50d10c522c4f2329d3a6a9ac74cb7b7c190e`.

### AmScope adapter: not this camera

Micro-Manager does contain `DeviceAdapters/AmScope`, but its own readme calls
it an adapter for AmScope MU-series USB 3 cameras on Windows.  Its source fixes
the offered model to `MU1403`, its Visual Studio project links ToupTek's 2016
ToupCam SDK, and the runtime instructions require the AmScope Windows driver
package.  It is therefore corroborating evidence for the AmScope/ToupTek
relationship, not support for the USB 2.0 Tucsen TCA-10.0N/IS1000
`0547:c003`.  The adapter's BSD-licensed source can still inform a future
native Micro-Manager adapter at the application-API level.

Source:

<https://github.com/micro-manager/mmCoreAndDevices/tree/e28c50d10c522c4f2329d3a6a9ac74cb7b7c190e/DeviceAdapters/AmScope>

### Video4Linux adapter: the shortest Linux integration path

The same source tree contains a Linux `Video4Linux` device adapter.  It accepts
a configurable `/dev/video*` path and resolution and includes YUYV input
handling.  This matches the boundary already proven by this project: the
camera-specific libusb reader publishes a temporary 1280-by-960 YUYV
`v4l2loopback` device which ordinary consumers have opened successfully.

The next Micro-Manager experiment should therefore be:

```text
0547:c003 camera
  -> tucsen-tca-camera userspace reader
  -> temporary V4L2 YUYV device
  -> Micro-Manager Video4Linux adapter
  -> Micro-Manager/Pycro-Manager acquisition
```

This keeps the recovered protocol in the public userspace reader and avoids a
second camera-specific USB implementation.  It must still be tested because
the adapter may impose format, buffer, or sequence-acquisition assumptions not
covered by the short FFmpeg consumer test.

Source:

<https://github.com/micro-manager/mmCoreAndDevices/blob/e28c50d10c522c4f2329d3a6a9ac74cb7b7c190e/DeviceAdapters/Video4Linux/video4linux2.cpp>

## Pycro-Manager's role

Pycro-Manager is an acquisition and automation layer above Micro-Manager Core;
it does not independently add support for an unrecognized camera.  Once the
Video4Linux adapter (or a future native C003 adapter) supplies frames, its
Python APIs and acquisition hooks can coordinate Z stacks, tiled XY
acquisitions, stages, processing, storage, and adaptive actions.

The practical order is therefore camera reader, V4L2/Micro-Manager acceptance,
stage identification and configuration, then Pycro-Manager automation.  This
also lets camera support remain usable outside the microscopy stack.

Sources:

- <https://pycro-manager.readthedocs.io/en/latest/backends.html>
- <https://pycro-manager.readthedocs.io/en/latest/acq_hooks.html>
- <https://github.com/micro-manager/pycro-manager/blob/c9c8acd1969fb5e55619d8284b6c1fd96fc236b4/docs/source/application_notebooks/Single_shot_autofocus_pycromanager.ipynb>

## Autofocus after the optical system is present

A coarse-to-fine Z search on the preview mode is a sensible first software
autofocus baseline.  For each candidate Z position, hold exposure, gain,
illumination, Bayer conversion, and crop constant; score a central or
sample-appropriate grayscale ROI; and use the variance of a Laplacian-filtered
image as the initial sharpness metric.  Search a bounded coarse interval,
rescan a narrower interval around the best coarse plane, then optionally take
the final image in 3664-by-2748 mode.

This is a future optical experiment, not a transport acceptance test.  The
sensor is presently covered, the microscope and sample are not attached, and
no motorized Z stage has been identified.  The Laplacian score must be checked
against real brightfield specimens because noise, low texture, saturation,
illumination changes, and Bayer artifacts can produce false maxima.  Preserve
the whole focus curve and compare at least one alternative gradient or
frequency-domain metric before making autofocus a release claim.

The suggestion to focus on preview rather than full resolution is consistent
with the transport geometry.  A full device frame is 10,068,992 bytes, so USB
2.0's 480-Mbit/s signalling rate gives an absolute, overhead-free ceiling of
about 5.96 frames/s before control, scheduling, exposure, and conversion costs.
The actual steady-state full-mode rate has not yet been benchmarked; “a few
frames per second” is a reasonable expectation, not a measured result.

## Tile acquisition and stitching

Fiji's Grid/Collection Stitching plugin and NIST's MIST are credible downstream
choices once an XY stage and reproducible, overlapping tile acquisition exist.
Fiji accepts grids or collections, can use approximate positions or metadata,
and offers virtual-stack/disk-backed operation for large datasets.  MIST is
specifically designed for 2D microscopy mosaics, models stage placement error,
and can treat time points as independent 2D datasets; it is not a volumetric
3D stitcher.

The acquisition layer should preserve raw tiles, calibrated pixel size,
commanded and reported XY/Z positions, overlap, exposure/gain, illumination,
focus score, and capture time.  A first benchmark should use a small 3-by-3
grid with roughly 10--20 percent overlap and compare the resulting placement
against stage coordinates before scaling up.

Sources:

- <https://imagej.net/plugins/grid-collection-stitching>
- <https://github.com/usnistgov/MIST/tree/26481de8dccf7f7c58ba86549556e8544368d1e4>

## Decision

The suggested stack does not replace the C003 reader, but it improves the
application roadmap:

1. retain the trace-derived userspace driver as the camera transport;
2. validate Micro-Manager through its Linux Video4Linux adapter;
3. add Pycro-Manager only after camera and stage devices work in MMCore;
4. implement and measure preview-mode coarse-to-fine autofocus after optical
   and motorized-Z hardware are available; and
5. evaluate Fiji and MIST on a small, metadata-rich tile grid before choosing a
   production stitching path.
