#!/usr/bin/env python3
"""Append human-permission forks to form intake queue → M1 Canvas on next regen."""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
INTAKE_PATH = Path.home() / ".sina/live-founder-decision-form-intake-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load() -> dict:
    if INTAKE_PATH.is_file():
        return json.loads(INTAKE_PATH.read_text(encoding="utf-8"))
    return {"schema": "live-founder-decision-form-intake-v1", "rows": []}


def _save(data: dict) -> None:
    INTAKE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    INTAKE_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def append_row(
    *,
    qid: str,
    title: str,
    question: str,
    options: list[str],
    recommended: str,
    effect: str,
    blocks: str = "",
    asked_by: str = "form_conflict_intake_v1",
) -> dict:
    data = _load()
    rows = list(data.get("rows") or [])
    if any(r.get("id") == qid for r in rows):
        return {"ok": False, "error": f"duplicate id {qid}"}
    row = {
        "id": qid,
        "title": title,
        "question": question,
        "blocks": blocks,
        "recommended": recommended,
        "options": options,
        "effect": effect,
        "asked_by": asked_by,
        "reply_template": f"ASF: FIVE-STEP — PICK: {qid} {recommended}",
        "intake_id": str(uuid.uuid4())[:8],
        "intake_at": _now(),
    }
    rows.append(row)
    data["rows"] = rows
    _save(data)
    return {"ok": True, "row": row, "path": str(INTAKE_PATH)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Form conflict intake — new founder-permission rows")
    ap.add_argument("--id", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--question", required=True)
    ap.add_argument("--recommended", required=True)
    ap.add_argument("--effect", required=True)
    ap.add_argument("--blocks", default="")
    ap.add_argument("--options", nargs="+", required=True)
    ap.add_argument("--regen", action="store_true", help="Regenerate M1 Canvas after intake")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = append_row(
        qid=args.id,
        title=args.title,
        question=args.question,
        options=args.options,
        recommended=args.recommended,
        effect=args.effect,
        blocks=args.blocks,
    )
    if result.get("ok") and args.regen:
        import subprocess

        root = SCRIPTS.parent
        wire = subprocess.run(
            [sys.executable, str(SCRIPTS / "form_official_wire_e2e_v1.py"), "--json"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
        )
        result["regenerated"] = True
        result["wire_ok"] = wire.returncode == 0
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("OK" if result.get("ok") else f"FAIL: {result.get('error')}")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
