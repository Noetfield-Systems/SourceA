#!/usr/bin/env python3
"""Merge founder-language + LinkedIn voice → FORM_TERMINOLOGY for M1 Canvas."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FL = ROOT / "archive/attachments/founder-language"


def _load_yaml(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def canvas_terminology(*, max_rows: int = 16) -> list[dict[str, str]]:
    """Return {term, sayInstead} rows for Canvas FORM_TERMINOLOGY_REQUIRED."""
    rows: list[dict[str, str]] = []
    seen: set[str] = set()

    def add(term: str, say: str) -> None:
        term = (term or "").strip()
        say = (say or "").strip()
        if not term or term in seen:
            return
        seen.add(term)
        rows.append({"term": term, "sayInstead": say})

    # Core form discipline (always first)
    add("Hub Track", "sidebar projection only — not the form office")
    add("Maintainer explains in chat", "case written on the form row (this card)")
    add("EXTERNAL_CRITIC", "ChatGPT/advisor paste — report only, never build order")
    add("FORM_OFFICIAL", "this Canvas — Pending confirmations · Submit when done")
    add("Canva", "Cursor Canvas")
    add("616 / factory drain hero", "background honest counter — not pitch headline")

    linkedin = _load_yaml(FL / "linkedin-voice.yaml")
    for p in linkedin.get("linkedin_phrases") or []:
        add(str(p.get("founder", "")), str(p.get("plain", "")))

    for p in linkedin.get("form_row_copy", {}).get("banned_in_rows") or []:
        add(str(p), "use plain English on the form card")

    perimeter = linkedin.get("perimeter") or {}
    for p in perimeter.get("never") or []:
        add(str(p), "RPAA-safe advisory only — see linkedin-voice.yaml perimeter.say")

    add("Trust OS / Decision Cloud", "controlled execution layer · demo scope")
    add("hub is not a goal", "Hub projects disk — agentic engine is the goal")

    dictionary = _load_yaml(FL / "dictionary.yaml")
    for e in dictionary.get("entries") or []:
        if len(rows) >= max_rows:
            break
        not_val = e.get("not")
        plain = e.get("plain") or e.get("machine")
        if not_val:
            add(str(e.get("founder", "")), f"{plain} — not {not_val}")

    return rows[:max_rows]


def main() -> int:
    print(json.dumps({"ok": True, "terminology": canvas_terminology()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
