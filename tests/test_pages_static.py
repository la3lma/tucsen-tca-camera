#!/usr/bin/env python3
"""Static checks for the mutually linked GitHub Pages project documents."""

from __future__ import annotations

import pathlib
import sys


PAGES_ROOT = "https://la3lma.github.io/tucsen-tca-camera"
DOCSTACK_URL = f"{PAGES_ROOT}/docstack/"
REPORT_URL = f"{PAGES_ROOT}/report/microscope-window-sensor.pdf"
REPOSITORY_URL = "https://github.com/la3lma/tucsen-tca-camera"


def require(text: str, tokens: tuple[str, ...], label: str) -> None:
    for token in tokens:
        assert token in text, f"{label} missing {token}"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} PROJECT_ROOT")
    root = pathlib.Path(sys.argv[1]).resolve()
    readme = (root / "README.md").read_text(encoding="utf-8")
    landing = (root / "site/index.html").read_text(encoding="utf-8")
    docstack = (root / "site/docstack/index.html").read_text(encoding="utf-8")
    workflow = (root / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    report = root / "site/report/microscope-window-sensor.pdf"

    require(readme, (DOCSTACK_URL, REPORT_URL), "README")
    require(landing, ("docstack/", "report/microscope-window-sensor.pdf", REPOSITORY_URL), "landing")
    require(docstack, (DOCSTACK_URL, REPORT_URL, REPOSITORY_URL), "Docstack")
    require(workflow, ("actions/configure-pages@v5", "actions/upload-pages-artifact@v3", "actions/deploy-pages@v4", "path: ./site"), "Pages workflow")
    assert report.is_file(), report
    assert report.stat().st_size > 100_000, "published report is unexpectedly small"
    assert (root / "site/docstack/styles.css").is_file()
    assert (root / "site/docstack/app.js").is_file()
    assert (root / "site/.nojekyll").is_file()
    print("GitHub Pages static-site checks: PASS")


if __name__ == "__main__":
    main()
