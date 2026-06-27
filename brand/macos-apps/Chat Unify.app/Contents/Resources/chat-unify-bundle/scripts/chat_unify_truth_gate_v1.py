#!/usr/bin/env python3
"""Chat Unify — ORD truth gate (score → ALLOW | RETRY | ESCALATE | BLOCK).

Receipt: ~/.sina/chat-unify-truth-gate-v1.json (latest) + per-run on kernel.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
LATEST_RECEIPT = SINA / "chat-unify-truth-gate-v1.json"
GATE_VERSION = "1.3.0"

# Thresholds (truth_score 0–100)
THRESHOLD_ALLOW = 72
THRESHOLD_RETRY = 58
THRESHOLD_ESCALATE = 42

# Phase 2 weights (must sum to 100)
WEIGHT_DISK = 40
WEIGHT_CONSISTENCY = 30
WEIGHT_SOURCE = 20
WEIGHT_HEURISTIC = 10

GATE_AI_SYSTEM = """You are a truth gate advisor for a founder reviewing AI agent output.

Given atom stats and issues, return ONLY JSON:
{"action":"allow|retry|escalate|block","founder_line":"one plain sentence","reason":"brief"}

Be conservative — disk mismatch or contradictions → retry or block, not allow."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _weighted_components(
    *,
    confidence: int | None,
    issue_count: int,
    flag_count: int,
    disk_mismatch: bool,
    stats: dict | None,
    graph: dict | None,
) -> dict:
    stats = stats or {}
    checkable_n = max(1, stats.get("checkable_count") or stats.get("atom_count") or 1)
    verified = stats.get("verified") or 0
    unverified = stats.get("unverified") or 0
    mismatch = stats.get("disk_mismatch") or 0
    contradictions = stats.get("contradictions") or 0
    if not contradictions and graph:
        contradictions = sum(1 for e in graph.get("edges", []) if e.get("type") == "contradicts")

    deploy_verified = stats.get("deploy_verified")
    if deploy_verified is None:
        deploy_verified = 0

    disk_pct = int(100 * verified / checkable_n)
    if deploy_verified and verified < checkable_n:
        disk_pct = min(100, disk_pct + min(15, int(deploy_verified) * 8))
    if mismatch:
        disk_pct = max(0, disk_pct - mismatch * 18)
    if disk_mismatch:
        disk_pct = max(0, disk_pct - 25)

    live_unverified = stats.get("live_http_unverified") or 0
    if live_unverified and verified >= 1 and mismatch == 0:
        consistency_pct_boost = 8
    else:
        consistency_pct_boost = 0

    consistency_pct = max(
        0,
        100 - issue_count * 12 - contradictions * 15 - flag_count * 8 + consistency_pct_boost,
    )
    hallucinated = stats.get("hallucinated") or (unverified + mismatch)
    source_pct = max(0, 100 - int(100 * hallucinated / checkable_n))

    base = int(confidence if confidence is not None else 70)
    heuristic_pct = max(0, min(100, base - flag_count * 5))

    truth_score = int(
        (disk_pct * WEIGHT_DISK)
        + (consistency_pct * WEIGHT_CONSISTENCY)
        + (source_pct * WEIGHT_SOURCE)
        + (heuristic_pct * WEIGHT_HEURISTIC)
    ) // 100
    truth_score = max(5, min(98, truth_score))

    return {
        "truth_score": truth_score,
        "components": {
            "disk_pct": disk_pct,
            "consistency_pct": consistency_pct,
            "source_pct": source_pct,
            "heuristic_pct": heuristic_pct,
        },
        "stats": stats,
        "contradictions": contradictions,
    }


def _ai_gate_overlay(*, draft_excerpt: str, stats: dict, issues: list[str], rules_action: str) -> dict | None:
    try:
        from chat_ord_atoms_v1 import _ai_json_call  # noqa: WPS433
    except ImportError:
        return None
    user = json.dumps(
        {
            "rules_action": rules_action,
            "stats": stats,
            "issues": issues[:8],
            "draft_excerpt": draft_excerpt[:2000],
        },
        ensure_ascii=False,
    )
    data, prov = _ai_json_call(system=GATE_AI_SYSTEM, user=user, timeout_sec=18)
    if not data or not data.get("action"):
        return None
    action = str(data["action"]).lower()
    if action not in ("allow", "retry", "escalate", "block"):
        return None
    return {
        "action": action,
        "founder_line": str(data.get("founder_line") or "")[:240],
        "reason": str(data.get("reason") or "")[:400],
        "method": prov,
    }


def evaluate_truth_gate(
    *,
    confidence: int | None = None,
    issue_count: int = 0,
    flag_count: int = 0,
    issues: list | None = None,
    tags: list | None = None,
    disk_mismatch: bool = False,
    stats: dict | None = None,
    graph: dict | None = None,
    use_ai: bool = False,
    draft_excerpt: str = "",
) -> dict:
    """Governor layer — ORD report → decision with dispatch authority."""
    issues = issues or []
    tags = tags or []

    weighted = _weighted_components(
        confidence=confidence,
        issue_count=issue_count,
        flag_count=flag_count,
        disk_mismatch=disk_mismatch,
        stats=stats,
        graph=graph,
    )
    score = weighted["truth_score"]

    action = "allow"
    reason = "Output looks usable — still verify disk before execution."
    founder_line = "Proceed with one bounded step — treat agent prose as draft."
    dispatch_blocked = False

    if score >= THRESHOLD_ALLOW and issue_count <= 2 and not disk_mismatch and weighted["contradictions"] == 0:
        action = "allow"
        reason = f"Truth score {score}/100 — disk+graph OK ({weighted['components']})."
        founder_line = "ALLOW — one bounded action OK if disk agrees."
    elif score >= THRESHOLD_RETRY:
        action = "retry"
        reason = f"Truth score {score}/100 — {issue_count} issue(s), {weighted['contradictions']} contradiction(s)."
        founder_line = "RETRY — ask agent to fix contradictions before you act."
        dispatch_blocked = True
    elif score >= THRESHOLD_ESCALATE:
        action = "escalate"
        reason = f"Truth score {score}/100 — needs founder review before dispatch."
        founder_line = "ESCALATE — read disk receipts yourself before any move."
        dispatch_blocked = True
    else:
        action = "block"
        reason = f"Truth score {score}/100 — too many flags, mismatches, or graph contradictions."
        founder_line = "BLOCK — do not dispatch from this agent reply."
        dispatch_blocked = True

    if disk_mismatch and action == "allow":
        action = "retry"
        dispatch_blocked = True
        reason = f"Disk mismatch detected — downgraded to RETRY (score {score})."
        founder_line = "RETRY — agent prose disagrees with disk."

    if (stats or {}).get("disk_mismatch", 0) > 0 and action == "allow":
        action = "retry"
        dispatch_blocked = True
        reason = f"{stats.get('disk_mismatch')} atom(s) mismatch disk — RETRY."
        founder_line = "RETRY — cited paths or eval state disagree with disk."

    ai_overlay = None
    if use_ai:
        ai_overlay = _ai_gate_overlay(
            draft_excerpt=draft_excerpt,
            stats=stats or {},
            issues=issues,
            rules_action=action,
        )
        if ai_overlay:
            ai_action = ai_overlay["action"]
            severity = {"allow": 0, "retry": 1, "escalate": 2, "block": 3}
            if severity.get(ai_action, 0) > severity.get(action, 0):
                action = ai_action
                founder_line = ai_overlay.get("founder_line") or founder_line
                reason = f"AI gate: {ai_overlay.get('reason')} (rules: {score}/100)"
                dispatch_blocked = action != "allow"

    row = {
        "schema": "chat-unify-truth-gate-v1",
        "version": GATE_VERSION,
        "at": _now(),
        "action": action,
        "truth_score": score,
        "dispatch_blocked": dispatch_blocked,
        "reason": reason,
        "founder_line": founder_line,
        "inputs": {
            "confidence": confidence,
            "issue_count": issue_count,
            "flag_count": flag_count,
            "disk_mismatch": disk_mismatch,
            "issue_sample": issues[:5],
            "stats": stats,
            "weighted": weighted,
            "ai_overlay": ai_overlay,
        },
    }
    return row


def write_latest_receipt(decision: dict, *, run_id: str | None = None) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    payload = dict(decision)
    if run_id:
        payload["run_id"] = run_id
    LATEST_RECEIPT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def format_decision_block(decision: dict) -> str:
    return "\n".join(
        [
            "Truth gate",
            f"Action: {decision.get('action', '?').upper()}",
            f"Score: {decision.get('truth_score')}/100",
            f"Reason: {decision.get('reason')}",
            f"Founder: {decision.get('founder_line')}",
            f"Dispatch blocked: {decision.get('dispatch_blocked')}",
        ]
    )
