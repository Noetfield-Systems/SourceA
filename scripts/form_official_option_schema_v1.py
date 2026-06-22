#!/usr/bin/env python3
"""FORM_OFFICIAL — stable 5-slot option schema (A–D + E free-text).

SSOT: data/form-official-question-schema-v1.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/form-official-question-schema-v1.json"
CHOICE_KEYS = ("A", "B", "C", "D")
FIFTH_KEY = "E"
FIFTH_LABEL = "5 — Write your own answer"
FIFTH_PLACEHOLDER = "Type your answer here (option 5)"


def _pick_key(opt: str) -> str:
    m = re.match(r"^([A-Za-z0-9_]+)", str(opt or "").strip())
    return m.group(1).upper() if m else ""


def _strip_prefix(opt: str) -> str:
    return re.sub(r"^[A-Za-z0-9_]+\s*[—–\-:]\s*", "", str(opt or "").strip())


def load_schema() -> dict:
    if not SCHEMA_PATH.is_file():
        return {"schema": "form-official-question-schema-v1", "option_count": 5}
    try:
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": "form-official-question-schema-v1", "option_count": 5}


def normalize_question_options(raw_options: list | None) -> list[dict]:
    """Exactly 5 slots — 4 choices + founder free-text (E)."""
    keyed: dict[str, str] = {}
    sequential: list[str] = []
    for opt in raw_options or []:
        key = _pick_key(opt)
        text = _strip_prefix(opt) or str(opt).strip()
        if key == FIFTH_KEY:
            continue
        if key in CHOICE_KEYS and key not in keyed:
            keyed[key] = text
        else:
            sequential.append(text)

    ordered: list[dict] = []
    seq_i = 0
    for i, key in enumerate(CHOICE_KEYS):
        if key in keyed:
            text = keyed[key]
        elif seq_i < len(sequential):
            text = sequential[seq_i]
            seq_i += 1
        else:
            text = "—"
        ordered.append(
            {
                "slot": i + 1,
                "key": key,
                "type": "choice",
                "text": text,
                "label": f"{key} — {text}",
                "disabled": text == "—",
            }
        )

    ordered.append(
        {
            "slot": 5,
            "key": FIFTH_KEY,
            "type": "founder_free_text",
            "text": FIFTH_LABEL,
            "label": FIFTH_LABEL,
            "placeholder": FIFTH_PLACEHOLDER,
        }
    )
    return ordered


def normalize_question_row(q: dict) -> dict:
    """Agent-stable card row for hub + /form/."""
    slots = normalize_question_options(q.get("options"))
    choice_labels = [s["label"] for s in slots if s["type"] == "choice"]
    # Legacy options[] strings for older consumers
    legacy = choice_labels + [f"E — {FIFTH_LABEL}"]
    rec = str(q.get("recommended") or "").strip().upper()[:1] or None
    return {
        "id": q.get("id"),
        "number": q.get("number"),
        "subject": q.get("title") or q.get("subject") or "",
        "title": q.get("title") or "",
        "question": q.get("question") or "",
        "options": legacy,
        "option_slots": slots,
        "option_schema": "form-official-question-schema-v1",
        "option_count": 5,
        "recommended": rec,
        "gather_tier": q.get("gather_tier") or "",
        "prior_pick": q.get("prior_pick") or "",
        "effect": q.get("effect") or "",
        "blocks": q.get("blocks") or "",
        "reply_template": q.get("reply_template") or "",
        "option_effects": q.get("option_effects") or {},
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="FORM_OFFICIAL 5-slot option schema")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--schema", action="store_true")
    args = ap.parse_args()
    if args.schema:
        print(json.dumps(load_schema(), indent=2))
        return 0
    sample = normalize_question_row(
        {
            "id": "Q-SAMPLE",
            "title": "Sample",
            "question": "Pick one",
            "options": ["A — yes", "B — no"],
            "recommended": "A",
        }
    )
    if args.json:
        print(json.dumps(sample, indent=2))
    else:
        print(f"slots={len(sample['option_slots'])} schema={sample['option_schema']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
