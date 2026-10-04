# D40 physical-cold probe result

Executed once on `rpios-17` on 2026-09-27 after the owner physically removed
camera USB power for more than ten seconds and reconnected it. The camera
enumerated as a new USB instance at bus 1 address 4 (previously address 3), so
this was not merely a reuse of the earlier Linux device session.

The reviewed version-2 prefix was then issued exactly once:

```text
c0 02 0000 000f length=0 timeout=1000ms
c0 11 0000 3ff0 length=3 timeout=1000ms expected-ack=08
c0 03 0000 000e length=0 timeout=1000ms
```

All three operations returned `LIBUSB_ERROR_TIMEOUT (-7)`. Continuing from the
open timeout to the single corrected register read was intentional: offline
execution of the matching TSView7 DLL shows that its wrapper ignores the open
result before issuing the read. The process exited with status 1.

The failure was safe and bounded. Before and after the prefix, the descriptor
fixture opened the device, read its descriptors, claimed interface 0, released
it, and closed it successfully. Identity remained `0547:c003`, configuration 1,
high speed, vendor interface 0, bulk-IN endpoint `0x82`, 512-byte maximum
packet. The before/after device records are byte-identical, USB inventory did
not change, and the kernel log acquired no USB fault.

The copied evidence bundle is:

```text
work/live-cold-probe-20260927T184037Z-24842/
```

Its own manifest verifies every captured file. Key SHA-256 values are:

```text
29b0df032a6ac3364ce32defe1b70a3dd8eddd90673d0a6c84bcc3323cce72fe  manifest.sha256
217d9eb11056e6c734dff09a2046a85ea0a492a0721985bb91dd7f4b664d884c  probe.stdout.txt
39655af0e69df9521a453d9c4294502a95d0e113fd75ab95ce3453ba1e281698  probe.stderr.txt
4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865  probe-exit-status.txt
1fbaeafad21f5078332dbfd6e01c19b929ea649bd8824cefc5b1a436c57a0c17  before-device.txt
1fbaeafad21f5078332dbfd6e01c19b929ea649bd8824cefc5b1a436c57a0c17  after-device.txt
```

This closes the final justified Linux request experiment at D40. It is valid
negative evidence for the corrected TCA prefix from a physical cold start, not
evidence that the camera is defective. No request-field variation or retry is
approved. The next discriminator is the already planned first-attach USB trace
from the recovered software in an isolated x86-64 Windows guest.
