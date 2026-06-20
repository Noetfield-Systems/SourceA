#!/usr/bin/env python3
"""Restore founder draft picks from INCIDENT-029 backup — exclude agent bulk (Jun 19 17:29)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
ARCHIVE = SINA / "archive" / "form-incident-029"
APPLIED_BAK = ARCHIVE / "canvas-form-picks-applied-v1.json.2026-06-19T173203Z.bak"
LOG_BAK = ARCHIVE / "canvas-form-picks-applied-v1.jsonl.2026-06-19T173203Z.bak"
CANVAS_BAK = ARCHIVE / "sourcea-system-integrity-100.canvas.data.json.2026-06-19T173203Z.bak"
DRAFT = SINA / "canvas-form-picks-draft-v1.json"
APPLIED = SINA / "canvas-form-picks-applied-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def agent_bulk_ids() -> set[str]:
    if not LOG_BAK.is_file():
        return set()
    out: set[str] = set()
    for line in LOG_BAK.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        at = str(e.get("at") or "")
        comment = str(e.get("comment") or "").strip()
        if at.startswith("2026-06-19T17:29") and not comment:
            out.add(str(e.get("id") or ""))
    return {x for x in out if x}


def restore(*, write: bool = True) -> dict:
    bulk = agent_bulk_ids()
    picks: dict[str, str] = {}
    if APPLIED_BAK.is_file():
        bak = json.loads(APPLIED_BAK.read_text(encoding="utf-8"))
        for qid, pick in (bak.get("picks") or {}).items():
            if qid not in bulk:
                picks[str(qid)] = str(pick)

    body = {
        "schema": "canvas-form-picks-draft-v1",
        "at": _now(),
        "incident": "INCIDENT-029",
        "law": "Draft only — NOT §ANSWERED until founder Hub Submit",
        "picks": picks,
        "excluded_agent_bulk_count": len(bulk),
        "restored_count": len(picks),
    }
    if write:
        DRAFT.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
        APPLIED.write_text(
            json.dumps(
                {"schema": "canvas-form-picks-applied-v1", "picks": {}, "draft_ref": str(DRAFT), "at": _now()},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        if CANVAS_BAK.is_file():
            canvas = json.loads(CANVAS_BAK.read_text(encoding="utf-8"))
            canvas["picks"] = {k: picks[k] for k in picks if k in (canvas.get("picks") or {}) or k in picks}
            for k in picks:
                canvas.setdefault("picks", {})[k] = picks[k]
            canvas["confirmed"] = {k: False for k in picks}
            canvas["draft_only"] = True
            canvas["restored_at"] = _now()
            canvas_path = Path(
                str(
                    canvas.get("_path")
                    or "~/.cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.data.json"
                ).replace("~", str(Path.home()))
            )
            if CANVAS_BAK.name.endswith(".bak"):
                real = Path.home() / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.data.json"
                real.parent.mkdir(parents=True, exist_ok=True)
                real.write_text(json.dumps(canvas, indent=2) + "\n", encoding="utf-8")
    body["draft_path"] = str(DRAFT)
    return body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = restore()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: restored {row['restored_count']} draft picks · excluded {row['excluded_agent_bulk_count']} agent bulk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
