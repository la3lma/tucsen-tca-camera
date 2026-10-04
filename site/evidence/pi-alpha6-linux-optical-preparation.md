# Raspberry Pi alpha-6 optical acceptance preparation

Date: 2026-10-04

The camera remained connected to the Apple Silicon workstation while the
Linux bench was prepared. No camera transfer was sent during this preparation.

## Exact release bench

The reachable AArch64 host is `rpios-17`. A clean shallow checkout at
`/home/rmz/tucsen-tca-camera-alpha6` is pinned to public tag
`v0.2.0-alpha.6`, commit
`0fded6e214e51c7b082b0471b4d55f5a3fe16132`. Native
`make clean all test` passed all static/inert, V4L2, frame-statistics,
white-balance, and staged install/uninstall checks. The worktree is clean and
the built reader reports `tca-camera 0.2.0-alpha.6`.

The host has libusb 1.0.28, FFmpeg 7.1.3, v4l2-ctl 1.30.1, and
`v4l2loopback-dkms` 0.15.3. A bounded setup check loaded a loopback device as
`/dev/video42`, verified its `TCA 10MP Microscope` identity and streaming
capabilities, and unloaded it again. The final prepared state has no camera,
no `/dev/video42`, and no loaded `v4l2loopback` module, which is the state the
release helper requires before taking temporary ownership.

An end-to-end camera-independent preflight then removed the remaining generic
V4L2 uncertainty. FFmpeg wrote a 1280x960 YUYV test source into a fresh
exclusive-capabilities `/dev/video42`; a separate FFmpeg process opened the
node as an ordinary capture client and consumed six exact 2,457,600-byte
frames. The resulting 14,745,600-byte stream rendered back to the expected
test image, both FFmpeg logs were empty, and teardown removed the node and
module. A copied, locally revalidated manifest is retained under
`work/pi-alpha6-preparation/v4l2-preflight-QxdWZXu7/`. The post-switch run
therefore tests the camera reader and its bridge composition, not previously
untested loopback plumbing.

## One-shot post-switch harness

`tools/run_alpha6_linux_optical_acceptance.sh` is copied to
`/home/rmz/tca-acceptance-tools/` on the Pi. With no arguments it is inert,
prints `NO USB TRANSFER SENT`, and exits zero. Its static/inert test passes.
The explicit execution path requires exactly one `0547:c003`, the exact public
commit, a pre-primed sudo credential, and an already-existing evidence parent.
It then:

1. records USB and release inventory;
2. captures three 1280x960 frames at 250 ms/gain 0 and checks exact sizes;
3. captures one fully assembled 3664x2748 frame and checks exact sizes;
4. records statistics and a neutral-region white-balance estimate;
5. starts the release V4L2 bridge at `/dev/video42`;
6. has FFmpeg consume six YUYV frames through the ordinary application API;
7. renders the first consumed frame to PNG;
8. stops the bridge and verifies that its device and module were removed; and
9. creates a SHA-256 manifest for the complete run directory.

No password or secret is embedded in the harness or evidence. The exact
execution remains pending the owner's physical camera move from the Mac to the
Pi.

## Pinned hashes

```text
279c40ea1c80a33259cb21f14a00de787b45fda7a663b2bf688dc1af577a025d  Pi build/tca-camera
6c6bd49fb3958805fab5c16f911a1d8b8029fe65dc4b98964ddfcab6aeb10224  release scripts/tca-v4l2
65f9f7e73a22128549755871e9d445ff308d7409b3f3cd59bea7387ee2367f9a  release scripts/tca-frame-stats
02735eb1a74c1d2a84620b644389c6438507b864e19e80fffe3b0078fb0096cc  release scripts/tca-white-balance
25e55de29d1967cdbb5e3c1d2e9867e537fe4cef12f4a3bc310bffdd69e684a7  tools/run_alpha6_linux_optical_acceptance.sh
fd7444dd103e2dafca5c1ee604280941db1a83401c0093d6681050713b4b0c6c  tests/test_alpha6_linux_optical_acceptance_static.py
1125dbe7fb837b9ce2767684daa2b965f14f69ea3e2b073819c7970bc881ec03  V4L2 preflight first-frame.png
d4bd831e964fafb33d3d8b9c28e091ca4ac3fd9784077a0402efc4741c363472  V4L2 preflight six-frames.yuyv
cacd696836e2290aba074d68e21b3cb40ac6b7e9b2a3018bf57916994b6353cc  V4L2 preflight manifest-local.sha256
```
