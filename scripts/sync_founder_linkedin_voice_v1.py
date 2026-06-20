#!/usr/bin/env python3
"""Sync LinkedIn founder voice → dictionary · open-row spec · M1 Canvas terminology."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FL = ROOT / "archive/attachments/founder-language"
OPEN_ROW_SPEC = (
    Path.home()
    / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/integrity-open-row-spec.ts"
)
DICT = FL / "dictionary.yaml"


def _load_yaml(path: Path) -> dict:
    import yaml  # type: ignore

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _patch_open_row_spec(terms: list[dict[str, str]]) -> None:
    if not OPEN_ROW_SPEC.is_file():
        print(f"WARN: missing {OPEN_ROW_SPEC}", file=sys.stderr)
        return
    lines = ["export const FORM_TERMINOLOGY_REQUIRED: { term: string; sayInstead: string }[] = ["]
    for t in terms:
        term = t["term"].replace('"', '\\"')
        say = t["sayInstead"].replace('"', '\\"')
        lines.append(f'  {{ term: "{term}", sayInstead: "{say}" }},')
    lines.append("];")
    block = "\n".join(lines)
    text = OPEN_ROW_SPEC.read_text(encoding="utf-8")
    text = re.sub(
        r"export const FORM_TERMINOLOGY_REQUIRED: \{ term: string; sayInstead: string \}\[\] = \[.*?\];",
        block,
        text,
        count=1,
        flags=re.DOTALL,
    )
    OPEN_ROW_SPEC.write_text(text, encoding="utf-8")


def _merge_dictionary(linkedin: dict) -> int:
    if not DICT.is_file():
        return 0
    import yaml  # type: ignore

    data = _load_yaml(DICT)
    entries = list(data.get("entries") or [])
    existing = {e.get("founder") for e in entries}
    added = 0
    for p in linkedin.get("linkedin_phrases") or []:
        founder = p.get("founder")
        if not founder or founder in existing:
            continue
        entries.append(
            {
                "founder": founder,
                "plain": p.get("plain"),
                "machine": p.get("machine"),
                "source": "linkedin-voice.yaml",
            }
        )
        existing.add(founder)
        added += 1
    if added:
        data["entries"] = entries
        data["updated"] = linkedin.get("updated", "2026-06-12")
        DICT.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return added


def sync(*, regen_canvas: bool = True) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from founder_voice_terminology_v1 import canvas_terminology  # noqa: WPS433

    linkedin = _load_yaml(FL / "linkedin-voice.yaml")
    terms = canvas_terminology()
    _patch_open_row_spec(terms)
    dict_added = _merge_dictionary(linkedin)
    steps: list[str] = ["open_row_spec", f"dictionary+{dict_added}"]
    if regen_canvas:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/generate_integrity_canvas_form_data_v1.py")],
            check=False,
        )
        steps.append("generate_canvas")
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/live_founder_decision_form_v1.py"), "--write-receipt"],
            check=False,
        )
        steps.append("write_receipt")
    return {"ok": True, "terminology_count": len(terms), "dictionary_added": dict_added, "steps": steps}


def main() -> int:
    import json

    ap = __import__("argparse").ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-canvas", action="store_true")
    args = ap.parse_args()
    result = sync(regen_canvas=not args.no_canvas)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"OK: sync founder linkedin voice · terms={result['terminology_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
