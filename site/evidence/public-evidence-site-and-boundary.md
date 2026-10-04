# Public evidence site and permanent publication boundary

Date: 2026-10-04

Public implementation commit:
[`064cf31`](https://github.com/la3lma/tucsen-tca-camera/commit/064cf317bce660a3044e76755b6c3bc93e874b0b)

## Purpose

Make the public evidence ledger completely browsable on GitHub Pages while
permanently preventing raw proprietary reverse-engineering material from
entering the public repository. The private report workspace may retain such
material where lawful and necessary; the public repository and its Pages
artifact may not.

## Rendered evidence

The public build now renders every Markdown evidence record as a sibling HTML
page, rewrites evidence-to-evidence links from `.md` to `.html`, and generates
both an evidence index and an owner-photograph index. The Docstack ledger links
to the rendered HTML records rather than to raw Markdown. A static test parses
every local `href` and `src` in the generated site and fails on a missing
target.

Deployment and CI for commit `064cf31` both passed. Live HTTP checks confirmed:

- `/evidence/` returns the rendered evidence index;
- `/evidence/live-control-trials.html` returns rendered HTML with evidence,
  Docstack, report, and source navigation;
- `/evidence/photos/` returns the owner-photograph index; and
- the Docstack evidence ledger targets rendered `.html` records.

The historical `.md` URLs remain available as source text. They are no longer
the primary ledger targets.

## Permanent public/private boundary

`PUBLICATION_POLICY.md` is the repository's standing instruction to humans and
future coding agents. Public material may include independently written source,
tests, procedures, hashes, measurements, owner-supplied photographs, and prose
conclusions. It must never include raw disassembly, decompiler exports, Ghidra
projects or databases, symbol or strings dumps, vendor executables, DLLs,
drivers, catalogs, installers, SDK binaries, firmware, packet captures, virtual
machine disks, secrets, symlinks to private material, or files copied from the
private `work/` and analysis areas.

`tests/test_publication_policy.py` enforces denied paths and suffixes in the
current tracked tree and the complete Git object history. CI now uses a
full-depth checkout so the history audit is meaningful. `.gitignore` also
blocks the private working directories and dangerous artifact suffixes.
The policy says explicitly that the denylist must not be weakened merely to
make a build pass and that an accidental public commit is a disclosure incident
requiring publication to stop while the history and any affected credentials
are remediated.

## Audit result

A fresh filename and object-history audit found no raw disassembly, Ghidra
project/export, vendor binary or driver, firmware image, packet capture, or
private-work filename in the public repository's current tree or history.
The public Ghidra evidence page is an independently written factual summary; it
does not contain or link the raw decompiler output. The private report workspace
continues to hold the underlying licensed analysis artifacts outside the public
repository.

## Future-self release checklist

Before every public push, tag, release, or Pages deployment:

1. Run the full public test suite from a full-history checkout.
2. Review the exact staged paths and every release or Pages file.
3. Confirm that only independently written facts, hashes, and conclusions cross
   the private/public boundary.
4. Never publish or link raw proprietary binaries, disassembly, decompiler
   exports, Ghidra state, packet captures, firmware, VM images, or private work.
5. Stop publication and remediate history immediately if the audit reports a
   forbidden artifact; do not relax the rule to obtain a passing build.
