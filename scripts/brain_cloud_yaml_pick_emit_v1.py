#!/usr/bin/env python3
"""B0012 — Brain pick vs Worker paste: emit structured YAML pick, not prose.

Law: brain-cloud-reasoning E01 · Brain routes · Worker executes · YAML is SSOT for picks.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "brain-cloud-reasoning-1000-upgrade-plan-v1.json"
SINA = Path.home() / ".sina"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _yaml_quote(s: str) -> str:
    if not s or any(c in s for c in ':"\\\'\n'):
        return json.dumps(s, ensure_ascii=False)
    return s


def next_planned_pick(*, upgrade_id: str | None = None) -> dict | None:
    plan = _read(PLAN)
    upgrades = plan.get("upgrades") or []
    if upgrade_id:
        for u in upgrades:
            if u.get("id") == upgrade_id:
                return u
        return None
    active = plan.get("active_epic") or "E01"
    for u in upgrades:
        if u.get("status") == "planned" and u.get("epic") == active:
            return u
    for u in upgrades:
        if u.get("status") == "planned":
            return u
    return None


def emit_brain_pick(*, upgrade_id: str | None = None) -> dict:
    pick = next_planned_pick(upgrade_id=upgrade_id)
    wo = _read(SINA / "brain-outbound-work-order-active-v1.json")
    inbox = _read(SINA / "worker-prompt-inbox-v1.json")
    surfaces = _read(SINA / "agent-live-surfaces-v1.json")

    if not pick:
        return {"ok": False, "error": "no_planned_brain_pick", "at": _now()}

    pid = str(pick.get("id") or "")
    reconcile = {
        "brain_surface": "brain_yaml_pick",
        "worker_surface": "worker_inbox_paste",
        "rule": "Brain emits YAML pick block — Worker must not paste prose picks",
        "forbidden": ["prose_pick", "chat_summary_as_ssot", "worker_scope_in_brain_chat"],
    }
    worker_scope = {
        "lane": pick.get("lane") or "brain_reasoning",
        "execution_plane": pick.get("execution_plane") or "cloud_api_worker",
        "control_plane": pick.get("control_plane") or "mac_hub",
        "local_worker_deprecated": bool(pick.get("local_worker_deprecated")),
    }
    row = {
        "schema": "brain-cloud-yaml-pick-v1",
        "version": "1.0.0",
        "at": _now(),
        "ok": True,
        "upgrade_id": pid,
        "title": pick.get("title") or "",
        "epic": pick.get("epic"),
        "tier": pick.get("tier"),
        "brain_pick": {
            "id": pid,
            "pick": f"ROUTE:{pid}",
            "intent": pick.get("title") or "",
            "acceptance": pick.get("acceptance") or "",
            "owner_role": "brain",
            "emit_format": "yaml_only",
        },
        "reconcile": reconcile,
        "worker_scope": worker_scope,
        "work_order": {
            "active": bool(wo.get("work_order_id")),
            "id": wo.get("work_order_id"),
            "execution_mode": wo.get("execution_mode"),
        },
        "inbox_pending": bool(inbox.get("pending")),
        "factory_now_line": surfaces.get("factory_now_line") or "",
        "brain_yaml_line": f"brain-yaml-pick · {pid} · prose=FORBIDDEN · worker_paste=BLOCKED",
    }
    return row


def to_yaml_block(row: dict) -> str:
    if not row.get("ok"):
        return f"schema: brain-cloud-yaml-pick-v1\nok: false\nerror: {_yaml_quote(str(row.get('error') or 'unknown'))}\n"
    bp = row.get("brain_pick") or {}
    lines = [
        "schema: brain-cloud-yaml-pick-v1",
        f"at: {_yaml_quote(str(row.get('at') or ''))}",
        "ok: true",
        "brain_pick:",
        f"  id: {_yaml_quote(str(bp.get('id') or ''))}",
        f"  pick: {_yaml_quote(str(bp.get('pick') or ''))}",
        f"  intent: {_yaml_quote(str(bp.get('intent') or ''))}",
        f"  emit_format: yaml_only",
        "reconcile:",
        f"  brain_surface: {_yaml_quote(str((row.get('reconcile') or {}).get('brain_surface') or ''))}",
        f"  worker_surface: {_yaml_quote(str((row.get('reconcile') or {}).get('worker_surface') or ''))}",
        f"  rule: {_yaml_quote(str((row.get('reconcile') or {}).get('rule') or ''))}",
        "worker_scope:",
        f"  execution_plane: {_yaml_quote(str((row.get('worker_scope') or {}).get('execution_plane') or ''))}",
        f"  local_worker_deprecated: {str(bool((row.get('worker_scope') or {}).get('local_worker_deprecated'))).lower()}",
        f"brain_yaml_line: {_yaml_quote(str(row.get('brain_yaml_line') or ''))}",
    ]
    return "\n".join(lines) + "\n"


def mark_done(upgrade_id: str, *, receipt: str = "") -> dict:
    plan = _read(PLAN)
    upgrades = plan.get("upgrades") or []
    hit = False
    for u in upgrades:
        if u.get("id") == upgrade_id:
            u["status"] = "done"
            u["done_at"] = _now()
            u["brain_proof"] = True
            if receipt:
                u["receipt"] = receipt
            hit = True
            break
    if not hit:
        return {"ok": False, "error": f"missing {upgrade_id}"}
    done = sum(1 for u in upgrades if u.get("status") == "done")
    prog = plan.setdefault("progress", {})
    prog["done"] = done
    prog["planned"] = sum(1 for u in upgrades if u.get("status") == "planned")
    prog["brain_reasoning_proven"] = sum(1 for u in upgrades if u.get("brain_proof"))
    prog["pct"] = round(100 * done / len(upgrades)) if upgrades else 0
    plan["saved_at"] = _now()
    PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "upgrade_id": upgrade_id, "done": done, "total": len(upgrades)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Brain cloud YAML pick emitter (B0012)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--yaml", action="store_true")
    ap.add_argument("--id", default="", help="Upgrade id e.g. B0012")
    ap.add_argument("--mark-done", action="store_true")
    ap.add_argument("--receipt", default="")
    args = ap.parse_args()
    uid = args.id.strip() or None
    if args.mark_done and uid:
        out = mark_done(uid, receipt=args.receipt)
    else:
        out = emit_brain_pick(upgrade_id=uid)
        if args.yaml:
            print(to_yaml_block(out))
            return 0 if out.get("ok") else 1
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(out.get("brain_yaml_line") or json.dumps(out))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
