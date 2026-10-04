# Updated-firmware discovery (non-gating)

Search dates: 2026-09-27, 2026-09-29, 2026-10-03, and 2026-10-04

This is the low-priority research lane requested by the camera owner. It does
not gate the Linux reader plan, and no firmware image will be uploaded merely
because a filename or updater appears to match.

## Identity searched

- USB identity: `0547:c003`
- Official model names: `TCA-10.0N`, `TCA-10.0-N`, and `IS1000`
- Vendor/reseller names: Tucsen and AmScope

The official Tucsen discontinued-camera matrix maps the same VID/PID to two
software lineages:

- `TCA-10.0N` -> TCA driver plus TSView6 or TSView7
- `IS1000` -> Beta Camera Driver plus ISCapture 3.6.8

Source: <https://www.tucsen.com/uploads/Software-and-Driver-download-links.pdf>
(preserved locally as `work/tucsen-discontinued-camera-download-links.pdf`).

## Surfaces checked

- Tucsen's discontinued-camera matrix and linked packages.
- Tucsen's current support/download surfaces.
- AmScope's current MU-series camera support surface.
- The recovered TCA, Beta/IS1000, TSView6, TSView7, ISCapture, and AmScope v3
  installers already preserved under `work/`.
- Package contents and filenames for common firmware/updater forms, including
  `.hex`, `.iic`, `.bin`, `.fw`, `firmware`, and `update`.
- Public-web searches combining the VID/PID and both model names with
  `firmware`, `update`, `updater`, `EEPROM`, and `FX2`.

## 2026-09-29 current-package refresh

AmScope's official MU-series support page currently offers AmLite for ARM64
Linux dated 2026-04-13 and AmScope for Windows v4.12.31631. Both packages were
downloaded into `work/firmware-search/amscope-current/`, hash-pinned, and
extracted statically without running an installer or opening the camera.

| Official package | SHA-256 |
|---|---|
| `AmScopeAmLite.arm64-20260413.tar.bz2` | `a25fb2b6c9c04f7cf1c4888bd0a1fe188f1fa517c7bd11a4ff4ae41418c1aef4` |
| `AmScopeSetup_v4.12.31631.zip` | `8629021144d1d369dce22d132b3a31410c8f293eb840509becbd2e61611bd5d1` |

Primary source: <https://amscope.com/pages/camera-support-mu-series>.

Artifact URLs:

- <https://storage.googleapis.com/software-download-d79bb.appspot.com/software/AmLite/Linux/20260413/AmScopeAmLite.arm64.tar.bz2>
- <https://storage.googleapis.com/software-download-d79bb.appspot.com/software/AmScope/v4.12.31631/AmScopeSetup_v4.12.31631.zip>

Static inspection produced the following bounded result:

- The Linux archive contains 29 installed files, including an ARM64 AmLite
  executable, `libamcam.so`, and `99-amcam.rules`. The udev rule grants access
  to all devices from vendors `0547` and `04b4`; this is not a supported-model
  list and does not establish compatibility.
- Neither the Linux nor Windows extracted tree contains the strings `c003`,
  `TCA-10.0N`, `IS1000`, or `Tucsen`.
- The current Windows x86 and x64 `amcam.inf` files each enumerate 232 hardware
  IDs and identify driver version `1.0.0.29904` dated 2025-11-02. Neither INF
  contains `USB\\VID_0547&PID_C003`.
- No extracted filename uses a recognized standalone firmware form such as
  `.hex`, `.iic`, `.fw`, `.rom`, `.eep`, or `.eeprom`, and no filename contains
  `firmware`, `update`, or `updater`.
- The user-interface resources contain generic `Firmware Version` and
  `Software upgrade` labels. Those strings are application features, not an
  exact-device firmware claim or a separately recoverable image.

This refresh does not prove that `libamcam.so` could never communicate with the
camera, because a binary may discover devices without embedding an obvious
textual ID. It does show that the current MU-series Windows driver will not bind
to `0547:c003` through its supplied INF, and it found no candidate firmware
payload. No current package was executed against the camera.

## 2026-10-03 official-web refresh

Fresh searches of the official Tucsen and AmScope domains combined each exact
identity (`0547:c003`, `TCA-10.0N`, and `IS1000`) with `firmware`, `update`, and
`updater`. Tucsen's two currently indexed discontinued-camera endpoints still
resolve to the same three-page matrix:

- <https://www.tucsen.com/Home/Product/info/dataid/31.html>
- <https://www.tucsen.com/Home/Product/info/dataid/35.html>

The matrix still maps `TCA-10.0N` and `IS1000` to `0547:C003`, the TCA row to
the TCA driver/TSView lineage, and the Beta row to the ISCapture lineage. It
does not name a firmware image or updater for either exact model. Official
search results do expose firmware-update tools and `.bin`/`.hex` procedures for
newer Dhyana and GT camera families, but those pages claim different models and
do not claim VID/PID `0547:C003`. They are therefore evidence that Tucsen
publishes firmware when applicable, not compatible candidates for this device.
No new package was downloaded or executed during this refresh.

## 2026-10-04 ToupTek latest-SDK and updater refresh

ToupTek's official download centre now distinguishes a stable May 19, 2026
SDK from a latest release displayed as September 11, 2026. The latest archive,
`toupcamsdk.20260818.zip`, was downloaded only into the private project and
inspected statically. It has SHA-256
`3f177938023686321e7ab9de8ecc431d0ab061f5f1b72122525fc2598c47b446`
and declares SDK version `60.32327.20260818` in `toupcam.h`.

Primary source: <https://www.touptekphotonics.com/download/?category=SDK>.

The x86 and x64 Windows INF tables are identical at the compatibility boundary
relevant here: each explicitly lists 1,839 unique USB VID/PID pairs, but neither
contains `USB\\VID_0547&PID_C003`. Compared with the previously inspected stable
SDK's 1,768 pairs, the latest table adds 71 and removes none. All 71 additions
are vendor `0547`, spanning product IDs `167B` through `16C1`; this demonstrates
that the table really changed while strengthening, rather than merely
repeating, the C003 negative result. No textual exact-model match for `C003`,
`TCA-10.0N`, `IS1000`, or `MU1000` was found in the inspected package, and no
standalone firmware-like filename was present.

The same official page advertises `USBCameraSdkUpdate` as a driver update
package, but marks its stable, latest, and legacy entries unavailable and
provides no file URL or supported-model table. It is therefore not an
obtainable firmware/updater candidate, and the generic title supplies no exact
C003 compatibility claim. No package component was executed and the camera was
not opened.

## Result

No standalone firmware image, firmware manifest, or obtainable official
updater claiming compatibility with `0547:c003` was found. The official
archived material
provides Windows drivers and applications, not a separately identified camera
firmware payload. The 2026 AmScope packages add no exact C003 claim, and the
current AmScope Windows INF omits the device. ToupTek's newer September 2026
SDK also omits it despite adding 71 explicit USB IDs, and its generic updater
entry is unavailable. Current Tucsen and AmScope support pages do not list a
C003 firmware updater.

This is a bounded negative result, not proof that no such artifact ever
existed. Periodic archive and mirror searches remain worthwhile, but they must
not delay protocol recovery or the Linux reader.

## Important ambiguity

The recovered Windows INF files call the device a `Firmware Device` in
comments:

- TCA INF: `Tucsen Firmware Device`
- Beta INF: `IS1000 Firmware Device`

That label is not evidence of an uploadable firmware image. Neither inspected
driver package contains a separately named firmware file, and the current USB
device already enumerates with stable descriptors and one bulk-IN endpoint.
Treat the wording only as a historical driver label unless runtime tracing
proves a volatile upload step.

## Adoption gate for any future candidate

Before any firmware transfer, require all of the following:

1. Exact VID/PID and model/revision claim from an attributable source.
2. Cryptographic hash and preserved original package.
3. Static proof of transfer target, format, and whether the write is volatile
   or non-volatile.
4. Recovery and rollback method, including behavior on power loss.
5. A separately reviewed experiment and explicit owner authorization.
