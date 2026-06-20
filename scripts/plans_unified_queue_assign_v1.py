#!/usr/bin/env python3
"""Assign unified plan backlog (cloud · phase0 · full-stack · brain-1000) to Worker queue + INBOX.

Runs: plans_unified_upgrade_v1.py first (sync all plan progress)
Writes: data/plans-unified-worker-queue-v1.json
        ~/.sina/healthy-queue-30-active.json
        ~/.sina/worker-prompt-inbox-v1.json
        .sina-loop/INBOX.md
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
BRAIN = ROOT / "data" / "brain-cloud-reasoning-1000-upgrade-plan-v1.json"
FULL_STACK = ROOT / "data" / "sourcea-full-stack-100-fix-plan-v1.json"
PHASE0 = ROOT / "data" / "phase0-freemium-sandbox-reference-v1.json"
QUEUE_SSOT = ROOT / "data" / "plans-unified-worker-queue-v1.json"
QUEUE_HOME = SINA / "healthy-queue-30-active.json"
QUEUE_REPO = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "prompts" / "healthy-queue-30-active.json"
STATE_HOME = SINA / "healthy-queue-state-v1.json"
PHASE = "phase-unified-plans-v1"
SA_BASE = 1200

sys.path.insert(0, str(SCRIPTS))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _tier_rank(tier: str) -> int:
    t = str(tier or "P1").upper()
    if t == "P0":
        return 0
    if t == "P1":
        return 1
    if t == "P2":
        return 2
    return 3


def _sa_id(n: int) -> str:
    return f"sa-{SA_BASE + n - 1:04d}"


def _cloud_factory_items() -> list[dict]:
    items: list[dict] = []
    try:
        from cloud_factory_check_v1 import run_check  # noqa: WPS433

        chk = run_check()
    except Exception as exc:
        return [
            {
                "id": "CF-CHECK",
                "plan": "cloud_factory_10",
                "plan_path": "scripts/cloud_factory_10_steps_v1.py",
                "title": f"Cloud factory check error: {exc}",
                "tier": "P0",
                "lane": "cloud_factory",
                "wired_to": "scripts/cloud_factory_10_steps_v1.py",
                "acceptance": "cloud_factory_check_v1 ok=True",
                "critical": True,
            }
        ]
    for c in chk.get("checks") or []:
        if c.get("ok") and not c.get("warn"):
            continue
        step = str(c.get("step") or "cf")
        items.append(
            {
                "id": f"CF-{step.upper()}",
                "plan": "cloud_factory_10",
                "plan_path": "scripts/cloud_factory_10_steps_v1.py",
                "title": f"Cloud factory {step}: {c.get('detail', '')[:80]}",
                "tier": "P0",
                "lane": "cloud_factory",
                "wired_to": "data/brain-cloud-practical-300-plan-v1.json",
                "acceptance": f"{step} ok=True on cloud_factory_check_v1",
                "critical": not c.get("warn"),
            }
        )
    return items


def _phase0_items() -> list[dict]:
    ref = _read(PHASE0)
    out: list[dict] = []
    for row in ref.get("inventory") or []:
        if row.get("status") == "done":
            continue
        out.append(
            {
                "id": str(row.get("id") or ""),
                "plan": "phase0_freemium",
                "plan_path": str(PHASE0.relative_to(ROOT)),
                "title": str(row.get("title") or ""),
                "tier": "P0",
                "lane": str(row.get("lane") or "phase0"),
                "wired_to": str(row.get("wired_to") or ""),
                "acceptance": str(row.get("acceptance") or ""),
                "critical": str(row.get("id") or "") in ("P0-13", "P0-01", "P0-02"),
            }
        )
    return out


def _full_stack_items(plan: dict) -> list[dict]:
    crit = set(plan.get("critical_path") or [])
    out: list[dict] = []
    for fix in plan.get("fixes") or []:
        if fix.get("status") == "done":
            continue
        fid = str(fix.get("id") or "")
        out.append(
            {
                "id": fid,
                "plan": "full_stack_100",
                "plan_path": str(FULL_STACK.relative_to(ROOT)),
                "title": str(fix.get("title") or fix.get("fix") or ""),
                "tier": str(fix.get("tier") or "P1"),
                "lane": str(fix.get("lane") or fix.get("layer") or "full_stack"),
                "wired_to": str(fix.get("wired_to") or fix.get("proof") or ""),
                "acceptance": str(fix.get("acceptance") or fix.get("verify") or ""),
                "critical": fid in crit,
            }
        )
    return out


def _brain_items(plan: dict) -> list[dict]:
    crit = set(plan.get("critical_path") or [])
    out: list[dict] = []
    for u in plan.get("upgrades") or []:
        if u.get("status") == "done":
            continue
        uid = str(u.get("id") or "")
        out.append(
            {
                "id": uid,
                "plan": "brain_cloud_1000",
                "plan_path": str(BRAIN.relative_to(ROOT)),
                "title": str(u.get("title") or ""),
                "tier": str(u.get("tier") or "P1"),
                "lane": str(u.get("lane") or u.get("epic") or "brain_cloud"),
                "wired_to": str(u.get("wired_to") or u.get("proof") or ""),
                "acceptance": str(u.get("acceptance") or u.get("verify") or ""),
                "critical": uid in crit,
            }
        )
    return out


WORKER_SKIP_LANES = frozenset({"brain_reasoning", "commercial_w3"})
WORKER_SKIP_ACCEPTANCE = (
    "not local cursor worker turn",
    "w3_send_ready pass",
    "brain reasoning receipt + cloud federated proof",
    "github active",
)


def _worker_queue_eligible(item: dict) -> bool:
    """Worker INBOX only — skip Brain/cloud bay + founder commercial gates."""
    lane = str(item.get("lane") or "").lower()
    if lane in WORKER_SKIP_LANES:
        return False
    blob = " ".join(
        str(item.get(k) or "")
        for k in ("title", "acceptance", "wired_to", "lane", "plan")
    ).lower()
    for skip in WORKER_SKIP_ACCEPTANCE:
        if skip in blob:
            return False
    try:
        from prompt_feasibility_gate import check_text  # noqa: WPS433

        feas = check_text(blob)
        if not feas.get("ok"):
            return False
    except Exception:
        pass
    return True


def collect_all_items(*, worker_only: bool = True) -> list[dict]:
    brain = _read(BRAIN)
    fs = _read(FULL_STACK)
    items: list[dict] = []
    items.extend(_cloud_factory_items())
    items.extend(_phase0_items())
    items.extend(_full_stack_items(fs))
    if not worker_only:
        items.extend(_brain_items(brain))

    def sort_key(row: dict) -> tuple:
        plan_order = {"cloud_factory_10": 0, "phase0_freemium": 1, "full_stack_100": 2, "brain_cloud_1000": 3}
        return (
            0 if row.get("critical") else 1,
            _tier_rank(str(row.get("tier") or "P1")),
            plan_order.get(str(row.get("plan") or ""), 9),
            str(row.get("id") or ""),
        )

    items.sort(key=sort_key)
    if worker_only:
        items = [row for row in items if _worker_queue_eligible(row)]
    return items


def _prompt_for(item: dict, *, pos: int, total: int, sa_id: str) -> str:
    uid = item.get("id", "")
    plan = item.get("plan", "")
    return (
        f"[UNIFIED_PLANS pos={pos}/{total}] sa={sa_id} role=act · {plan}\n\n"
        f"WORK: Implement **{uid}** — {item.get('title', '')}\n"
        f"Plan: {item.get('plan_path')}\n"
        f"Lane: {item.get('lane')}\n"
        f"Tier: {item.get('tier')}\n"
        f"Wired to: {item.get('wired_to')}\n"
        f"Acceptance: {item.get('acceptance')}\n\n"
        f"Law: plans_unified_upgrade_v1 · cloud factory hardening · no agent email send\n"
        f"ACT — wire minimal diff · verify acceptance · mark plan row done · "
        f"run `python3 scripts/plans_unified_upgrade_v1.py` · broker-submit · STOP"
    )


def build_assignment(*, items: list[dict] | None = None) -> dict:
    items = items if items is not None else collect_all_items()
    total = len(items)
    queue_items: list[dict] = []
    catalog: list[dict] = []

    for pos, item in enumerate(items, start=1):
        sa_id = _sa_id(pos)
        prompt = _prompt_for(item, pos=pos, total=total, sa_id=sa_id)
        row = {
            "queue_pos": pos,
            "hp_id": f"up-{item.get('plan')}-{item.get('id', pos)}",
            "queue_role": "act",
            "step_type": "implement",
            "sa_id": sa_id,
            "sa_path": f"{item.get('plan_path')}#{item.get('id')}",
            "sa_title": f"{item.get('id')} — {str(item.get('title', ''))[:72]}",
            "sa_tier": str(item.get("tier") or "P1"),
            "phase": PHASE,
            "upgrade_id": item.get("id"),
            "upgrade_lane": item.get("lane"),
            "plan_source": item.get("plan"),
            "title": f"[ACT] {item.get('id')} — {str(item.get('title', ''))[:72]}",
            "instruction": prompt,
            "verify": f"acceptance: {item.get('acceptance', '')}",
            "closeout": True,
            "one_sa_per_turn": True,
        }
        queue_items.append(row)
        catalog.append(
            {
                "upgrade_id": item.get("id"),
                "plan": item.get("plan"),
                "tier": item.get("tier"),
                "lane": item.get("lane"),
                "sa_id": sa_id,
                "queue_pos": pos,
                "title": item.get("title"),
                "status": "assigned",
            }
        )

    sa_range = [_sa_id(1), _sa_id(total)] if total else []
    doc = {
        "schema": "healthy-queue-30-active.v1",
        "product": f"Unified plans drain — {total} items (cloud · phase0 · full-stack · brain-1000)",
        "thread": "UNIFIED-PLANS",
        "repo": "sourcea",
        "count": total,
        "rhythm": "1 act per plan item · verify · mark done · plans_unified tick",
        "law": "scripts/plans_unified_upgrade_v1.py · plans_unified_queue_assign_v1.py",
        "generated_at": _now(),
        "phase_strict": False,
        "phase_strict_complete": total == 0,
        "queue_exhausted": total == 0,
        "stop_reason": None if total else "unified_plans_complete",
        "pick_floor": None,
        "sa_range": sa_range,
        "plans_unified": True,
        "queue": queue_items,
    }
    ssot = {
        "schema": "plans-unified-worker-queue-v1",
        "version": "1.0.0",
        "saved_at": _now(),
        "phase": PHASE,
        "sa_range": sa_range,
        "total": total,
        "assignments": catalog,
        "command": "python3 scripts/plans_unified_queue_assign_v1.py --deliver-first --sync",
    }
    return {"queue_doc": doc, "ssot": ssot, "head": queue_items[0] if queue_items else None, "total": total}


def write_queue(bundle: dict) -> dict:
    doc = bundle["queue_doc"]
    ssot = bundle["ssot"]
    total = bundle["total"]
    QUEUE_SSOT.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_SSOT.write_text(json.dumps(ssot, indent=2) + "\n", encoding="utf-8")
    SINA.mkdir(parents=True, exist_ok=True)
    QUEUE_HOME.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    if QUEUE_REPO.parent.is_dir():
        QUEUE_REPO.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    STATE_HOME.write_text(
        json.dumps(
            {
                "next_pos": 1,
                "queue_exhausted": total == 0,
                "last_advanced_at": _now(),
                "last_completed_pos": 0,
                "reset_by": "plans_unified_queue_assign_v1",
                "phase": PHASE,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"ok": True, "total": total, "sa_range": ssot.get("sa_range"), "ssot": str(QUEUE_SSOT)}


def deliver_head(bundle: dict) -> dict:
    head = bundle.get("head")
    if not head:
        from worker_inject_lib import clear_inbox  # noqa: WPS433

        clear_inbox(reason="unified_plans_empty")
        return {"ok": False, "error": "empty_queue"}
    from worker_inject_lib import deliver_to_worker_inbox  # noqa: WPS433

    meta = {
        "sa_id": head["sa_id"],
        "queue_role": head["queue_role"],
        "queue_pos": head["queue_pos"],
        "queue_total": bundle["total"],
        "queue_exhausted": False,
        "phase": PHASE,
        "upgrade_id": head.get("upgrade_id"),
        "plan_source": head.get("plan_source"),
    }
    return deliver_to_worker_inbox(
        head["instruction"],
        source="plans_unified_queue_assign",
        meta=meta,
        mark_pending=True,
        fast=True,
    )


def sync_truth() -> dict:
    try:
        from queue_ssot_unify_v1 import unify_queue_ssot  # noqa: WPS433

        return unify_queue_ssot(write_brain=True, rebuild_factory=True, fast=True)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Unified plans → Worker queue + INBOX")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-upgrade", action="store_true", help="Skip plans_unified_upgrade tick")
    ap.add_argument("--deliver-first", action="store_true")
    ap.add_argument("--sync", action="store_true")
    ap.add_argument(
        "--include-brain",
        action="store_true",
        help="Include brain_reasoning items (default: worker-eligible only)",
    )
    args = ap.parse_args()

    upgrade_row: dict = {"skipped": True}
    if not args.skip_upgrade:
        from plans_unified_upgrade_v1 import run_upgrade  # noqa: WPS433

        upgrade_row = run_upgrade(write=True)

    bundle = build_assignment(
        items=collect_all_items(worker_only=not args.include_brain),
    )
    if args.dry_run:
        out = {
            "dry_run": True,
            "upgrade": upgrade_row.get("plans_unified_line"),
            "total": bundle["total"],
            "head_sa": (bundle.get("head") or {}).get("sa_id"),
            "head_id": (bundle.get("head") or {}).get("upgrade_id"),
        }
        print(json.dumps(out, indent=2) if args.json else str(out))
        return 0

    write_row = write_queue(bundle)
    deliver_row = deliver_head(bundle) if args.deliver_first else {"skipped": True}
    sync_row = sync_truth() if args.sync or args.deliver_first else {"skipped": True}
    out = {
        "ok": bool(write_row.get("ok")),
        "upgrade": upgrade_row,
        "assign": write_row,
        "deliver": deliver_row,
        "sync": sync_row,
        "head": {
            "sa_id": (bundle.get("head") or {}).get("sa_id"),
            "upgrade_id": (bundle.get("head") or {}).get("upgrade_id"),
            "plan": (bundle.get("head") or {}).get("plan_source"),
        },
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(
            f"OK: unified queue {write_row['total']} items · "
            f"sa {write_row['sa_range'][0]}–{write_row['sa_range'][-1]} · "
            f"inbox pending={deliver_row.get('pending', deliver_row.get('ok'))}"
        )
    return 0 if write_row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
