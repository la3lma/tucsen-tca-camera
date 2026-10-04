# Open-source prior art and its boundary

Original search date: 2026-09-27

Updated after live protocol capture: 2026-10-03

Historical repository: <https://github.com/JohnDMcMaster/uvscopetek>

Inspected commit: `db9681b64353c899fff74be28105e6ea19373b53`

## What the repository establishes

The historical `devices.txt` inventory explicitly records:

```text
TS IS1000, 10.0 MP              0547:C003   Tucsen   tucsen.inf, JM has one
```

This independently corroborates the Tucsen/IS1000 identity and shows that an
open-source camera-recovery project knew of a physical C003 unit.

## What it does not establish

The implemented `scopetek` driver and replay code target ScopeTek/AmScope
`0547:4d88`, not Tucsen `0547:c003`. Its control protocol is structurally
similar but numerically different.  A successful reference trace has now
removed the earlier uncertainty about which C003 software lineage controls the
physical unit:

- request `0x01` for open/state transitions at index `0x000f`;
- request `0x0b` for one-byte acknowledgements; and
- request `0x0a` for three-byte register reads.

The physical C003 session uses the `b3`, `b4`, `b5`, `b7`, and `bb` request
families recovered from the 2011 Windows stack.  In particular, trace-confirmed
`b7` writes program exposure register `0x3012` and gain register `0x305e`.
The older TCA/TSView7 static package remains useful comparative evidence, but
neither its `0x02`/`0x03`/`0x10`/`0x11` plans nor the 4D88 replay are the
validated physical protocol and must not be sent to this unit.

## Engineering use

Use this repository only as comparative evidence for the broader Anchor-Chips
camera architecture: vendor control setup, sensor-register access, bulk-IN
frame transport, and explicit frame geometry. It is useful when designing the
reader and capture tooling, but it is not a protocol oracle for C003.

The local checkout is preserved at `work/reference-source/uvscopetek`; the two
key files are hashed in `evidence/hashes.sha256`.
