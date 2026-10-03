# Contributing

Bug reports, hardware observations, portability fixes, and narrowly supported
protocol extensions are welcome.

Before proposing a live USB command, provide one of:

1. a trace from a working reference stack;
2. repeatable behavior from an already supported command family; or
3. independent static evidence plus a bounded, reversible test plan.

New live commands must have fixed request shapes and checked value ranges. Do
not add arbitrary register-write or firmware-upload interfaces. Preserve the
first untouched device frame when changing transport or marker handling.

Run `make test` on every supported platform. A hardware result should include
device descriptors, platform versions, stderr logs, exact byte counts, and
hashes, without proprietary binaries or private image content.
