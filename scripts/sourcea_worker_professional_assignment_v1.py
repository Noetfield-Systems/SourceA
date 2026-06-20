#!/usr/bin/env python3
"""SourceA Worker professional assignment — cloud-first phased queue (Mac Law).

Phase 1: Cloud plans (Brain cloud 1000 + FORGE + FBE)
Phase 2: Marketing (competitor-1000 × 5 stacks)
Phase 3: Build (sourcea-1000 REGISTRY)

Law: Mac = control panel only · execution on cloud/API workers.
SSOT: data/sourcea-worker-professional-assignment-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
ASSIGNMENT = ROOT / "data" / "sourcea-worker-professional-assignment-v1.json"
RECEIPT = SINA / "sourcea-worker-professional-assignment-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_assignment() -> dict:
    if not ASSIGNMENT.is_file():
        raise SystemExit(f"FAIL missing {ASSIGNMENT}")
    return json.loads(ASSIGNMENT.read_text(encoding="utf-8"))


def _active_item(row: dict) -> tuple[dict, dict]:
    active = row.get("active") or {}
    phase_id = str(active.get("phase_id") or "phase-cloud")
    queue_id = str(active.get("queue_id") or "")
    phase = next((p for p in row.get("phases") or [] if p.get("id") == phase_id), None)
    if not phase:
        raise SystemExit(f"FAIL unknown phase {phase_id}")
    if phase_id == "phase-cloud":
        item = next((q for q in phase.get("queue") or [] if q.get("id") == queue_id), None)
        if not item:
            item = (phase.get("queue") or [{}])[0]
        return phase, item
    return phase, {"id": phase_id, "role": "act", "title": phase.get("label", phase_id)}


def _proof_block(item: dict) -> str:
    mac_proof = item.get("mac_proof") or []
    hub = item.get("hub_dispatch") if isinstance(item.get("hub_dispatch"), dict) else None
    verify = item.get("verify") or []
    lines: list[str] = []
    if mac_proof:
        lines.append("**Read receipts (Read tool only):**")
        lines.extend(f"- `{p}`" for p in mac_proof)
    if hub and hub.get("path"):
        body = hub.get("body") or {}
        lines.append("")
        lines.append("**Optional one Hub POST (Mac control plane only):**")
        lines.append(f"- `POST http://127.0.0.1:13020{hub['path']}`")
        lines.append(f"- body: `{json.dumps(body)}`")
    if not lines and verify:
        lines.extend(f"- `{c}`" for c in verify)
    if not lines:
        lines.append("- Read assignment SSOT `mac_proof` + optional `hub_dispatch`")
    bind = item.get("mac_ctl_bind")
    if bind:
        lines.append(f"- MAC-CTL bind: `{bind}`")
    return "\n".join(lines)


def _prompt_for_item(phase: dict, item: dict) -> str:
    pid = phase.get("id", "")
    wid = item.get("id", "?")
    role = str(item.get("role") or "check").upper()
    title = item.get("title") or phase.get("label") or wid
    proof_block = _proof_block(item)
    mac_law = (
        "**Mac Law:** Mac observes only — Hub :13020 · Mac Health · Routing · Mac Law cockpit. "
        "No factory motors · no Mac build when `mac_build_forbidden: true`. "
        "Cloud FORGE / Railway FBE executes."
    )
    return f"""# SourceA Worker — {wid} · {role}

**Phase:** {phase.get('label', pid)} · **Execution plane:** {item.get('execution_plane') or phase.get('execution_plane', 'cloud_api_worker')}
**Assignment SSOT:** `data/sourcea-worker-professional-assignment-v1.json`
**Mac Law:** `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md`

## Task

{title}

{mac_law}

## This turn ({role} only)

1. `python3 scripts/prompt_feasibility_gate.py --role worker --strict`
2. `bash scripts/worker_turn_entry_v1.sh`
3. Execute role — **one turn · one item · STOP**

## Mac proof (Read only · optional one Hub POST)

{proof_block}

## Forbidden on Mac

- `validate-*` bash chains · local `forge_competitor_run` body · local `brain_cloud_reasoning_plan_pulse` body
- Mac factory body · local motor drain · building app code on Mac when cloud_forge
- Batch multiple queue items · skip WORKER_ROUND_REPORT

## Close

```yaml
status: WORKER_ROUND_REPORT
round_type: check | act | verify
sa_focus: {item.get('sa_bind') or wid}
assignment_id: {wid}
phase_id: {pid}
execution_plane: cloud
validate:
  spine: PASS|FAIL
summary: one line Mac Law + cloud receipt path
```

Then: `python3 scripts/goal1_lane_broker.py worker-submit --stdin`
"""


def build_prompt(row: dict | None = None) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import normalize_sa_id  # noqa: WPS433

    row = row or load_assignment()
    phase, item = _active_item(row)
    prompt = _prompt_for_item(phase, item)
    active = row.get("active") or {}
    meta = {
        "sa_id": normalize_sa_id(str(item.get("sa_bind") or item.get("id") or "W-CLOUD-001")),
        "queue_role": str(item.get("role") or active.get("role") or "check"),
        "queue_pos": int(active.get("queue_pos") or 1),
        "queue_total": int(active.get("queue_total") or 3),
        "assignment_id": str(item.get("id") or ""),
        "phase_id": str(phase.get("id") or ""),
        "execution_plane": str(item.get("execution_plane") or phase.get("execution_plane") or "cloud_api_worker"),
        "mac_build_forbidden": bool(item.get("mac_build_forbidden", True)),
        "source": "sourcea_worker_professional_assignment_v1",
    }
    return {"ok": True, "prompt": prompt, "meta": meta, "phase": phase.get("id"), "item": item.get("id")}


def advance_queue(*, write: bool = True) -> dict:
    row = load_assignment()
    active = dict(row.get("active") or {})
    phase_id = str(active.get("phase_id") or "phase-cloud")
    if phase_id != "phase-cloud":
        return {"ok": False, "error": "advance_only_phase_cloud", "phase_id": phase_id}
    phase = next((p for p in row.get("phases") or [] if p.get("id") == phase_id), None)
    queue = phase.get("queue") or [] if phase else []
    if not queue:
        return {"ok": False, "error": "empty_queue"}
    cur_id = str(active.get("queue_id") or queue[0].get("id") or "")
    idx = next((i for i, q in enumerate(queue) if q.get("id") == cur_id), 0)
    next_idx = min(idx + 1, len(queue) - 1)
    nxt = queue[next_idx]
    active.update(
        {
            "phase_id": phase_id,
            "queue_id": str(nxt.get("id") or ""),
            "queue_pos": next_idx + 1,
            "queue_total": len(queue),
            "role": str(nxt.get("role") or "check"),
        }
    )
    row["active"] = active
    row["saved_at"] = _now()
    if write:
        ASSIGNMENT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "from": cur_id,
        "to": active["queue_id"],
        "queue_pos": active["queue_pos"],
        "role": active["role"],
    }


def inject_next(*, dry_run: bool = False) -> dict:
    built = build_prompt()
    if dry_run:
        return {**built, "dry_run": True, "injected": False}

    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import deliver_to_worker_inbox, write_active_inbox_rule  # noqa: WPS433

    result = deliver_to_worker_inbox(
        built["prompt"],
        source="sourcea_worker_professional_assignment",
        meta=built["meta"],
    )
    if result.get("ok") and not result.get("blocked_by_freeze"):
        write_active_inbox_rule(built["prompt"], meta=built["meta"])
    receipt = {
        "schema": "sourcea-worker-professional-assignment-receipt-v1",
        "at": _now(),
        "assignment": str(ASSIGNMENT),
        "active": built["meta"],
        "inject": result,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return {**built, "inject": result, "receipt": str(RECEIPT)}


def status() -> dict:
    row = load_assignment()
    phase, item = _active_item(row)
    return {
        "ok": True,
        "at": _now(),
        "one_law": row.get("one_law"),
        "active_phase": phase.get("id"),
        "active_item": item.get("id"),
        "active_title": item.get("title"),
        "role": item.get("role"),
        "phases": [{"id": p.get("id"), "order": p.get("order"), "label": p.get("label")} for p in row.get("phases") or []],
        "mac_law": row.get("mac_law", {}).get("control_plane"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA Worker professional assignment (cloud-first)")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--show-prompt", action="store_true")
    ap.add_argument("--inject-next", action="store_true")
    ap.add_argument("--advance-queue", action="store_true", help="Advance phase-cloud queue then inject-next")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.status:
        out = status()
    elif args.show_prompt:
        out = build_prompt()
    elif args.inject_next:
        out = inject_next(dry_run=args.dry_run)
    elif args.advance_queue:
        adv = advance_queue(write=not args.dry_run)
        if not adv.get("ok"):
            out = adv
        else:
            out = {**adv, **inject_next(dry_run=args.dry_run)}
    else:
        ap.print_help()
        return 0

    if args.json or args.status or args.inject_next or args.show_prompt or args.advance_queue:
        print(json.dumps(out, indent=2))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
