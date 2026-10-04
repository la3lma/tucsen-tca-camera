# Modeled TCA trace plan and comparator

Evidence date: 2026-09-29

## Purpose and boundary

The VirtualHere trace gate needs a repeatable comparison against the protocol
already represented in the portable C core. Two offline tools now provide that
comparison without opening USB or generating an executable request path:

- `tools/tca_expected_trace.c` composes the existing open, 80-read startup
  signature, and selected fixed-mode plans into a machine-readable TSV. It may
  optionally append the modeled close request.
- `tools/compare_tca_trace.py` aligns that TSV with the output of
  `annotate_tca_trace.py`, reports matching, missing, unexpected, and mismatched
  wire tuples, and independently checks expected response patterns and the
  annotator's transport validation.

The generated file is a model-derived expectation, not proof that TSView emits
no additional request. Sequence differences remain evidence for review and do
not authorize replay. The generator links only the transport-neutral protocol
and startup modules; it has no libusb or platform-device import. The comparator
accepts TSV files only.

## Mode-4 expectation

The Ready-state mode-4 model contains 120 controls:

1. one `0xc0/0x02` open request;
2. 80 exact `0xc0/0x11` startup-signature reads, including expected big-endian
   values and acknowledgement `0x08`; and
3. 39 non-delay controls from the fixed mode-4 plan.

Adding `--include-close` appends the modeled `0xc0/0x03` close request for 121
controls total. Mode-plan sleeps are deliberately not represented as USB
transactions. Exact write acknowledgements are `08`; mode calibration-read
values use the constrained wildcard `????08` because only their acknowledgement
is currently modeled.

Generated reference:

- `work/trace-captures/expected-mode4-ready.tsv`
- SHA-256 `6299a0ed41b8e6ef261a57a4c215221b50290427051767986465063ba7895b8b`

## Tests and preserved negative trace

`tests/test_compare_tca_trace.py` verifies all 120 mode-4 Ready controls, exact
open and optional close shapes, first and last startup signature responses,
first decoded mode write, wildcard calibration-read acknowledgement, invalid
mode refusal, sequence insertion alignment, response mismatch detection, and
an exact-match case.

The strict C build, Python test, and preserved-capture comparison pass on Apple
Silicon macOS and AArch64 Ubuntu. The macOS ARM64 AddressSanitizer and
UndefinedBehaviorSanitizer build also passes. Both platforms generate identical
reference and comparison artifacts.

Applied to the USB/IP negative trace, the comparison reports zero actual vendor
controls and all 120 modeled controls missing. This is the expected result
because that transport failed during a standard descriptor request before
configuration; it confirms that the comparator does not fabricate a partial
TCA match.

Artifacts:

- `work/trace-captures/usbip-session-local-vm-20260929T1507Z/mode4-alignment.tsv`
- `work/trace-captures/usbip-session-local-vm-20260929T1507Z/mode4-alignment-summary.json`
- alignment TSV SHA-256 `58211414543b380c7e6a3339a2548dbdc119f137e29ef5d17f7a546e4ceeb135`
- summary SHA-256 `4b7fcedbe657ab8145490f097da2fd20ab6c13b32f4f3619b68287dbffbab9a2`

## Intended successful-trace command

After extraction and annotation:

```sh
make expected-trace MODE=4 > expected-mode4-ready.tsv
python3 tools/compare_tca_trace.py \
  expected-mode4-ready.tsv annotated-urbs.tsv \
  --output mode4-alignment.tsv \
  --summary-json mode4-alignment-summary.json
```

The first divergence is a review point. It must be reconciled against the
captured Windows behavior before any cold-start backend is implemented or run.
