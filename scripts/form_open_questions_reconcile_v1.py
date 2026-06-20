#!/usr/bin/env python3
"""Reconcile form open rows ↔ M1 Canvas ↔ applied picks — FORM_OFFICIAL audit."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
M1_CANVAS = (
    Path.home()
    / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.tsx"
)
AUDIT_PATH = Path.home() / ".sina/form-open-questions-reconcile-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canvas_open_ids() -> list[str]:
    if not M1_CANVAS.is_file():
        return []
    text = M1_CANVAS.read_text(encoding="utf-8", errors="replace")
    m = re.search(
        r"const OPEN_FORM_QUESTIONS = \[(.*?)\];\s*\n// @generated-integrity-form-data-end",
        text,
        re.S,
    )
    if not m:
        return []
    return re.findall(r'\bid:\s*"([^"]+)"', m.group(1))


def reconcile(*, regen: bool = False) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from live_founder_decision_form_v1 import (  # noqa: WPS433
        OPEN_QUESTIONS_CORE,
        PENDING_OUTSIDE_AS_OPEN,
        _canvas_applied_pick_ids,
        _load_enf_open_questions,
        _load_intake_questions,
        all_open_questions,
    )

    applied = _canvas_applied_pick_ids()
    all_defs = {q["id"]: q for q in OPEN_QUESTIONS_CORE + PENDING_OUTSIDE_AS_OPEN + _load_enf_open_questions()}
    intake = _load_intake_questions()
    for q in intake:
        all_defs.setdefault(q["id"], q)
    open_rows = all_open_questions()
    open_ids = [q["id"] for q in open_rows]
    canvas_ids = _canvas_open_ids()

    missing_canvas = sorted(set(open_ids) - set(canvas_ids))
    extra_canvas = sorted(set(canvas_ids) - set(open_ids))
    closed_core = sorted(set(q["id"] for q in OPEN_QUESTIONS_CORE) & applied)

    result = {
        "ok": not missing_canvas and not extra_canvas,
        "schema": "form-open-questions-reconcile-v1",
        "audited_at": _now(),
        "open_count": len(open_ids),
        "open_ids": open_ids,
        "canvas_open_count": len(canvas_ids),
        "canvas_open_ids": canvas_ids,
        "applied_count": len(applied),
        "defined_count": len(all_defs),
        "intake_pending_count": len(intake),
        "missing_on_canvas": missing_canvas,
        "extra_on_canvas": extra_canvas,
        "closed_via_apply_sample": closed_core[:15],
        "policy": "100-pack POV stays on Canvas · §OPEN forks only on OPEN_FORM_QUESTIONS · Hub shows count only",
    }

    if regen and (missing_canvas or extra_canvas):
        subprocess.run([sys.executable, str(SCRIPTS / "generate_integrity_canvas_form_data_v1.py")], check=False)
        canvas_ids = _canvas_open_ids()
        result["regenerated"] = True
        result["canvas_open_ids_after"] = canvas_ids
        result["ok"] = set(open_ids) == set(canvas_ids)

    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    result["audit_path"] = str(AUDIT_PATH)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit form open rows vs M1 Canvas")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--regen", action="store_true", help="Regenerate canvas OPEN block if mismatch")
    args = ap.parse_args()
    result = reconcile(regen=args.regen)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "OK" if result.get("ok") else "MISMATCH"
        print(
            f"{status}: open={result.get('open_count')} canvas={result.get('canvas_open_count')} "
            f"missing={result.get('missing_on_canvas')} extra={result.get('extra_on_canvas')}"
        )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
