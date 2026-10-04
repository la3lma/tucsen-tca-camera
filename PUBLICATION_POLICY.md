# Public publication boundary

This repository and everything deployed from `site/` are public. The private
investigation tree may retain raw reverse-engineering material, but that
material must never be copied, committed, attached to a release, or deployed
from this repository.

## Permanent rule for future maintainers and coding agents

Publish independently written source, tests, procedures, hashes, measurements,
screenshots produced by the owner, and prose conclusions derived from analysis.
Do **not** publish any of the following:

- disassembly listings, decompiler exports, Ghidra projects/databases, symbol
  or strings dumps, or bulk function listings;
- vendor executables, DLLs, drivers, catalogs, installers, archives, SDK
  binaries, firmware payloads, or extracted package trees;
- raw packet captures, USB trace bundles, virtual-machine disks, private work
  directories, or unreviewed binary dumps;
- private credentials, machine-specific secrets, or a filesystem link that
  could make any private artifact part of a Pages or release bundle.

The public evidence pages may state hashes, file metadata, observed behavior,
and independently written findings such as the targeted Ghidra analysis. They
must not embed or link the underlying proprietary/raw artifact. When in doubt,
leave the artifact private and publish a reproducible description of how it
was examined.

## Enforcement

`tests/test_publication_policy.py` rejects forbidden current paths and, in a
full Git checkout, audits every filename retained in public history. CI checks
out full history and runs this test through `make test`. `.gitignore` provides
a second barrier against common raw-artifact names; it is not a substitute for
the test or review.

Before every public push, tag, GitHub release, or Pages deployment:

1. Run `make test` in this public repository.
2. Review `git status --short` and `git diff --cached --name-status`.
3. Confirm the proposed release/site file list contains only reviewed public
   material.
4. Keep private paths in the private report workspace; copy only deliberately
   selected public summaries and owner-generated media.

Never weaken the denylist merely to make a build pass. If a legitimate public
file conflicts with it, document the exception narrowly in the test and review
the file contents first. If a prohibited artifact is ever committed, stop
publishing immediately, remove it from all refs/history and release assets,
invalidate affected deployments, and treat the event as a disclosure rather
than assuming a later deletion made it private again.
