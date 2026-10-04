# Deterministic usbmon trace extractor and TCA annotator

Evidence date: 2026-09-29

## Purpose

`tools/extract_tca_usbmon.py` turns a Linux usbmon pcap/pcapng capture into one
deterministic TSV row per correlated submit/completion URB. It is the prepared
analysis half of the VirtualHere Windows-positive-control experiment: once the
armed capture records the known-good TSView7 session, the same command will
separate enumeration, vendor control requests, and bulk traffic without manual
packet transcription.

For every pair the output records submit/completion frames, elapsed
milliseconds, URB id, bus/device, transfer type, endpoint and direction,
statuses, setup request fields, requested/actual lengths, and the first
available decoded or captured payload. Unmatched submissions and orphan
completions are counted explicitly. A sorted compact JSON summary reports
standard versus vendor controls, bulk-IN versus bulk-OUT, errors, and pairing
gaps.

The implementation invokes the installed `tshark` field interface and never
modifies a capture. Optional bus/device filters keep unrelated USB traffic out
of the protocol table.

`tools/annotate_tca_trace.py` is the second, fully offline stage. It accepts
only the extractor's paired TSV and adds four columns: TCA event kind, decoded
register, decoded value, and validation result. It recognizes the recovered
TCA open/close, device-state, sensor-write, acknowledged-write, sensor-read,
and endpoint-`0x82` bulk-frame shapes. Sensor writes reverse the `0x17a0` XOR
encoding; sensor reads decode the first two response bytes as big-endian and
require acknowledgement `0x08`. Unknown vendor requests are retained as
`unknown-vendor-control`; the tool never treats an unknown row as safe and
cannot emit or execute USB operations.

## Tests

`tests/test_extract_tca_usbmon.py` includes a synthetic vendor register-read
pair with a three-byte `12 34 08` response, a bulk-IN completion with payload,
and an unmatched bulk-OUT submission. It checks exact setup formatting, timing,
payload normalization, direction, pairing, and all summary counters.

`tests/test_annotate_tca_trace.py` checks exact open recognition, read-value
decoding, write XOR reversal, acknowledgement failure, endpoint-`0x82` bulk
classification, unknown-request retention, deterministic TSV round-trip, and
strict input-header rejection.

The annotator test and the preserved-capture integration run pass independently
on Apple Silicon macOS and the AArch64 Ubuntu bench. Both platforms produce
byte-identical annotated TSV and JSON hashes: `52900b7152ec93b050be2eb0c7b6c3572e1689a143d4458202a0f3aa6b0e4a1c`
and `fe49582152a4239f6ea13b5ea8304c426ebf7bd976b28a9fe70105f4eef9a697`,
respectively.

The integration test processes the preserved USB/IP failure capture at bus 3,
device 2. It reconstructs ten standard-control pairs, no vendor control, no
bulk transfer, no pairing gaps, and one completion error. The final row is the
already documented descriptor failure with a 5,004.272 ms duration and status
`-104`. Generated artifacts:

- `work/trace-captures/usbip-session-local-vm-20260929T1507Z/paired-urbs.tsv`
- `work/trace-captures/usbip-session-local-vm-20260929T1507Z/paired-summary.json`
- `work/trace-captures/usbip-session-local-vm-20260929T1507Z/annotated-urbs.tsv`
- `work/trace-captures/usbip-session-local-vm-20260929T1507Z/annotated-summary.json`

This independently reproduces the earlier manual finding that USB/IP failed
before `SET_CONFIGURATION` or any vendor request. Tests pass with Python 3 and
tshark on macOS and the Ubuntu ARM64 VM.

## Intended VirtualHere use

After the Windows reference program reaches `Ready`, stop the existing
`dumpcap` process cleanly, copy the immutable pcapng into a new timestamped
project evidence directory, hash it, identify the camera's observed bus/device,
and run:

```sh
python3 tools/extract_tca_usbmon.py CAPTURE.pcapng \
  --bus BUS --device DEVICE > paired-urbs.tsv 2> paired-summary.json
python3 tools/annotate_tca_trace.py paired-urbs.tsv \
  --output annotated-urbs.tsv --summary-json annotated-summary.json
```

The annotated sequence is the first comparison surface for the portable
open/signature/mode/control plans; bulk-IN requested and actual lengths are
then compared to the fixed frame scheduler. Unknown requests remain evidence
for review; neither stage labels them safe or generates executable code.
