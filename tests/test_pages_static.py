#!/usr/bin/env python3
"""Static checks for the mutually linked GitHub Pages project documents."""

from __future__ import annotations

import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit


PAGES_ROOT = "https://la3lma.github.io/tucsen-tca-camera"
DOCSTACK_URL = f"{PAGES_ROOT}/docstack/"
REPORT_URL = f"{PAGES_ROOT}/report/microscope-window-sensor.pdf"
REPOSITORY_URL = "https://github.com/la3lma/tucsen-tca-camera"


def require(text: str, tokens: tuple[str, ...], label: str) -> None:
    for token in tokens:
        assert token in text, f"{label} missing {token}"


class LocalReferences(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        attribute = "href" if tag == "a" else "src" if tag in {"img", "script"} else None
        if attribute and values.get(attribute):
            self.references.append(values[attribute] or "")


def resolve_local(site: pathlib.Path, page: pathlib.Path, reference: str) -> pathlib.Path | None:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("mailto:"):
        return None
    path = unquote(parsed.path)
    if path.startswith("/tucsen-tca-camera/"):
        candidate = site / path.removeprefix("/tucsen-tca-camera/")
    elif path.startswith("/"):
        return None
    else:
        candidate = page.parent / path
    if path.endswith("/"):
        candidate /= "index.html"
    return candidate.resolve()


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
    evidence = root / "site/evidence"
    markdown_records = sorted(evidence.glob("*.md"))
    assert markdown_records, "no public evidence records"
    for source in markdown_records:
        rendered = source.with_suffix(".html")
        assert rendered.is_file(), f"missing rendered evidence page for {source.name}"
        text = rendered.read_text(encoding="utf-8")
        require(text, ("Evidence index", "Docstack ledger", "evidence.css"), rendered.name)
    assert (evidence / "index.html").is_file()
    assert (evidence / "photos/index.html").is_file()
    evidence_links = re.findall(r'href="(\.\./evidence/[^"]+)"', docstack)
    assert evidence_links, "Docstack contains no evidence links"
    assert all(urlsplit(link).path.endswith(".html") for link in evidence_links), (
        "Docstack evidence links must target rendered HTML",
        evidence_links,
    )

    site = root / "site"
    for page in site.rglob("*.html"):
        parser = LocalReferences()
        parser.feed(page.read_text(encoding="utf-8"))
        for reference in parser.references:
            target = resolve_local(site, page, reference)
            if target is not None:
                assert target.is_file(), f"{page.relative_to(site)} -> {reference} is missing"
    print("GitHub Pages static-site checks: PASS")


if __name__ == "__main__":
    main()
