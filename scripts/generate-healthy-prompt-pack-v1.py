#!/usr/bin/env python3
"""Generate healthy-prompt-pack-100.json + healthy-queue-30-active.json for REGISTRY drain."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "os" / "plan-library" / "sourcea-1000"
OUT_DIR = PACK / "prompts"
REG = PACK / "REGISTRY.json"

MANDATORY = [
    "brain-os/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md",
    "brain-os/enforcement/REGISTRY_DRAIN_RAIL_LOCKED_v1.md",
    "brain-os/system/GOAL_EXECUTION_ACTIVE_LOCKED_v1.md",
    "brain-os/plan-registry/sourcea-1000/HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md",
    "brain-os/plan-registry/sourcea-1000/REGISTRY_DRAIN_PROCESS_LOCKED_v1.md",
    ".cursor/rules/000-entry-gate.mdc",
]

STEP_TYPES = [
    "snapshot",
    "plan",
    "analyze",
    "check",
    "debug",
    "fix",
    "implement",
    "verify_backend",
    "verify_ui",
    "delta",
]

DOMAINS = [
    "eval-dispatch",
    "hub-build-ci",
    "scoreboard-fleet",
    "spine-loop",
    "gates-receipts",
    "hub-ui",
    "governance",
    "ssot-alignment",
    "commercial-lanes",
    "registry-pack",
]

QUEUE_ROLES = ("check", "act", "verify")

ROLE_TO_STEP = {
    "check": "check",
    "act": "implement",
    "verify": "verify_backend",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_registry() -> list[dict]:
    data = json.loads(REG.read_text(encoding="utf-8"))
    return data["plans"]


def _pick_backlog(limit: int) -> list[dict]:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from healthy_queue_blocker_lib import filter_achievable_picks  # noqa: WPS433
    from sourcea_pick_lib import pick_backlog_plans  # noqa: WPS433

    plans = _load_registry()
    raw = pick_backlog_plans(
        plans, tiers=["T0", "T1", "T2", "T3"], limit=limit * 3, order="phase-first"
    )
    achievable, blocked = filter_achievable_picks(raw)
    if blocked and len(achievable) < limit:
        # Pull more backlog rows skipping live-eval-dependent sa when OpenRouter blocked.
        # Use a large limit to reach deeper tiers (s3-T2, s4-T2) that don't require live eval.
        # Explicitly exclude commercial phase (sa-050x) — GOAL_HIERARCHY_LOCKED T5 never default.
        seen = {p["id"] for p in achievable}
        from healthy_queue_blocker_lib import sa_requires_live_eval  # noqa: WPS433
        COMMERCIAL_PHASE = "phase-s5-commercial-lanes"
        for p in pick_backlog_plans(
            plans, tiers=["T0", "T1", "T2", "T3"], limit=limit * 30, order="phase-first"
        ):
            if p["id"] in seen:
                continue
            if p.get("phase") == COMMERCIAL_PHASE or (p.get("id") or "").startswith("sa-05"):
                continue
            if sa_requires_live_eval(p):
                continue
            achievable.append(p)
            seen.add(p["id"])
            if len(achievable) >= limit:
                break
    return achievable[:limit]


def _task_body(step_type: str, domain: str, variant: int) -> str:
    templates = {
        "snapshot": f"SNAPSHOT — read Goal 1 progress, live pick, and {domain} disk SSOT. Report facts only.",
        "plan": f"PLAN — one {domain} sa: goal, non-goals, done criteria (≤8 lines). No code.",
        "analyze": f"ANALYZE — search {domain} for missing validators, stale PRIORITY rows, REGISTRY drift.",
        "check": f"CHECK — run preflight validators for {domain}; log PASS/FAIL; no implement.",
        "debug": f"DEBUG — reproduce one {domain} verify FAIL; root cause in 5 lines max.",
        "fix": f"FIX — one minimal {domain} fix from last debug/check. No scope creep.",
        "implement": f"IMPLEMENT — one REGISTRY {domain} task. Minimal diff only.",
        "verify_backend": f"VERIFY backend — strict build + find_critical_bugs for {domain}.",
        "verify_ui": f"VERIFY UI — hub alignment / audit_backend_e2e spot check for {domain}.",
        "delta": f"DELTA — 3-line near-miss + blockers for {domain}. No code.",
    }
    base = templates[step_type]
    return f"{base} (variant {variant + 1}/10)."


def _role_instruction(role: str, sa: dict) -> str:
    pid = sa["id"]
    path = sa.get("path") or ""
    title = sa.get("title") or ""
    if role == "check":
        return (
            f"CHECK ONLY — read `{path}`. Run session-start + spine + find_critical_bugs. "
            f"Report gaps vs task: {title[:80]}. Do NOT implement. Do NOT closeout."
        )
    if role == "act":
        return (
            f"ACT ONLY — implement `{pid}` per its .md. Minimal diff. "
            f"Task: {title[:80]}. One sa only."
        )
    return (
        f"VERIFY + CLOSEOUT — `{pid}` only. strict build + find_critical_bugs critical 0. "
        f"REGISTRY done · PRIORITY row · pack validate · WORKER_ROUND_REPORT → STOP."
    )


def _verify_for_tier(tier: str) -> str:
    m = {
        "T0": "cd scripts && SINA_AUDIT_STRICT=1 python3 build-sina-command-panel.py && python3 find_critical_bugs.py",
        "T1": "cd scripts && bash validate-eval-packet-v1b-live.sh && bash validate-governance-fleet-v1.sh && python3 audit_hub_source_alignment.py",
        "T2": "cd scripts && python3 audit_backend_e2e.py && bash validate-spine-bridge-founder-v1.sh",
        "T3": "cd scripts && python3 find_critical_bugs.py",
    }
    return m.get(tier, m["T0"])


def build_catalog_100() -> dict:
    suggestions = []
    n = 0
    for domain in DOMAINS:
        for step_type in STEP_TYPES:
            n += 1
            suggestions.append(
                {
                    "id": n,
                    "hp_id": f"hp-{n:03d}",
                    "step_type": step_type,
                    "fast_loop_step": STEP_TYPES.index(step_type) + 1,
                    "domain": domain,
                    "category": f"{step_type}:{domain}",
                    "title": _task_body(step_type, domain, n % 10),
                    "intent": _task_body(step_type, domain, n % 10),
                    "thread": "STRATEGIC-SLICE",
                    "repo": "sourcea",
                    "workspace": str(ROOT),
                    "mandatory_reads": MANDATORY,
                    "forbidden": ["UNATTENDED BATCH", "pick 30", "batch closeout", "chat-memory sa ids"],
                    "source": "healthy-prompt-pack-v1",
                }
            )
    return {
        "schema": "healthy-prompt-pack-100.v1",
        "product": "SourceA REGISTRY drain",
        "thread": "STRATEGIC-SLICE",
        "repo": "sourcea",
        "count": 100,
        "law": "os/plan-library/sourcea-1000/HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md",
        "generated_at": _now(),
        "suggestions": suggestions,
    }


def build_queue_30(*, picks: list[dict]) -> dict:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from healthy_queue_blocker_lib import sa_requires_live_eval  # noqa: WPS433

    queue = []
    pos = 0
    for i in range(0, min(30, len(picks) * 3), 3):
        sa = picks[i // 3]
        for role in QUEUE_ROLES:
            pos += 1
            if pos > 30:
                break
            step = ROLE_TO_STEP[role]
            queue.append(
                {
                    "queue_pos": pos,
                    "hp_id": f"hq-{pos:03d}",
                    "queue_role": role,
                    "step_type": step,
                    "sa_id": sa["id"],
                    "live_eval_required": sa_requires_live_eval(sa),
                    "sa_path": sa.get("path"),
                    "sa_title": sa.get("title"),
                    "sa_tier": sa.get("tier"),
                    "phase": sa.get("phase"),
                    "title": f"[{role.upper()}] {sa['id']} — {sa.get('title', '')[:60]}",
                    "instruction": _role_instruction(role, sa),
                    "mandatory_reads": MANDATORY,
                    "verify": _verify_for_tier(sa.get("tier") or "T0") if role == "verify" else "preflight only — see CHECK/ACT law",
                    "closeout": role == "verify",
                    "forbidden": ["UNATTENDED BATCH", "pick 30", "implement on CHECK turn", "closeout on ACT turn"],
                    "one_sa_per_turn": True,
                }
            )
    return {
        "schema": "healthy-queue-30-active.v1",
        "product": "SourceA REGISTRY drain — next 30 healthy prompts",
        "thread": "STRATEGIC-SLICE",
        "repo": "sourcea",
        "count": len(queue),
        "rhythm": "3 prompts per sa: check → act → verify+closeout",
        "law": "os/plan-library/sourcea-1000/HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md",
        "generated_at": _now(),
        "sa_range": [queue[0]["sa_id"], queue[-1]["sa_id"]] if queue else [],
        "queue": queue,
    }


def patch_queue_mandatory_reads() -> dict:
    """P1: fix mandatory_reads on existing queue without changing sa_range."""
    paths = [
        OUT_DIR / "healthy-queue-30-active.json",
        Path.home() / ".sina" / "healthy-queue-30-active.json",
    ]
    updated = []
    for path in paths:
        if not path.is_file():
            continue
        q = json.loads(path.read_text(encoding="utf-8"))
        q["law"] = "brain-os/plan-registry/sourcea-1000/HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md"
        for item in q.get("queue") or []:
            item["mandatory_reads"] = list(MANDATORY)
        path.write_text(json.dumps(q, indent=2) + "\n", encoding="utf-8")
        updated.append(str(path))
    return {"ok": bool(updated), "updated": updated, "mandatory_count": len(MANDATORY)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--patch-mandatory-reads",
        action="store_true",
        help="Fix mandatory_reads paths on existing queue JSON (no regen)",
    )
    args = p.parse_args()

    if args.patch_mandatory_reads:
        out = patch_queue_mandatory_reads()
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(f"OK: patched mandatory_reads · {len(out.get('updated') or [])} files")
        return 0 if out.get("ok") else 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog = build_catalog_100()
    picks = _pick_backlog(10)  # 10 sa × 3 roles = 30 queue items
    queue = build_queue_30(picks=picks)

    cat_path = OUT_DIR / "healthy-prompt-pack-100.json"
    q_path = OUT_DIR / "healthy-queue-30-active.json"
    cat_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    q_path.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps({"catalog": str(cat_path), "queue": str(q_path), "queue_count": queue["count"]}, indent=2))
    else:
        print(f"OK: healthy-prompt-pack-100 ({catalog['count']} templates)")
        print(f"OK: healthy-queue-30-active ({queue['count']} prompts · {queue.get('sa_range')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
