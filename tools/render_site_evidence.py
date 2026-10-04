#!/usr/bin/env python3
"""Render every public evidence Markdown record as a linked HTML site."""

from __future__ import annotations

import argparse
import html
import pathlib
import re
import subprocess
import sys


def title_for(source: pathlib.Path) -> str:
    for line in source.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return source.stem.replace("-", " ").title()


def render_fragment(source: pathlib.Path) -> str:
    completed = subprocess.run(
        [
            "pandoc",
            "--from=markdown+raw_html+header_attributes+pipe_tables",
            "--to=html5",
            str(source),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    fragment = completed.stdout
    return re.sub(
        r'href="([^"#:?]+)\.md(#[^"]*)?"',
        lambda match: f'href="{match.group(1)}.html{match.group(2) or ""}"',
        fragment,
    )


def page(title: str, body: str, root_prefix: str = "../") -> str:
    escaped = html.escape(title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped} — Tucsen TCA evidence</title>
  <link rel="stylesheet" href="{root_prefix}evidence/evidence.css">
</head>
<body>
  <header class="site-header">
    <a href="{root_prefix}evidence/">Evidence index</a>
    <a href="{root_prefix}docstack/#evidence-ledger">Docstack ledger</a>
    <a href="{root_prefix}report/microscope-window-sensor.pdf">PDF report</a>
    <a href="https://github.com/la3lma/tucsen-tca-camera">Source repository</a>
  </header>
  <main class="evidence-record">
{body}
  </main>
  <footer>Public evidence record for the AmScope/Tucsen 0547:c003 reader.</footer>
</body>
</html>
"""


def render_index(sources: list[pathlib.Path], destination: pathlib.Path) -> None:
    items = "\n".join(
        f'      <li><a href="{html.escape(source.stem)}.html">'
        f"{html.escape(title_for(source))}</a></li>"
        for source in sources
    )
    body = f"""    <h1>Microscope camera evidence</h1>
    <p>This index exposes every public Markdown evidence record as a rendered
    HTML page. The Docstack ledger links to these pages rather than to raw
    Markdown or workstation-local paths.</p>
    <p><a href="photos/index.html">Owner photographs of the camera</a></p>
    <ol class="evidence-index">
{items}
    </ol>"""
    destination.write_text(page("Evidence index", body), encoding="utf-8")


def render_photos(evidence_dir: pathlib.Path) -> None:
    photos = evidence_dir / "photos"
    images = sorted(
        path for path in photos.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    figures = "\n".join(
        f'    <figure><a href="{html.escape(image.name)}"><img src="{html.escape(image.name)}" '
        f'alt="{html.escape(image.stem.replace("-", " "))}"></a>'
        f"<figcaption>{html.escape(image.stem.replace('-', ' '))}</figcaption></figure>"
        for image in images
    )
    body = f"""    <h1>Owner photographs</h1>
    <p>Exterior views of the unmarked AmScope microscope camera used by this
    investigation. Select an image to open the full-resolution original.</p>
    <div class="photo-grid">
{figures}
    </div>"""
    (photos / "index.html").write_text(
        page("Owner photographs", body, root_prefix="../../"), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "repository",
        nargs="?",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[1],
    )
    arguments = parser.parse_args()
    evidence_dir = arguments.repository.resolve() / "site" / "evidence"
    sources = sorted(evidence_dir.glob("*.md"))
    if not sources:
        print("render-site-evidence: no evidence Markdown found", file=sys.stderr)
        return 64
    try:
        for source in sources:
            body = render_fragment(source)
            source.with_suffix(".html").write_text(
                page(title_for(source), body), encoding="utf-8"
            )
        render_index(sources, evidence_dir / "index.html")
        render_photos(evidence_dir)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"render-site-evidence: {error}", file=sys.stderr)
        return 1
    print(f"Rendered {len(sources)} evidence records plus indexes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
