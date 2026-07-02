#!/usr/bin/env python3
"""L17 session cost receipt — post {agent_id, tier, model, tokens, usd_est, tasks} to truth_log.

Every agent session (session gate) emits AGENT_SESSION_COST.
Escalation to higher tier requires TIER_ESCALATION receipt with reason.
"""
from __future__ import annotations

import argparse
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = Path.home() / ".sina" / "agent-session-cost-receipt-v1.json"
ESCALATION_RECEIPT = Path.home() / ".sina" / "tier-escalation-receipt-v1.json"
CONTRACT = ROOT / "data" / "agent-session-cost-contract-v1.json"
QUEUE_SSOT = ROOT / "data" / "worker-cost-tier-queue-v1.json"

TIER_ORDER = ("T0", "T1", "T2", "T3")
TIER_USD_EST = {"T0": 0.0, "T1": 0.05, "T2": 0.15, "T3": 0.75}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def infer_tier_for_task(*, task_id: str = "", task_class: str = "") -> str:
    """Lowest plausible tier from worker-cost-tier-queue SSOT."""
    if QUEUE_SSOT.is_file():
        doc = json.loads(QUEUE_SSOT.read_text(encoding="utf-8"))
        for row in doc.get("reclassified_open_queue") or []:
            if row.get("id") == task_id:
                return str(row.get("cost_tier") or "T2")
    tc = (task_class or task_id or "").lower()
    if any(k in tc for k in ("vocab", "grep", "sweep", "registry", "sync", "lint", "script")):
        return "T0"
    if "kaizen" in tc or "copilot" in tc or "machine_safe" in tc:
        return "T1"
    if any(k in tc for k in ("integrate", "merge", "main", "l15")):
        return "T3"
    return "T2"


def estimate_session_cost(*, tier: str, role: str, step_count: int) -> dict[str, Any]:
    tier = tier if tier in TIER_ORDER else "T2"
    model = os.environ.get("CURSOR_MODEL", "").strip() or (
        "auto" if tier in ("T0", "T2") else "copilot" if tier == "T1" else "cloud-integrator"
    )
    base_tokens = {"T0": 0, "T1": 8000, "T2": 25000, "T3": 40000}.get(tier, 25000)
    tokens = base_tokens + max(0, step_count - 5) * 500
    usd = TIER_USD_EST.get(tier, 0.15)
    if tier == "T2":
        usd = 0.0
    return {"tier": tier, "model": model, "tokens": tokens, "usd_est": round(usd, 4)}


def post_tier_escalation(
    *,
    agent_id: str,
    from_tier: str,
    to_tier: str,
    reason: str,
    evidence: str = "",
) -> dict[str, Any]:
    """Escalation requires receipt — L17 routing law."""
    if from_tier not in TIER_ORDER or to_tier not in TIER_ORDER:
        return {"ok": False, "error": "invalid_tier"}
    if TIER_ORDER.index(to_tier) <= TIER_ORDER.index(from_tier):
        return {"ok": False, "error": "escalation_must_increase_tier", "from": from_tier, "to": to_tier}
    if not (reason or "").strip():
        return {"ok": False, "error": "reason_required"}

    receipt = {
        "schema": "tier-escalation-receipt-v1",
        "escalation_id": f"TESC-{uuid.uuid4().hex[:10]}",
        "at": _now(),
        "agent_id": agent_id,
        "from_tier": from_tier,
        "to_tier": to_tier,
        "reason": reason.strip(),
        "evidence": (evidence or "")[:500],
        "law": "L17 — escalation requires receipt with reason",
    }
    ESCALATION_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    ESCALATION_RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    try:
        from mac_spine_bridge_v1 import dual_write_mac_truth  # noqa: WPS433

        spine = dual_write_mac_truth(
            "TIER_ESCALATION",
            payload=receipt,
            receipt_id=receipt["escalation_id"],
        )
    except Exception as exc:
        spine = {"ok": False, "error": str(exc)[:200]}

    receipt["truth_log"] = spine
    ESCALATION_RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "receipt": receipt, "truth_log": spine}


def post_session_cost_receipt(
    *,
    agent_id: str,
    role: str = "any",
    tier: str | None = None,
    model: str | None = None,
    tokens: int | None = None,
    usd_est: float | None = None,
    tasks: list[str] | None = None,
    step_count: int = 0,
    gate_id: str = "",
) -> dict[str, Any]:
    """Post AGENT_SESSION_COST to truth_log; mirror to ~/.sina/."""
    inferred = tier or infer_tier_for_task(task_id=(tasks or [""])[0] if tasks else "")
    est = estimate_session_cost(tier=inferred, role=role, step_count=step_count)
    tier = tier or est["tier"]
    model = model or est["model"]
    tokens = tokens if tokens is not None else est["tokens"]
    usd_est = usd_est if usd_est is not None else est["usd_est"]
    task_list = tasks or [f"session_gate:{role}"]

    payload = {
        "schema": "agent-session-cost-v1",
        "cost_id": f"ASC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}",
        "at": _now(),
        "agent_id": agent_id,
        "role": role,
        "tier": tier,
        "model": model,
        "tokens": int(tokens),
        "usd_est": float(usd_est),
        "tasks": task_list,
        "gate_id": gate_id or None,
        "law": "L17 W3 — session cost receipt",
        "queue_ssot": str(QUEUE_SSOT.relative_to(ROOT)),
    }

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    try:
        from mac_spine_bridge_v1 import dual_write_mac_truth  # noqa: WPS433

        spine = dual_write_mac_truth(
            "AGENT_SESSION_COST",
            payload=payload,
            receipt_id=payload["cost_id"],
            deployment_id=tier,
        )
    except Exception as exc:
        spine = {"ok": False, "error": str(exc)[:200], "degraded": True}

    payload["truth_log"] = spine
    RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "step": "agent_session_cost",
        "agent_id": agent_id,
        "tier": tier,
        "model": model,
        "tokens": tokens,
        "usd_est": usd_est,
        "tasks": task_list,
        "receipt_path": str(RECEIPT),
        "truth_log": spine,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "command",
        choices=["post", "infer", "escalate"],
        nargs="?",
        default="post",
    )
    ap.add_argument("--agent-id", default="cursor")
    ap.add_argument("--role", default="any")
    ap.add_argument("--tier", default="")
    ap.add_argument("--task-id", default="")
    ap.add_argument("--from-tier", default="T0")
    ap.add_argument("--to-tier", default="T2")
    ap.add_argument("--reason", default="")
    ap.add_argument("--evidence", default="")
    ap.add_argument("--gate-id", default="")
    ap.add_argument("--steps", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.command == "infer":
        row = {"tier": infer_tier_for_task(task_id=args.task_id), "task_id": args.task_id}
    elif args.command == "escalate":
        row = post_tier_escalation(
            agent_id=args.agent_id,
            from_tier=args.from_tier,
            to_tier=args.to_tier,
            reason=args.reason,
            evidence=args.evidence,
        )
    else:
        tasks = [args.task_id] if args.task_id else None
        row = post_session_cost_receipt(
            agent_id=args.agent_id,
            role=args.role,
            tier=args.tier or None,
            tasks=tasks,
            step_count=args.steps,
            gate_id=args.gate_id,
        )

    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(row))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
