# Public package install and removal operations

Date: 2026-10-03

Scope: public repository commit
`fb502c1d58252c7168f68b873ff1ab51aa431ca8`.

Commit `fb502c1` closes the remaining software-only D110 operations gap. The
public Makefile now installs exactly these executable files below the selected
`PREFIX` and optional `DESTDIR`:

- `tca-camera`;
- `tca-v4l2`; and
- `tca-frame-stats`.

Its `uninstall` target removes exactly those three paths. It does not remove
the containing `bin` directory, an optional udev rule, a distribution-managed
`v4l2loopback` package, or unrelated files.

`tests/test_install.py` stages installation under a new temporary `DESTDIR`,
requires all three regular files to be owner-executable, creates an unrelated
sentinel in the same `bin` directory, runs `make uninstall`, and requires the
three project files to be absent while the sentinel remains unchanged.

The complete test suite, including that install/removal test, passed on Apple
Silicon and on a clean detached Raspberry Pi worktree at exact commit
`fb502c1`. GitHub Actions run
<https://github.com/la3lma/tucsen-tca-camera/actions/runs/37151022334>
also completed successfully on Ubuntu and macOS.

This validates staged package operations without mutating the Pi's live system
installation. It does not replace the still-open physical camera-cable or
microscope optical checks.
