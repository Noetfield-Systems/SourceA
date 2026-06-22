#!/usr/bin/env python3
"""Task / plan validation — always-on for SourceA agents + NEXT TASK trigger.

SSOT: data/sourcea-next-task-trigger-v1.json v2.0.0
Receipt: ~/.sina/next-task-trigger-receipt-v1.json

Every agent discussing ANY task or plan MUST answer:
  1. What is this task?
  2. Benefit + priority
  3. Real-world output type
  4. Usefulness verdict (useful | noise | blocked | needs_founder_answer)
  5. Proceed? (yes | no | wait | ask_founder)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data/sourcea-next-task-trigger-v1.json"
RECEIPT = SINA / "next-task-trigger-receipt-v1.json"
ALWAYS_FLAG = SINA / "task-plan-validation-always-v1.flag"
TRIGGER_FLAG = SINA / "next-task-trigger-active-v1.flag"
DRAIN_SSOT = ROOT / "data/secondary-cloud-drain-next-100-v1.json"
BRAIN_PLAN = ROOT / "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _read_ssot() -> dict:
    return _read(SSOT)


def _matches_trigger(text: str, phrases: list[str]) -> bool:
    t = (text or "").lower()
    for p in phrases:
        if p.lower() in t:
            return True
    return bool(re.search(r"\bnext\s+task\b", t, re.I))


def detect_task_plan_topic(text: str) -> bool:
    if not (text or "").strip():
        return False
    ssot = _read_ssot()
    t = text.lower()
    for pat in ssot.get("task_plan_topic_patterns") or []:
        if pat.lower() in t:
            return True
    if re.search(r"\bB\d{4}\b", text, re.I):
        return True
    if re.search(r"\bsa-mkt-\d+\b", text, re.I):
        return True
    if re.search(r"\bCLOUD-SEC-\d+\b", text, re.I):
        return True
    if re.search(r"\bsa-\d{4}\b", text, re.I):
        return True
    if re.search(r"\b(next task|work order|backlog|roadmap|upgrade plan|cloud drain|real-world output)\b", t):
        return True
    if re.search(r"\b(task|plan)\b", t) and re.search(r"\b(execute|proceed|finish|useful|noise|blocked|priority)\b", t):
        return True
    return False


def _extract_ids(text: str) -> dict[str, list[str]]:
    return {
        "brain": list(dict.fromkeys(re.findall(r"\bB(\d{4})\b", text, re.I))),
        "sa_mkt": list(dict.fromkeys(re.findall(r"\bsa-mkt-(\d+)\b", text, re.I))),
        "cloud_sec": list(dict.fromkeys(re.findall(r"\bCLOUD-SEC-(\d+)\b", text, re.I))),
        "sa": list(dict.fromkeys(re.findall(r"\bsa-(\d{4})\b", text, re.I))),
    }


def _find_brain(plan: dict, brain_id: str) -> dict | None:
    bid = brain_id if brain_id.startswith("B") else f"B{brain_id.zfill(4)}"
    for u in plan.get("upgrades") or []:
        if str(u.get("id") or "").upper() == bid.upper():
            return u
    return None


def _find_cloud(drain: dict, *, cloud_id: str = "", registry: str = "") -> dict | None:
    for row in drain.get("plans") or []:
        if cloud_id and str(row.get("id") or "") == cloud_id:
            return row
        if registry and str(row.get("maps_registry") or "") == registry:
            return row
    return None


def _next_brain_upgrade(plan: dict) -> dict | None:
    for u in plan.get("upgrades") or []:
        if str(u.get("status") or "") in ("planned", "pending", "open"):
            return u
    return None


def _next_cloud_drain(obs: dict, drain: dict) -> dict | None:
    head = str(obs.get("cloud_drain_head") or "CLOUD-SEC-001")
    plans = drain.get("plans") or []
    ids = [str(p.get("id") or "") for p in plans if str(p.get("id", "")).startswith("CLOUD-SEC-")]
    if head in ids:
        idx = ids.index(head)
        if idx + 1 < len(ids):
            nxt = ids[idx + 1]
            return next((p for p in plans if p.get("id") == nxt), None)
    return next((p for p in plans if p.get("id") == head), None)


def resolve_task_context(
    *,
    founder_text: str = "",
    task_id: str = "",
    plan_id: str = "",
    prefer_disk_next: bool = False,
) -> dict[str, Any]:
    blob = f"{founder_text} {task_id} {plan_id}".strip()
    ids = _extract_ids(blob)
    plan = _read(BRAIN_PLAN)
    drain = _read(DRAIN_SSOT)
    brain_row: dict | None = None
    cloud_row: dict | None = None
    source = "disk_next"

    if ids["brain"]:
        brain_row = _find_brain(plan, ids["brain"][0])
        source = "explicit_brain_id"
    if ids["cloud_sec"]:
        cloud_row = _find_cloud(drain, cloud_id=f"CLOUD-SEC-{ids['cloud_sec'][0].zfill(3)}")
        source = "explicit_cloud_id"
    if ids["sa_mkt"]:
        cloud_row = cloud_row or _find_cloud(drain, registry=f"sa-mkt-{ids['sa_mkt'][0].zfill(4)}")
        source = "explicit_registry_id"
    if task_id:
        tid = task_id.strip()
        if tid.upper().startswith("B"):
            brain_row = brain_row or _find_brain(plan, tid)
            source = "cli_task_id"
        elif tid.startswith("CLOUD-SEC"):
            cloud_row = cloud_row or _find_cloud(drain, cloud_id=tid)
            source = "cli_task_id"
        elif tid.startswith("sa-"):
            cloud_row = cloud_row or _find_cloud(drain, registry=tid)
            source = "cli_task_id"
    if plan_id:
        cloud_row = cloud_row or _find_cloud(drain, registry=plan_id.strip())
        source = "cli_plan_id"

    if prefer_disk_next or (not brain_row and not cloud_row):
        brain_row = brain_row or _next_brain_upgrade(plan)
        obs = _read(SINA / "phase-observed-v1.json")
        cloud_row = cloud_row or _next_cloud_drain(obs, drain)
        if source == "disk_next" and (brain_row or cloud_row):
            source = "disk_next"

    sa_row: dict | None = None
    reg = str((cloud_row or {}).get("maps_registry") or plan_id or "")
    if reg.startswith("sa-mkt-"):
        sa_row = {"id": reg, "source": "drain_ssot"}

    title = str((brain_row or {}).get("title") or (cloud_row or {}).get("cloud_action") or (cloud_row or {}).get("title") or "")
    action = str((cloud_row or {}).get("cloud_action") or (brain_row or {}).get("acceptance") or title)

    return {
        "source": source,
        "brain": brain_row,
        "cloud": cloud_row,
        "sa_plan": sa_row,
        "task_label": _task_label(brain_row, cloud_row),
        "title": title,
        "action": action,
    }


def _task_label(brain: dict | None, cloud: dict | None) -> str:
    parts: list[str] = []
    if brain:
        parts.append(str(brain.get("id") or ""))
    if cloud:
        parts.append(str(cloud.get("id") or ""))
        if cloud.get("maps_registry"):
            parts.append(str(cloud["maps_registry"]))
    return " · ".join(p for p in parts if p) or "unresolved"


def _classify_output(*, action: str, title: str, tier: str, lane: str = "") -> str:
    blob = f"{action} {title} {lane}".lower()
    if any(x in blob for x in ("hub ux", "preview", "deploy preview", "onboarding", "landing", "saas", "agent product")):
        return "ai_agent_product"
    if any(x in blob for x in ("marketing", "gtm", "copy", "price card", "plg", "outreach", "demo")):
        return "marketing_system"
    if any(x in blob for x in ("fetch", "evidence", "row", "json", "pipeline", "ledger", "supabase", "labs")):
        return "data_pipeline"
    if any(x in blob for x in ("receipt", "validate", "pass/fail", "theater", "brain maps", "cites disk", "governance meta")):
        return "internal_meta"
    if any(x in blob for x in ("write", "generate", "file", "manifest", "schema", ".md", ".json")):
        return "file_generation"
    if tier in ("T1", "T2", "T3") and "cloud" in blob:
        return "ai_agent_product"
    return "unknown"


def _usefulness(*, output_type: str, blocked: list[str], meta_only: bool) -> str:
    if blocked:
        return "blocked"
    if output_type == "internal_meta" and meta_only:
        return "noise"
    if output_type in ("data_pipeline", "ai_agent_product", "marketing_system", "file_generation"):
        return "useful"
    if output_type == "internal_meta":
        return "needs_founder_answer"
    return "needs_founder_answer"


def _disk_snapshot() -> dict:
    obs = _read(SINA / "phase-observed-v1.json")
    assignment = _read(ROOT / "data/sourcea-worker-professional-assignment-v1.json")
    active = assignment.get("active") or {}
    surfaces = _read(SINA / "agent-live-surfaces-v1.json")
    loop_cfg = _read(SINA / "loop-specialist-config-v1.json")
    plan = _read(BRAIN_PLAN)
    blocked: list[str] = []
    fn = _read(SINA / "factory-now-v1.json")
    if str(fn.get("mode") or "").upper() == "FREEZE":
        blocked.append("factory_FREEZE")
    return {
        "era": obs.get("era"),
        "cloud_drain_head": obs.get("cloud_drain_head"),
        "cloud_drain_last_completed": obs.get("cloud_drain_last_completed"),
        "desired_start_plan": active.get("start_plan"),
        "factory_now_line": surfaces.get("factory_now_line") or "",
        "factory_mode": fn.get("mode"),
        "loop_auto": bool(loop_cfg.get("loop_auto_dispatch_enabled")),
        "brain_done": (plan.get("progress") or {}).get("done"),
        "cloud_proven": sum(1 for u in (plan.get("upgrades") or []) if u.get("cloud_proof")),
        "blocked": blocked,
    }


def build_pipeline(ssot: dict, snap: dict, ctx: dict[str, Any]) -> dict[str, Any]:
    brain = ctx.get("brain") or {}
    cloud = ctx.get("cloud") or {}
    brain_id = str(brain.get("id") or "")
    cloud_id = str(cloud.get("id") or snap.get("cloud_drain_head") or "")
    registry = str(cloud.get("maps_registry") or (ctx.get("sa_plan") or {}).get("id") or "")
    action = str(ctx.get("action") or "")
    title = str(ctx.get("title") or "")
    lane = str(brain.get("lane") or cloud.get("workstream") or "")

    output_type = _classify_output(
        action=action,
        title=title,
        tier=str(cloud.get("tier") or brain.get("tier") or ""),
        lane=lane,
    )
    meta_only = output_type == "internal_meta" and not registry
    verdict = _usefulness(output_type=output_type, blocked=snap.get("blocked") or [], meta_only=meta_only)

    priority = ssot.get("priority_stack") or []
    priority_label = ""
    priority_id = ""
    try:
        sys.path.insert(0, str(SCRIPTS))
        from task_plan_priority_v1 import priority_for_task_id  # noqa: WPS433

        tid = registry or brain_id or cloud_id
        if tid:
            pr = priority_for_task_id(tid)
            priority_label = f"{pr.get('unified_priority')} — {pr.get('priority_label')}"
            priority_id = str(pr.get("unified_priority") or "")
    except Exception:
        pass
    if not priority_label:
        if registry and output_type in ("data_pipeline", "ai_agent_product", "marketing_system"):
            priority_label = "P1 — Cloud FORGE / product output"
        elif meta_only and verdict == "noise":
            priority_label = "P4 — internal meta (subordinate to buyer-visible output)"
        elif snap.get("blocked"):
            priority_label = "blocked — resolve factory/loop blockers first"
        elif output_type == "marketing_system":
            priority_label = "P3 — TrustField / GTM lane"
        else:
            priority_label = str(priority[1].get("label") if len(priority) > 1 else "P1")

    task_parts = [f"Task: {ctx.get('task_label')}"]
    if title:
        task_parts.append(title[:160])
    if action and action != title:
        task_parts.append(action[:120])
    what_is_task = " · ".join(task_parts)

    benefit = (
        f"Priority: {priority_label}. "
        f"Benefit: ties work to north-star traction — buyer-visible or data product output, not receipt theater."
    )
    if verdict == "noise":
        benefit = (
            f"Priority: {priority_label}. "
            f"Benefit: low alone — internal discipline row; pair with cloud/product plan for real output."
        )

    real_world = {
        "question": ssot.get("required_founder_question"),
        "classified_as": output_type,
        "examples_map": {
            "file_generation": "manifest, schema, doc, receipt pack logged",
            "marketing_system": "landing, pricing, GTM, outreach asset",
            "ai_agent_product": "Hub UX, FORGE preview URL, controlled agent surface",
            "data_pipeline": "labs row, competitor fetch, evidence store",
            "internal_meta": "brain/governance receipt only — no buyer artifact",
            "unknown": "founder must classify before proceed",
        },
        "this_task_delivers": action or title or "unspecified — ask founder",
    }

    proceed = "yes" if verdict == "useful" and not snap.get("blocked") else (
        "no" if verdict == "noise" else ("wait" if verdict == "blocked" else "ask_founder")
    )

    return {
        "what_is_task": what_is_task,
        "benefit_and_priority": benefit,
        "real_world_output": real_world,
        "output_type": output_type,
        "usefulness_verdict": verdict,
        "proceed": proceed,
        "task_ids": {
            "brain_upgrade_id": brain_id or None,
            "cloud_plan_id": cloud_id or None,
            "registry_plan_id": registry or None,
            "resolution_source": ctx.get("source"),
            "unified_priority": priority_id or None,
        },
        "paired_recommendation": _recommendation(registry, brain_id, verdict, proceed),
    }


def _recommendation(registry: str, brain_id: str, verdict: str, proceed: str) -> str:
    if verdict == "noise":
        return f"Do not execute {brain_id or 'meta row'} alone — pair with product/cloud plan or skip"
    if registry and proceed in ("yes", "ask_founder"):
        return (
            "Hub Proceed only — POST /api/cloud-drain/proceed/v1 or Worker Hub · Proceed next cloud task · "
            f"cloud runs {registry} · OpenRouter/Gemini on Railway · no Mac forge dispatch"
        )
    if verdict == "blocked":
        return "Wait for FREEZE/loop clearance · then Hub Proceed button (not local agent dispatch)"
    return "Classify real-world output with founder · then Hub Proceed when useful"


def _summary_line(pipeline: dict, snap: dict) -> str:
    ids = pipeline.get("task_ids") or {}
    return (
        f"task-plan-validate · {ids.get('resolution_source')} · "
        f"output={pipeline.get('output_type')} · verdict={pipeline.get('usefulness_verdict')} · "
        f"proceed={pipeline.get('proceed')} · head={snap.get('cloud_drain_head')}"
    )


def _write_receipt(row: dict) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    ALWAYS_FLAG.write_text(f"always_apply=true\nat={row['at']}\n", encoding="utf-8")
    if row.get("triggered"):
        TRIGGER_FLAG.write_text(f"activated_at={row['at']}\n", encoding="utf-8")


def refresh_baseline(
    *,
    founder_text: str = "",
    task_id: str = "",
    plan_id: str = "",
    write: bool = True,
) -> dict:
    ssot = _read_ssot()
    snap = _disk_snapshot()
    prefer_next = not (task_id or plan_id or _extract_ids(founder_text)["brain"] or _extract_ids(founder_text)["sa_mkt"])
    ctx = resolve_task_context(
        founder_text=founder_text,
        task_id=task_id,
        plan_id=plan_id,
        prefer_disk_next=prefer_next,
    )
    pipeline = build_pipeline(ssot, snap, ctx)
    triggered = _matches_trigger(founder_text, ssot.get("trigger_phrases") or []) if founder_text else False
    row = {
        "schema": "next-task-trigger-receipt-v1",
        "version": ssot.get("version", "2.0.0"),
        "at": _now(),
        "ok": True,
        "always_apply": bool(ssot.get("always_apply", True)),
        "triggered": triggered,
        "mode": "TASK_PLAN_VALIDATE_ALWAYS",
        "task_context": ctx,
        "pipeline": pipeline,
        "disk_snapshot": snap,
        "forbidden": ssot.get("forbidden_always") or [],
        "next_task_line": _summary_line(pipeline, snap),
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if write:
        _write_receipt(row)
    return row


def activate(*, founder_text: str = "", task_id: str = "", plan_id: str = "", write: bool = True) -> dict:
    row = refresh_baseline(founder_text=founder_text, task_id=task_id, plan_id=plan_id, write=write)
    row["mode"] = "VALIDATE_THEN_PROCEED" if row.get("triggered") else row["mode"]
    if write:
        _write_receipt(row)
    return row


def inject_slice() -> dict:
    ssot = _read_ssot()
    row = _read(RECEIPT) if RECEIPT.is_file() else refresh_baseline(write=False)
    return {
        "always_apply": bool(ssot.get("always_apply", True)),
        "trigger_phrases": ssot.get("trigger_phrases") or [],
        "task_plan_topic_patterns": ssot.get("task_plan_topic_patterns") or [],
        "one_law": ssot.get("one_law"),
        "required_founder_question": ssot.get("required_founder_question"),
        "pipeline_fields": (ssot.get("pipeline") or {}).get("required_fields") or [],
        "reply_sections": (ssot.get("pipeline") or {}).get("reply_sections") or [],
        "command_refresh": "python3 scripts/next_task_trigger_v1.py --refresh --json",
        "command_on_trigger": "python3 scripts/next_task_trigger_v1.py --activate --text '<founder message>' --json",
        "baseline_pipeline": row.get("pipeline"),
        "next_task_line": row.get("next_task_line"),
        "ssot": str(SSOT.relative_to(ROOT)),
    }


def validate_reply_text(text: str) -> dict:
    t = (text or "").lower()
    checks = {
        "what_is_task": any(
            x in t
            for x in (
                "what is this task",
                "what is the task",
                "### what is",
                "**what is this task",
                "this task:",
            )
        ),
        "benefit": any(x in t for x in ("benefit", "priority", "p0", "p1", "because", "### benefit")),
        "real_world_output": any(
            x in t
            for x in ("real-world", "real world", "real-world output", "output type", "### real-world")
        ),
        "verdict": any(
            x in t
            for x in ("usefulness verdict", "useful", "noise", "blocked", "needs_founder", "### usefulness")
        ),
        "proceed": any(x in t for x in ("proceed?", "proceed:", "proceed =", "### proceed")),
        "output_type_named": any(
            x in t
            for x in (
                "file_generation",
                "marketing_system",
                "ai_agent_product",
                "data_pipeline",
                "internal_meta",
                "data pipeline",
                "ai agent product",
            )
        ),
    }
    score = sum(1 for v in checks.values() if v)
    ok = score >= 4 and checks["what_is_task"] and checks["verdict"]
    return {"ok": ok, "checks": checks, "score": score, "min_required": 4}


def reply_template(pipeline: dict | None = None) -> str:
    p = pipeline or (_read(RECEIPT).get("pipeline") or {})
    return (
        "### What is this task?\n"
        f"{p.get('what_is_task', '[task from disk]')}\n\n"
        "### Benefit and priority\n"
        f"{p.get('benefit_and_priority', '[priority stack]')}\n\n"
        "### Real-world output\n"
        f"Type: {p.get('output_type', 'unknown')}\n\n"
        "### Usefulness verdict\n"
        f"{p.get('usefulness_verdict', 'needs_founder_answer')}\n\n"
        "### Proceed?\n"
        f"{p.get('proceed', 'ask_founder')}\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Task/plan validation — always-on + NEXT TASK trigger v2")
    ap.add_argument("--text", default="", help="Founder message")
    ap.add_argument("--task-id", default="", help="B0006 · CLOUD-SEC-003 · sa-mkt-0003 · sa-1201")
    ap.add_argument("--plan-id", default="", help="Registry plan id")
    ap.add_argument("--refresh", action="store_true", help="Session baseline (always_apply)")
    ap.add_argument("--activate", action="store_true", help="Refresh + mark trigger")
    ap.add_argument("--inject", action="store_true")
    ap.add_argument("--template", action="store_true")
    ap.add_argument("--detect-topic", default="")
    ap.add_argument("--validate-reply", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.validate_reply:
        row = validate_reply_text(args.validate_reply)
    elif args.detect_topic:
        row = {"ok": True, "topic": detect_task_plan_topic(args.detect_topic)}
    elif args.template:
        base = _read(RECEIPT)
        row = {"ok": True, "template": reply_template(base.get("pipeline"))}
    elif args.inject:
        row = inject_slice()
    elif args.refresh:
        row = refresh_baseline(founder_text=args.text, task_id=args.task_id, plan_id=args.plan_id, write=True)
    elif args.activate or _matches_trigger(args.text, _read_ssot().get("trigger_phrases") or []):
        row = activate(founder_text=args.text, task_id=args.task_id, plan_id=args.plan_id, write=True)
    else:
        row = refresh_baseline(founder_text=args.text, task_id=args.task_id, plan_id=args.plan_id, write=False)
        row["triggered"] = False
        row["note"] = "no trigger — use --refresh or discuss task/plan with pipeline sections"

    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("next_task_line") or row.get("template") or row.get("note") or json.dumps(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
