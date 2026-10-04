# Linux USB/IP plus usbmon trace bench

Prepared 2026-09-29. This bench is the next D40 evidence path after the
all-root USBPcap run proved blind to UTM's CocoaSPICE usbredir channel.

## Purpose

Route the workstation-attached physical `0547:c003` camera through the
project-local ARM64 Linux VM to the already working Windows 10 x64
Tucsen/TSView7 stack while Linux records the host-controller URBs with
`usbmon`. This observes a successful initialization without guessing another
vendor request. The Raspberry Pi procedure remains a later independent
deployment check, not a prerequisite for this trace.

## Pinned Windows client

The project contains the x64 installer for usbip-win2 0.9.8.0:

```text
81f426741f7ee2ed991febe24a22daca8400b6ae2f171054e3fb404897e15d39  work/windows-trace-bench/guest-tools/USBip-0.9.8.0-x64.exe
909717d8e29b45c6a616bb4095f13e0cacd34a994999fff87a2de3523513f0dd  work/windows-trace-bench/tca-usbip-tools.iso
```

Version 0.9.8.0 was selected instead of the two-day-old 0.9.8.1 release. The
upstream maintainer describes 0.9.8.0 as highly recommended; the 0.9.8.1 notes
explicitly warn that its large AI-assisted rewrite may contain regressions.
The selected release supports a Linux USB/IP 1.1.1 server and Windows 10 x64.
It remains third-party kernel software, so it belongs only in the disposable
camera VM.

Primary references:

- <https://github.com/vadimgrn/usbip-win2>
- <https://github.com/vadimgrn/usbip-win2/releases/tag/v.0.9.8.0>
- <https://docs.kernel.org/usb/usbmon.html>

### Windows client installation proof

Installed and verified in the disposable `Microscope TCA Trace` Windows 10 x64
guest on 2026-09-29. Setup used the pinned project-local installer, retained its
default full-install components and Microsoft Visual C++ runtime prerequisite,
and completed the requested restart. Post-restart checks established:

```text
C:\Program Files\USBip>usbip.exe --version
0.9.8.0

SERVICE_NAME: usbip2_ude
        TYPE               : 1  KERNEL_DRIVER
        STATE              : 4  RUNNING
                                (STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
        WIN32_EXIT_CODE    : 0  (0x0)
        SERVICE_EXIT_CODE  : 0  (0x0)
```

The installed directory contains `usbip.exe`, `wusbip.exe`, `libusbip.dll`,
`devnode.exe`, headers, libraries, and matching symbols. The installer does not
put `usbip.exe` on the global `PATH`; project scripts therefore intentionally
use `C:\Program Files\USBip\usbip.exe` by absolute path.

## Primary Linux VM side

The project-local `Microscope Linux Bench` guest is Ubuntu 24.04 ARM64 at
`192.168.65.5`. UTM passes the physical camera to it directly. Windows uses an
E1000 shared-network adapter at `192.168.65.6`, so it can reach Linux TCP 3240
without a macOS relay. See [the VM evidence](linux-vm-bench.md).

The capture helper retains its historical Pi-oriented filename but is
host-neutral. In the Linux VM, inspect the single matching device:

```sh
sudo tools/pi_usbip_capture.sh status
```

Start a new immutable session only after the camera has been physically
power-cycled or after explicitly recording that the run is a warm-state trace:

```sh
sudo tools/pi_usbip_capture.sh start --record-known-good-init
```

The script refuses zero or multiple matching devices, starts `usbmon` before
binding, exports only the exact sysfs bus ID, and prints the Linux host IP, bus
ID, and session directory. It does not issue camera controls.

## Windows side

USBip 0.9.8.0 is installed and its `usbip2_ude` kernel driver is running. In an
elevated command prompt, first list without attaching:

```bat
usbip-attach-camera.cmd 192.168.65.5 3-3
```

Use server `192.168.65.5`. After checking that bus ID `3-3` is `0547:c003`,
attach with the explicit
token:

```bat
usbip-attach-camera.cmd 192.168.65.5 3-3 --attach-known-good-camera
```

Verify Device Manager reports the remote camera with the already installed
Tucsen driver. Start TSView7 once, wait for `Ready`, and do not change controls
or invoke firmware actions.

## Stop and accept

Close TSView7, detach the USB/IP port in Windows, then stop the Linux capture:

```sh
sudo tools/pi_usbip_capture.sh stop work/usbip-session-TIMESTAMP
```

The stop action unbinds the physical device and writes a session manifest.
Accept the run only if the pcapng begins before Windows attaches, includes the
first successful vendor response and the first mode-4 bulk data, and the camera
still enumerates normally after unbind. Preserve the raw pcapng before any
filtering or tuple extraction.

## Raspberry Pi fallback and validation

The identical helper can run on `rpios-17` if UTM USB forwarding or its shared
network proves unreliable. The Pi also remains the independent hardware target
for the later install, reconnect, and endurance acceptance runs.

## Executed result: Windows enumeration failure

The prepared path was executed on 2026-09-29. Windows listed `0547:c003` and
reported a successful attach to virtual port 1, but the captured sequence
stopped before configuration or any vendor request. Valid device,
configuration, language, and product-string descriptors were followed by a
second device-descriptor request that timed out after 5.004272 seconds and was
reset as `-ECONNRESET`. TSView therefore never received a configured camera.

The stopped session is preserved under
`work/trace-captures/usbip-session-local-vm-20260929T1507Z`; its pcapng SHA-256
is `ff33d5e7ab7ffbd9dcf1b0771ad5baba288c364dfea7497aa6daccd8f57ca11c`.
This is accepted negative transport evidence. The next trace attempt uses the
[VirtualHere fallback](virtualhere-trace-bench.md), not another USB/IP retry.
