# Linux V4L2 replay bridge

Evidence date: 2026-09-29

## Scope

This is an application-boundary proof on the disposable Ubuntu ARM64 VM. It
uses the 640x480 Bayer8 frame previously captured live from the camera after
Windows initialization. It does not initialize or control the camera and does
not satisfy the live D70/D80 dependency.

Authoritative input:

```text
e21de091b464f3113f9ba9b66abf806a1f4af112a0d96afaa317a8b8040de769  work/live-host-capture-20260929T080041Z/mode4.raw
```

The sensor was covered, so a dark repeated frame is expected.

## Environment

- Ubuntu ARM64 kernel `6.8.0-142-generic`
- FFmpeg `6.1.1-3ubuntu5`
- `v4l-utils` `1.26.1-4build3`
- `v4l2loopback-dkms` `0.12.7-2ubuntu5.2`
- project C17 `tca_raw_convert`, built natively on the VM

Exact environment output is preserved in
`work/v4l2-bridge-environment-20260929.txt`.

## Pipeline

The native project converter transformed the live Bayer8 frame to a 921,600
byte RGB24 frame. FFmpeg repeated that frame at 5 fps, converted it to YUYV,
and wrote it to a temporary `v4l2loopback` node:

```sh
sudo modprobe v4l2loopback video_nr=42 \
  card_label="TCA Camera Replay" exclusive_caps=1 max_buffers=4

ffmpeg -re -stream_loop -1 -f rawvideo -pixel_format rgb24 \
  -video_size 640x480 -framerate 5 -i work/mode4-live.rgb \
  -vf format=yuyv422 -f v4l2 /dev/video42
```

The replay source is deliberately separable from USB acquisition. Once the
live reader emits exact Bayer8 frames, it can replace the file without changing
the V4L2-facing half of the pipeline.

## Consumer results

First run, `v4l2-ctl` consumer:

- device named `TCA Camera Replay`;
- capture format YUYV 4:2:2, 640x480, 1,280-byte line, 614,400-byte frame;
- three frames captured through streaming/mmap;
- output length 1,843,200 bytes, exactly three frames;
- output SHA-256
  `67bb7619499e46feb623f61e22e660da5c3912424187dffa4162957cbd9214cb`.

Evidence directory:
`work/v4l2-bridge-20260929T1705Z/`.

After stopping the writer, removing the module, and loading a fresh loopback
node, a second run used FFmpeg as the consumer. It accepted three 640x480 YUYV
frames. The `framemd5` file records the same 614,400-byte digest for each
repeated dark frame:

```text
5e0b144c315b994980ff81c06098308e
```

Evidence directory:
`work/v4l2-bridge-20260929T1710Z/`.

## Cleanup and remaining boundary

The writer processes were stopped and `v4l2loopback` was unloaded after each
run. The final environment record states `loopback_device_removed=yes`; no
`/dev/video42` remains. The physical camera still enumerates as `0547:c003`,
VirtualHere remains listening on TCP 7575, and the independent `usbmon3`
capture remains armed.

This verifies decode-to-V4L2 negotiation, two application consumers,
stop/remove/recreate/restart, and clean removal using a real camera payload.
It does not verify live acquisition, timestamps from the camera, slow-consumer
policy, controls, or disconnect recovery. D80 therefore remains proposed until
D70 supplies a stable live reader.

## Reproducible reader-core bridge

The manual proof has now been packaged as
`tools/tca_v4l2_replay.sh`. The foreground script:

1. refuses to alter an existing `v4l2loopback` setup or video node;
2. loads one temporary loopback device with exclusive capture capabilities;
3. grants the invoking user access only to that temporary node;
4. continuously replays the authoritative mode-4 raw frame through the new
   transport-neutral `camera-reader` session and FFmpeg YUYV conversion;
5. waits until the writer has opened and the device advertises capture before
   reporting readiness; and
6. stops the writer and unloads the module on normal exit or a trapped signal.

The packaged script was exercised natively on the Ubuntu ARM64 bench. A
`v4l2-ctl` consumer captured three frames totaling 1,843,200 bytes with the
same SHA-256 as the earlier manual bridge:

```text
67bb7619499e46feb623f61e22e660da5c3912424187dffa4162957cbd9214cb
```

The evidence is preserved in
`work/v4l2-reader-script-20260929T1740Z/`. After the scripted session,
`/dev/video42` was absent, the module was unloaded, no bridge process remained,
the camera still enumerated as `0547:c003`, and the independent VirtualHere/
usbmon bench remained armed.
