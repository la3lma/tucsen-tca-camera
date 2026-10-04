# Device identity: legacy AmScope 10 MP microscope camera

Observed on 2026-09-26. This sheet separates direct observations from model
identification and implementation inferences.

## Physical evidence

- Black, finned metal camera body with an `AmScope` logo.
- USB Type-B receptacle.
- No model, serial-number, or regulatory label is visible in the supplied
  views. Gaffer tape covers the exposed sensor/mount area for protection.
- Original photographs are retained in `evidence/photos/` and hashed in
  `evidence/hashes.sha256`.

## USB enumeration on macOS

Host: macOS 26.5.2 (build 25F84).

| Field | Observed value |
|---|---|
| Product string | `10MP CMOS Camera` |
| Manufacturer string | `123456789` |
| Serial-number string | absent (`iSerialNumber = 0`) |
| Vendor ID | `0x0547` (1351) |
| Product ID | `0xC003` (49155) |
| Device release | `0x0000` |
| USB version | 2.0 (`bcdUSB = 0x0200`) |
| Link speed | high speed, 480 Mbit/s |
| Device class | per-interface (`bDeviceClass = 0`) |
| Configurations | 1 |

The active configuration has one interface and one non-control endpoint:

| Field | Observed value |
|---|---|
| Configuration value | 1 |
| Total descriptor length | 25 bytes |
| Attributes | `0x80` (bus powered) |
| Maximum power | descriptor value 50 (100 mA in USB 2.0 units) |
| Interface | 0, alternate setting 0 |
| Interface class | `0xFF` (vendor-specific) |
| Subclass / protocol | `0x00` / `0x00` |
| Endpoint | `0x82` (endpoint 2, device-to-host) |
| Transfer type | bulk (`bmAttributes = 0x02`) |
| Maximum packet size | 512 bytes |
| Interval | 0 |

Bus and device addresses are deliberately omitted as identity fields because
they may change after reconnection. The descriptor snapshot was read with
libusb 1.0.29; only standard descriptors were requested.

## Identification

Tucsen's official discontinued-camera table says that model identity can be
confirmed using VID/PID. It maps `0547:C003` to both `TCA-10.0N` and `IS1000`:

- https://www.tucsen.com/uploads/The-Discontinued-CMOS-Camera-Download-Links.pdf

The official `TCA-10.0-N` driver INF binds `USB\VID_0547&PID_C003` and labels
it `Tucsen TCA-10.0-N Camera`. The official beta driver binds the same ID and
labels it `IS1000 USB Camera`. The physical AmScope unit is therefore identified
with high confidence as an AmScope-branded Tucsen TCA-10.0N / IS1000 hardware
family device. The USB descriptors alone do not distinguish which Tucsen sales
name AmScope used.

## Static inspection of official Windows packages

The original purchase CD, installer, and manual have been lost and are not
available for comparison. The packages below are replacement reference copies
recovered from Tucsen's official support site.

The official download table links these packages. They were downloaded into
the project-local `work/vendor-zips/` directory but not executed:

- `TCA-10.0-N-Driver-Setup.zip`
- `Beta-Camera-Driver.zip`
- `ISCapture-3.6.8-En-Setup.zip`

The packages contain 32-bit Inno Setup installers. Static extraction found:

- A 2011 TCA INF and a 2013 beta INF, both binding `0547:C003` to a KMDF
  `Tucsen64.sys` kernel driver.
- A registry setting named `MaximumTransferSize` with value 65,536 bytes.
- Driver strings referring to bulk and isochronous read/write source modules;
  the live device descriptor, however, exposes only bulk endpoint `0x82`.
- ISCapture contains a dedicated 32-bit `TS1000.dll`. Its exports cover camera
  initialization, preview, still capture, frame grabbing and decoding,
  exposure, gain, white balance, colour adjustment, flat-fielding and
  dead-pixel correction.
- `TS1000.dll` imports Windows file/device APIs including `CreateFileA`,
  `ReadFile`, `WriteFile`, and `DeviceIoControl`, indicating that much of the
  model-specific protocol and decoding likely lives in this user-mode DLL over
  a relatively thin Windows USB driver.

## Conclusions supported by current evidence

1. The device is **not USB Video Class (UVC)**. Its only interface is
   vendor-specific, so normal macOS AVFoundation and Linux UVC drivers will not
   claim it.
2. Host-to-device configuration must use endpoint-zero control transfers,
   because the only additional endpoint is bulk IN. Image data is expected on
   endpoint `0x82`; this remains an inference until a capture is observed.
3. A portable user-space implementation using libusb is plausible. The next
   unknowns are the initialization/control requests, frame boundaries, pixel
   format, and any calibration data.
4. The safest high-value next experiment is an isolated Windows run of the
   official driver and ISCapture while recording USB traffic. Static analysis
   of `TS1000.dll` can proceed in parallel and may reduce the required capture
   experiments.
5. Tucsen currently advertises a Linux SDK, but no evidence yet shows that it
   supports this discontinued `0547:C003` family. That avenue should be tested,
   not assumed.

## Safety status

No vendor-specific request, firmware upload, capture command, or persistent
device write has been attempted. Work so far consists of standard USB
descriptor reads and offline inspection of official vendor packages.
