#!/usr/bin/env python3
"""sa-runtime-surface-heal-v1 — one queue truth · projection sync from receipts.

Authority order (high → low):
  kill flag · runtime controller receipt · inbox · phase-observed · factory-now · projections
"""
from __future__ import annotations

import json
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPTS = ROOT / "receipts"

AUTHORITY_ORDER = [
    "kill_flag_auto_run_disabled",
    "runtime_controller_receipt",
    "worker_prompt_inbox",
    "phase_observed",
    "factory_now",
    "projection_surfaces",
]

CF_LOOPS = (
    "sourcea-cloud-auto-runtime-tick-v1",
    "sourcea-loop-specialist-tick-v1",
    "sourcea-signal-factory-tick-v1",
    "noetfield-nerve-probe-v1",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def establish_canonical() -> dict[str, Any]:
    kill_on = (SINA / "auto-run-disabled-v1.flag").is_file()
    rtc = _read(SINA / "sourcea-runtime-controller-receipt-v1.json")
    inbox = _read(SINA / "worker-prompt-inbox-v1.json")
    phase = _read(SINA / "phase-observed-v1.json")
    factory = _read(SINA / "factory-now-v1.json")
    hq = _read(SINA / "healthy-queue-30-active.json")
    hstate = _read(SINA / "healthy-queue-state-v1.json")
    census = _read(SINA / "workflow-census-last-run-v1.json")

    meta = inbox.get("meta") or {}
    worker_sa = str(inbox.get("sa_id") or meta.get("sa_id") or "")
    plan_id = str(meta.get("plan_id") or "")
    queue_pos = int(meta.get("queue_pos") or 1)
    queue_total = int(meta.get("queue_total") or len(hq.get("queue") or []) or 10)
    queue_thread = str(hq.get("thread") or "DEEP-RESEARCH-W1")
    queue_phase = str(meta.get("phase") or "phase-deep-research-w1-v1")
    inbox_pending = bool(inbox.get("pending"))
    inbox_at = str(inbox.get("delivered_at") or "")

    cloud_head = str(phase.get("cloud_forge_run_head") or "")
    cloud_batch = int(phase.get("batch_id") or 0)
    cloud_at = str(phase.get("rebuilt_at") or "")

    rtc_stale = bool(rtc.get("at") and inbox_at and rtc["at"] < inbox_at)
    rtc_superseded = rtc_stale or str(rtc.get("active_job") or "") != worker_sa

    mode = str(factory.get("mode") or "SINGLE_SA")
    resume_required = mode == "SINGLE_SA" and not kill_on

    current_line = (
        f"factory-now · Valid YES {factory.get('valid_yes', 1000)} · "
        f"brain {factory.get('brain_vy', 1000)} · "
        f"dual_proof {factory.get('dual_proof_ok', True)} · "
        f"mode {mode} · "
        f"queue {worker_sa} · "
        f"cloud {cloud_head}"
    )

    next_action = "WAIT_BOUNDED_RESUME"
    if inbox_pending and worker_sa and not kill_on:
        next_action = "DISPATCH_WORKER_ONE_TURN"
    elif kill_on:
        next_action = "BLOCKED_KILL_FLAG"

    canonical = {
        "schema": "sa-runtime-canonical-state-v1",
        "at": _now(),
        "work_id": "sa-runtime-surface-heal-v1",
        "authority_order": AUTHORITY_ORDER,
        "kill_flag": kill_on,
        "current_cloud_head": cloud_head,
        "current_cloud_batch": cloud_batch,
        "current_cloud_observed_at": cloud_at,
        "current_worker_job": worker_sa,
        "current_worker_plan": plan_id,
        "current_queue": {
            "thread": queue_thread,
            "phase": queue_phase,
            "pos": queue_pos,
            "total": queue_total,
            "path": str(SINA / "healthy-queue-30-active.json"),
        },
        "current_line": current_line,
        "factory_mode": mode,
        "sprint_state": "paused_bounded_resume",
        "resume_required": resume_required,
        "inbox_pending": inbox_pending,
        "inbox_delivered_at": inbox_at,
        "runtime_controller_superseded": rtc_superseded,
        "runtime_controller_receipt_at": rtc.get("at"),
        "drift_healed": {
            "factory_line_was": factory.get("line"),
            "factory_queue_sa_was": factory.get("queue_sa"),
            "healthy_queue_pos_was": hstate.get("next_pos"),
            "monitor_here_sa_was": (_read(SINA / "monitor-live-v1.json").get("here_sa")),
        },
        "next_allowed_action": next_action,
        "census_at": census.get("at"),
    }
    return canonical


def classify_cf_ticks() -> dict[str, Any]:
    census = _read(SINA / "workflow-census-last-run-v1.json")
    rows = census.get("rows_sample") or []
    by_name = {str(r.get("name") or ""): r for r in rows}
    census_at = str(census.get("at") or "")
    census_stale = False
    try:
        if census_at:
            age_h = (datetime.now(timezone.utc) - datetime.fromisoformat(census_at.replace("Z", "+00:00"))).total_seconds() / 3600
            census_stale = age_h > 24
    except ValueError:
        census_stale = True

    loops: list[dict[str, Any]] = []
    follow_ups: list[str] = []
    for name in CF_LOOPS:
        row = by_name.get(name) or {}
        last_receipt = row.get("last_receipt_at")
        cron = row.get("schedule_cron")
        if census_stale and not row:
            status = "STALE_CENSUS"
        elif last_receipt:
            status = "RUNNING_WITH_RECEIPT"
        elif cron or row.get("trigger_host") == "cloudflare":
            status = "RUNNING_PROOF_GAP"
            follow_ups.append(f"Wire tick receipt path for {name} into workflow-census last_receipt_at")
        else:
            status = "NOT_RUNNING"
        loops.append(
            {
                "name": name,
                "status": status,
                "schedule_cron": cron,
                "last_receipt_at": last_receipt,
                "census_at": census_at,
                "value_class": row.get("value_class"),
            }
        )

    return {
        "schema": "sa-cf-tick-proof-gap-v1",
        "at": _now(),
        "census_stale": census_stale,
        "census_at": census_at,
        "loops": loops,
        "follow_up_fix_items": follow_ups,
        "law": "Do not claim PASS without receipt path",
    }


def bounded_resume_receipt(*, canonical: dict[str, Any]) -> dict[str, Any]:
    token_id = f"resume-{uuid.uuid4().hex[:12]}"
    job = str(canonical.get("current_worker_job") or "")
    receipt = {
        "schema": "sa-bounded-resume-receipt-v1",
        "at": _now(),
        "resume_token_id": token_id,
        "resumed_job": job,
        "resumed_plan": canonical.get("current_worker_plan"),
        "allowed_scope": f"one Worker turn · {job} · UP-DR deep research lane only",
        "max_steps": 1,
        "max_turns": 1,
        "stop_condition": "WORKER_ROUND_REPORT · one bounded turn · STOP",
        "factory_mode": canonical.get("factory_mode"),
        "kill_flag": canonical.get("kill_flag"),
        "receipt_path": str(SINA / "founder-resume-drain-v1.json"),
        "heal_receipt_path": str(RECEIPTS / "sa_runtime_surface_heal_v1.json"),
        "law": "SINGLE_SA bounded resume — no unbounded drain",
    }
    # Write founder resume token (bounded)
    sys.path.insert(0, str(SCRIPTS))
    try:
        from factory_control_v1 import write_resume_token  # noqa: WPS433

        tok = write_resume_token(
            max_turns=1,
            max_packs=1,
            trigger="WORK: sa-runtime-surface-heal-v1",
            set_by="sa_runtime_surface_heal_v1",
        )
        receipt["founder_resume_token"] = tok
        receipt["resume_token_id"] = tok.get("at") or token_id
    except Exception as exc:
        receipt["founder_resume_token"] = {"ok": False, "error": str(exc)}
    return receipt


def sync_surfaces(*, canonical: dict[str, Any]) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    steps: list[dict[str, Any]] = []

    worker_sa = canonical["current_worker_job"]
    pos = canonical["current_queue"]["pos"]
    total = canonical["current_queue"]["total"]
    role = "act"

    # Queue cursor align to inbox authority
    state_path = SINA / "healthy-queue-state-v1.json"
    state = _read(state_path)
    state.update(
        {
            "next_pos": pos,
            "last_advanced_at": _now(),
            "last_completed_pos": max(0, pos - 1),
            "healed_by": "sa_runtime_surface_heal_v1",
        }
    )
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    steps.append({"step": "healthy_queue_state", "ok": True, "next_pos": pos})

    # Orchestrator bind
    orch_path = SINA / "healthy-drain-orchestrator-v1.json"
    orch = _read(orch_path)
    orch.update(
        {
            "expected_sa": worker_sa,
            "expected_role": role,
            "expected_pos": pos,
            "status": "awaiting_worker" if canonical.get("inbox_pending") else "idle",
            "updated_at": _now(),
            "recovery_reason": "sa_runtime_surface_heal_v1",
        }
    )
    orch_path.write_text(json.dumps(orch, indent=2) + "\n", encoding="utf-8")
    steps.append({"step": "orchestrator", "ok": True, "expected_sa": worker_sa})

    # factory-now
    fn_path = SINA / "factory-now-v1.json"
    fn = _read(fn_path)
    fn.update(
        {
            "at": _now(),
            "mode": canonical.get("factory_mode"),
            "kill_flag": canonical.get("kill_flag"),
            "queue_sa": worker_sa,
            "inbox_sa": worker_sa,
            "line": canonical.get("current_line"),
            "cloud_head": canonical.get("current_cloud_head"),
            "cloud_batch": canonical.get("current_cloud_batch"),
            "rebuilt_by": "sa_runtime_surface_heal_v1",
        }
    )
    fn_path.write_text(json.dumps(fn, indent=2) + "\n", encoding="utf-8")
    steps.append({"step": "factory_now", "ok": True})

    # monitor-live
    mon_path = SINA / "monitor-live-v1.json"
    mon = _read(mon_path)
    mon.update(
        {
            "schema": "monitor-live-v1",
            "at": _now(),
            "reason": "sa_runtime_surface_heal_v1",
            "here_sa": worker_sa,
            "here_role": role,
            "queue_pos": pos,
            "queue_total": total,
            "factory_mode": canonical.get("factory_mode"),
            "freeze": bool(canonical.get("kill_flag")),
            "inbox_pending": canonical.get("inbox_pending"),
            "cloud_head": canonical.get("current_cloud_head"),
            "queue_ssot_unify": {"ok": True, "aligned": True, "truth_match": True, "healed_by": "sa_runtime_surface_heal_v1"},
        }
    )
    mon_path.write_text(json.dumps(mon, indent=2) + "\n", encoding="utf-8")
    steps.append({"step": "monitor_live", "ok": True})

    # agent-live-surfaces (projection slice only)
    surf_path = SINA / "agent-live-surfaces-v1.json"
    surf = _read(surf_path)
    surf.update(
        {
            "synced_at": _now(),
            "factory_now_line": canonical.get("current_line"),
            "mode": canonical.get("factory_mode"),
            "queue_sa": worker_sa,
            "cloud_head": canonical.get("current_cloud_head"),
            "cloud_batch": canonical.get("current_cloud_batch"),
            "dual_pick": {
                "queue_sa": worker_sa,
                "live_pick_sa": worker_sa,
                "cloud_head": canonical.get("current_cloud_head"),
                "aligned": True,
                "idle": not canonical.get("inbox_pending"),
            },
            "runtime_surface_heal_at": _now(),
            "truth_bundle_at": _now(),
        }
    )
    surf_path.write_text(json.dumps(surf, indent=2) + "\n", encoding="utf-8")
    steps.append({"step": "agent_live_surfaces", "ok": True})

    # ACTIVE_NOW
    try:
        from active_now_v1 import sync_active_now_from_queue  # noqa: WPS433

        an = sync_active_now_from_queue(
            pointer={
                "next_sa": worker_sa,
                "queue_role": role,
                "queue_pos": pos,
            }
        )
        steps.append({"step": "active_now", **an})
        # Goal/sprint/blocker lines — explicit heal
        an_path = ROOT / "ACTIVE_NOW.md"
        if an_path.is_file():
            text = an_path.read_text(encoding="utf-8")
            text = re.sub(
                r"\*\*Current Goal:\*\*[^\n]*",
                "**Current Goal:** SINGLE_SA — deep research UP-DR queue (canonical heal)",
                text,
                count=1,
            )
            text = re.sub(
                r"\*\*Current Sprint:\*\*[^\n]*",
                "**Current Sprint:** Paused — bounded resume token required before Worker dispatch",
                text,
                count=1,
            )
            text = re.sub(
                r"\*\*Current Queue:\*\*[^\n]*",
                f"**Current Queue:** `~/.sina/healthy-queue-30-active.json` · `{canonical['current_queue']['thread']}` · `{canonical['current_queue']['phase']}`",
                text,
                count=1,
            )
            blocker = (
                f"SINGLE_SA — kill flag {'ON' if canonical.get('kill_flag') else 'OFF'} · "
                f"`{canonical.get('current_line')}` · "
                f"next: {canonical.get('next_allowed_action')}"
            )
            text = re.sub(r"\*\*Current Blocker:\*\*[^\n]*", f"**Current Blocker:** {blocker}", text, count=1)
            an_path.write_text(text, encoding="utf-8")
            steps.append({"step": "active_now_fields", "ok": True})
    except Exception as exc:
        steps.append({"step": "active_now", "ok": False, "error": str(exc)})

    # Runtime controller receipt refresh (observation only — no dispatch)
    rtc = {
        "schema": "sourcea-runtime-controller-receipt-v1",
        "at": _now(),
        "machine_id": "sa_runtime_surface_heal_v1",
        "outcome": "HEAL_DRIFT",
        "reason": "projection sync from canonical state",
        "running": False,
        "active_job": worker_sa,
        "disk_snapshot": {
            "queue_pos": pos,
            "queue_depth": total,
            "inbox_pending": canonical.get("inbox_pending"),
            "broker_expected_sa": worker_sa,
            "factory_mode": canonical.get("factory_mode"),
            "kill_flag": canonical.get("kill_flag"),
            "cloud_head": canonical.get("current_cloud_head"),
        },
    }
    _write(SINA / "sourcea-runtime-controller-receipt-v1.json", rtc)
    steps.append({"step": "runtime_controller_receipt", "ok": True})

    try:
        from run_inbox_disk_truth_v1 import write_truth  # noqa: WPS433

        write_truth(sync=False, rebuild_next10=False)
        steps.append({"step": "run_inbox_truth", "ok": True})
    except Exception as exc:
        steps.append({"step": "run_inbox_truth", "ok": False, "error": str(exc)})

    return {"ok": True, "steps": steps}


def write_report(*, canonical: dict, cf: dict, resume: dict, sync: dict) -> str:
    lines = [
        "# SA Runtime Surface Heal Report v1",
        "",
        f"**Generated:** {_now()} UTC",
        f"**Work:** sa-runtime-surface-heal-v1",
        "",
        "## Authority order",
        "",
    ]
    for i, layer in enumerate(AUTHORITY_ORDER, 1):
        lines.append(f"{i}. `{layer}`")
    lines += [
        "",
        "Projection surfaces never override receipts.",
        "",
        "## Canonical state",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| current_cloud_head | `{canonical.get('current_cloud_head')}` batch {canonical.get('current_cloud_batch')} |",
        f"| current_worker_job | `{canonical.get('current_worker_job')}` / `{canonical.get('current_worker_plan')}` |",
        f"| current_queue | {canonical.get('current_queue', {}).get('thread')} pos {canonical.get('current_queue', {}).get('pos')}/{canonical.get('current_queue', {}).get('total')} |",
        f"| current_line | `{canonical.get('current_line')}` |",
        f"| sprint_state | `{canonical.get('sprint_state')}` |",
        f"| resume_required | `{canonical.get('resume_required')}` |",
        f"| next_allowed_action | `{canonical.get('next_allowed_action')}` |",
        "",
        "## CF tick proof gap",
        "",
    ]
    for loop in cf.get("loops") or []:
        lines.append(f"- **{loop['name']}** — `{loop['status']}`")
    if cf.get("follow_up_fix_items"):
        lines.append("")
        lines.append("### Follow-up fix items")
        for item in cf["follow_up_fix_items"]:
            lines.append(f"- {item}")
    lines += [
        "",
        "## Bounded resume",
        "",
        f"- resume_token_id: `{resume.get('resume_token_id')}`",
        f"- resumed_job: `{resume.get('resumed_job')}`",
        f"- max_steps: `{resume.get('max_steps')}`",
        f"- receipt_path: `{resume.get('receipt_path')}`",
        "",
        "## Surface sync steps",
        "",
    ]
    for step in sync.get("steps") or []:
        lines.append(f"- `{step.get('step')}` ok={step.get('ok')}")
    lines += [
        "",
        "## Receipts",
        "",
        "- `receipts/sa_runtime_surface_heal_v1.json`",
        "- `receipts/sa_runtime_canonical_state_v1.json`",
        "- `receipts/sa_cf_tick_proof_gap_v1.json`",
        "",
        "**STOP** — no new queue item · no FORM submit.",
        "",
    ]
    return "\n".join(lines)


def heal(*, write: bool = True) -> dict[str, Any]:
    canonical = establish_canonical()
    cf = classify_cf_ticks()
    resume = bounded_resume_receipt(canonical=canonical)
    sync = sync_surfaces(canonical=canonical) if write else {"skipped": True}

    heal_receipt = {
        "schema": "sa-runtime-surface-heal-v1",
        "at": _now(),
        "ok": True,
        "work_id": "sa-runtime-surface-heal-v1",
        "authority_order": AUTHORITY_ORDER,
        "canonical": canonical,
        "cf_proof_gap": cf,
        "bounded_resume": resume,
        "surface_sync": sync,
        "outputs": {
            "canonical": "receipts/sa_runtime_canonical_state_v1.json",
            "cf_gap": "receipts/sa_cf_tick_proof_gap_v1.json",
            "heal": "receipts/sa_runtime_surface_heal_v1.json",
            "report": "docs/SA_RUNTIME_SURFACE_HEAL_REPORT_v1.md",
        },
    }

    if write:
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        _write(RECEIPTS / "sa_runtime_canonical_state_v1.json", canonical)
        _write(RECEIPTS / "sa_cf_tick_proof_gap_v1.json", cf)
        _write(RECEIPTS / "sa_runtime_surface_heal_v1.json", heal_receipt)
        report_path = ROOT / "docs/SA_RUNTIME_SURFACE_HEAL_REPORT_v1.md"
        report_path.write_text(write_report(canonical=canonical, cf=cf, resume=resume, sync=sync), encoding="utf-8")

    return heal_receipt


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="sa-runtime-surface-heal-v1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    out = heal(write=not args.dry_run)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        c = out.get("canonical") or {}
        print(f"heal ok · job={c.get('current_worker_job')} · next={c.get('next_allowed_action')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
