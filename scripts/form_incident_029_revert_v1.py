#!/usr/bin/env python3
"""INCIDENT-029 revert — remove agent-applied FORM picks (not founder Submit).

Removes §ANSWERED rows written by canvas_form_apply_picks_v1.py · resets applied JSON ·
enables form-agent-submit-forbidden flag.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from governance_paths_v1 import LIVE_FOUNDER_FORM

FORM_MD = LIVE_FOUNDER_FORM
SINA = Path.home() / ".sina"
APPLIED = SINA / "canvas-form-picks-applied-v1.json"
APPLIED_LOG = SINA / "canvas-form-picks-applied-v1.jsonl"
CANVAS_DATA = (
    Path.home()
    / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.data.json"
)
ARCHIVE = SINA / "archive" / "form-incident-029"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _archive(path: Path) -> Path | None:
    if not path.is_file():
        return None
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    dest = ARCHIVE / f"{path.name}.{_now().replace(':', '')}.bak"
    shutil.copy2(path, dest)
    return dest


def revert_form_md() -> dict:
    text = FORM_MD.read_text(encoding="utf-8")
    marker = "## 2. §ANSWERED — locked from evidence"
    if marker not in text:
        return {"ok": False, "error": "missing ANSWERED section"}

    head, tail = text.split(marker, 1)
    lines = tail.splitlines()
    kept: list[str] = []
    removed: list[str] = []
    for line in lines:
        if "canvas_form_apply_picks_v1.py" in line:
            m = re.search(r"\| \*\*([^|*]+)\*\*", line)
            if m:
                removed.append(m.group(1).strip())
            continue
        kept.append(line)

    FORM_MD.write_text(head + marker + "\n" + "\n".join(kept) + "\n", encoding="utf-8")
    return {"ok": True, "removed_count": len(removed), "removed_ids": removed}


def reset_applied_json() -> dict:
    bak = _archive(APPLIED)
    bak_log = _archive(APPLIED_LOG)
    empty = {"schema": "canvas-form-picks-applied-v1", "picks": {}, "reverted_at": _now(), "incident": "INCIDENT-029"}
    APPLIED.write_text(json.dumps(empty, indent=2) + "\n", encoding="utf-8")
    if APPLIED_LOG.is_file():
        APPLIED_LOG.write_text("", encoding="utf-8")
    return {"ok": True, "applied_backup": str(bak) if bak else None, "log_backup": str(bak_log) if bak_log else None}


def reset_canvas_confirmed() -> dict:
    if not CANVAS_DATA.is_file():
        return {"ok": True, "skipped": "no canvas data"}
    _archive(CANVAS_DATA)
    data = json.loads(CANVAS_DATA.read_text(encoding="utf-8"))
    data["confirmed"] = {k: False for k in (data.get("confirmed") or {})}
    data["hub_form_automatic"] = False
    data["agent_revert_at"] = _now()
    data["incident"] = "INCIDENT-029"
    CANVAS_DATA.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "canvas": str(CANVAS_DATA)}


def refresh_form_receipts() -> list[dict]:
    steps = []
    for label, cmd in [
        ("write_receipt", [sys.executable, str(ROOT / "scripts/live_founder_decision_form_v1.py"), "--write-receipt"]),
        ("form_reconcile", [sys.executable, str(ROOT / "scripts/form_open_questions_reconcile_v1.py"), "--json"]),
    ]:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=120)
        steps.append({"step": label, "ok": proc.returncode == 0, "rc": proc.returncode})
    return steps


def main() -> int:
    ap = argparse.ArgumentParser(description="INCIDENT-029 form revert")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        text = FORM_MD.read_text(encoding="utf-8")
        n = sum(1 for line in text.splitlines() if "canvas_form_apply_picks_v1.py" in line)
        out = {"ok": True, "dry_run": True, "would_remove_rows": n}
        print(json.dumps(out, indent=2))
        return 0

    _archive(FORM_MD)
    md = revert_form_md()
    applied = reset_applied_json()
    canvas = reset_canvas_confirmed()

    sys.path.insert(0, str(ROOT / "scripts"))
    from form_founder_supremacy_guard_v1 import write_block_receipt  # noqa: WPS433

    block = write_block_receipt(
        reason="Founder never submitted FORM 116 — Worker used canvas_form_apply_picks + hub automatic",
        reverted_ids=md.get("removed_ids") or [],
    )
    steps = refresh_form_receipts()

    out = {
        "ok": md.get("ok", False),
        "at": _now(),
        "incident": "INCIDENT-029",
        "form_md": md,
        "applied": applied,
        "canvas": canvas,
        "block_receipt": str(block),
        "refresh_steps": steps,
    }
    receipt = SINA / "form-incident-029-revert-receipt-v1.json"
    receipt.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    out["receipt_path"] = str(receipt)

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"OK: reverted {md.get('removed_count', 0)} agent rows · block ON · open={receipt}")
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
