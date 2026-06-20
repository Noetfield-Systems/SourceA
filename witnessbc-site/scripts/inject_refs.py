#!/usr/bin/env python3
"""Inject footer references from data/references.json into partials/refs-list.html."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "references.json"
REFS_PARTIAL = ROOT / "partials" / "refs-list.html"
PAGES_DATA = ROOT / "data" / "pages.json"

FORBIDDEN = re.compile(
    r"sourcea|noetfield|[agent-aispm-vendor]|[agent-aispm-vendor]|notenic|witnessai|witness\.ai|witness bc",
    re.I,
)

START = "<!-- REFS_START -->"
END = "<!-- REFS_END -->"
CITE_RE = re.compile(r'href="(?:[^"]*#)?ref-(\d+)"')


def _ref_li(ref: dict) -> str:
    rid = ref["id"]
    url = ref["url"]
    return f"""          <li id="ref-{rid}">
            {ref["cite_html"]}
            <a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>
            <span class="ref-type">{ref["type"]}</span>
          </li>"""


def render_ref_list(data: dict) -> str:
    lines = [_ref_li(r) for r in data["refs"]]
    return "        <ol class=\"ref-list ref-list-page\">\n" + "\n".join(lines) + "\n        </ol>"


def _assembled_pages() -> list[Path]:
    pages = json.loads(PAGES_DATA.read_text(encoding="utf-8"))["pages"]
    return [ROOT / p["file"] for p in pages]


def validate_refs(html_pages: list[str], data: dict) -> None:
    combined = "\n".join(html_pages)
    ref_ids = {r["id"] for r in data["refs"]}
    cited = {int(m) for m in CITE_RE.findall(combined)}
    missing = cited - ref_ids
    if missing:
        raise SystemExit(f"FAIL inject_refs: HTML cites missing ref ids: {sorted(missing)}")

    for ref in data["refs"]:
        if not ref.get("url"):
            raise SystemExit(f"FAIL inject_refs: ref {ref['id']} missing url")
        if FORBIDDEN.search(ref["cite_html"] + ref["url"]):
            raise SystemExit(f"FAIL inject_refs: forbidden brand in ref {ref['id']}")

    gartner = data.get("gartner_primary_url", "")
    if gartner and gartner not in combined:
        raise SystemExit("FAIL inject_refs: Gartner primary URL not found in site content")

    partial = REFS_PARTIAL.read_text(encoding="utf-8")
    for ref in data["refs"]:
        rid = ref["id"]
        if f'id="ref-{rid}"' not in partial:
            raise SystemExit(f"FAIL inject_refs: missing ref-{rid} in refs-list partial")


def inject() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    partial = REFS_PARTIAL.read_text(encoding="utf-8")

    if START not in partial or END not in partial:
        raise SystemExit(f"FAIL inject_refs: markers {START} / {END} missing in partials/refs-list.html")

    ref_block = render_ref_list(data)
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    new_partial = pattern.sub(f"{START}\n{ref_block}\n        {END}", partial, count=1)
    REFS_PARTIAL.write_text(new_partial, encoding="utf-8")

    # Validate citations across content files (assembled pages may be stale)
    html_pages: list[str] = []
    content_dir = ROOT / "content"
    if content_dir.is_dir():
        for content in sorted(content_dir.glob("*.html")):
            html_pages.append(content.read_text(encoding="utf-8"))
    else:
        for page_path in _assembled_pages():
            if page_path.is_file():
                html_pages.append(page_path.read_text(encoding="utf-8"))

    validate_refs(html_pages, data)
    return {"ok": True, "ref_count": len(data["refs"]), "target": str(REFS_PARTIAL)}


def main() -> int:
    result = inject()
    quiet = "--quiet" in sys.argv or "-q" in sys.argv
    if not quiet:
        if "--json" in sys.argv:
            print(json.dumps(result, indent=2))
        else:
            print(f"OK: injected {result['ref_count']} references into {result['target']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
