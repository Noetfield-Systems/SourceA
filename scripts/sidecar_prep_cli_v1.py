#!/usr/bin/env python3
"""Lane C — CLI prep. Lookahead ACT plan only while awake. Never advances boss queue."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OUT = Path.home() / ".sina" / "sidecar" / "cli-prep"
LOG = Path.home() / ".sina" / "sidecar-prep-cli-v1.jsonl"

sys.path.insert(0, str(SCRIPTS))
from healthy_queue_ssot_lib import (  # noqa: E402
    healthy_queue_state_path,
    load_healthy_queue,
    queue_items,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def _current_pos() -> int:
    st = healthy_queue_state_path()
    if st.is_file():
        try:
            return int(json.loads(st.read_text()).get("next_pos") or 1)
        except (ValueError, json.JSONDecodeError):
            pass
    return 1


def _next_act() -> dict | None:
    _, raw = load_healthy_queue()
    items = queue_items(raw)
    pos = _current_pos()
    for i in range(pos, len(items) + 1):
        item = items[i - 1]
        if (item.get("queue_role") or "").lower() == "act":
            return {**item, "_lookahead_pos": i}
    return None


def _resolve_sa_file(sa_path: str) -> Path | None:
    if not sa_path:
        return None
    for base in (ROOT, ROOT / "brain-os/plan-registry/sourcea-1000"):
        p = base / sa_path
        if p.is_file():
            return p
    return None


def _prep_plan(item: dict, *, dry_run: bool) -> dict:
    sa_id = item.get("sa_id", "unknown")
    out = OUT / f"{sa_id}-prep.md"
    scout = Path.home() / ".sina" / "sidecar" / "api-scout" / f"{sa_id}-scout.md"
    scout_ok = scout.is_file() and "don't have access" not in scout.read_text(encoding="utf-8", errors="replace").lower()
    if out.is_file() and out.stat().st_size > 200 and scout_ok:
        return {"ok": True, "sa_id": sa_id, "skipped": "prep_exists", "path": str(out)}

    sa_path = item.get("sa_path") or ""
    instr = item.get("instruction") or item.get("title") or ""
    sa_body = ""
    resolved = _resolve_sa_file(sa_path)
    if resolved:
        sa_body = resolved.read_text(encoding="utf-8", errors="replace")[:3000]
    scout_note = scout.read_text(encoding="utf-8", errors="replace")[:4000] if scout.is_file() else "(no scout yet)"

    plan = f"""# CLI prep — {sa_id}

**At:** {_now()}
**Lane:** C (plan only — no repo edits, no queue advance)
**Lookahead pos:** {item.get('_lookahead_pos')}

## Task
{instr}

## Path
{sa_path}

## Task file (registry path)
{sa_body or "(task file not found)"}

## API scout context
{scout_note}

## Suggested minimal diff plan
1. Read `{sa_path}` and bound files only.
2. List exact files/lines to touch.
3. List validators to run after Worker ACT.
4. Do NOT edit repo — Worker ships on boss lane.
"""
    if dry_run:
        _log({"event": "dry_run", "sa_id": sa_id})
        return {"ok": True, "dry_run": True, "sa_id": sa_id}

    OUT.mkdir(parents=True, exist_ok=True)
    out.write_text(plan, encoding="utf-8")
    _log({"event": "prep_written", "sa_id": sa_id, "path": str(out)})
    return {"ok": True, "sa_id": sa_id, "path": str(out)}


def main() -> int:
    p = argparse.ArgumentParser(description="Lane C — CLI prep (lookahead ACT plan only)")
    p.add_argument("--dry-plan", action="store_true", help="Write plan file without calling Claude CLI")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    item = _next_act()
    if not item:
        row = {"ok": True, "lane": "C", "note": "no_upcoming_act"}
        print(json.dumps(row, indent=2) if args.json else row["note"])
        return 0

    result = _prep_plan(item, dry_run=args.dry_plan)
    row = {"ok": result.get("ok"), "lane": "C", "prep": result}
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(result)
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
