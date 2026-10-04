# Historical Micro-Manager application precedent

Evidence date: 2026-09-29

## Confirmed exact-model use

Nilay Jayant Lakhkar's 2014 University College London PhD thesis, *Phosphate
Glass Microspheres as Cell Microcarrier Substrates for Bone Tissue Engineering
Applications*, identifies a "Tucsen TCA-10.0-N camera" running with
Micro-Manager for live view and an 80-hour, one-frame-per-hour time-lapse. The
equipment appendix specifies Micro-Manager 1.4, and the procedure uses its
`Live` view and `Multi-D Acq.` workflow.

This is direct historical evidence that the exact camera model was usable from
a general scientific-imaging application. It is not evidence that the camera
used UVC, nor does it identify the adapter or Windows transport path.

Source:

- UCL Discovery thesis PDF:
  <https://discovery.ucl.ac.uk/id/eprint/1436722/2/Nilay_Jayant_Lakhkar_PhD_Thesis.pdf._redacted.pdf>
- Local preserved copy:
  `work/reference-source/lakhkar-phd-thesis.pdf`
- PDF SHA-256:
  `f898da66ecd51fa10a13d8bd844bfb113bc30eb6f03cab5d75404ce1f402db36`
- Relevant printed pages: 76 and 222--223 (PDF pages 77 and 223--224 when
  counted from zero by common PDF tooling).

The URL was opened successfully on 2026-09-29. The author, title, institution,
year, camera model, Micro-Manager version, and described workflow were checked
against the preserved PDF text.

## Historical adapter-tree boundary

The official Micro-Manager `mmCoreAndDevices` repository was cloned to
`work/reference-source/mmCoreAndDevices`. The nearest commit before the thesis
PDF creation date is:

```text
ebaa59d726b96870a1beb9efe1de9f6dec47e804
2014-07-11T10:42:40Z
Adding new SW Release.
```

At that commit, `DeviceAdapters/` contains generic `TwainCamera` and
`OpenCVgrabber` adapters. A case-insensitive search of the adapter tree finds
no `Tucsen` or `TCA-10` string and no legacy Tucsen-specific adapter. The
generic TWAIN adapter advertises `Twain camera`, enumerates installed TWAIN
sources, implements still capture, and provides sequence acquisition. The
OpenCV adapter opens the first system camera through `cvCaptureFromCAM`.

This narrows the plausible historical paths to a generic system-camera source,
a generic TWAIN source supplied separately by Tucsen, or an adapter not present
in the public tree. It does **not** distinguish among those paths. No recovered
file currently proves that TSView7 or the matched TCA driver registered a
DirectShow or TWAIN source.

Official repository:
<https://github.com/micro-manager/mmCoreAndDevices>

Current preserved checkout commit:
`e28c50d10c522c4f2329d3a6a9ac74cb7b7c190e`

## Engineering consequence

Micro-Manager is a credible real-application acceptance target after the
portable reader works. On Linux, the shortest first bridge remains a standard
V4L2 loopback or media pipeline, because it can serve Micro-Manager's generic
camera path as well as FFmpeg, GStreamer, and ordinary V4L2 consumers without
duplicating USB protocol logic. A dedicated modern Micro-Manager adapter may be
considered later if it materially improves controls, metadata, or reliability.

This precedent does not change the D40 initialization evidence gate and does
not authorize any new live USB transaction.
