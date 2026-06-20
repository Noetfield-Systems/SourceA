#!/usr/bin/env python3
"""Governance events taxonomy — GOVERNANCE_UNIFICATION_ENGINE §7.6."""
from __future__ import annotations

import re

# Canonical table — GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md §7.6
EXACT_KINDS = frozenset(
    {
        "workspace_selected",
        "prompt_router",
        "governance_drift",
        "policy_reasoning_scan",
    }
)

PREFIX_KINDS = (
    "execution_state_",
    "essay_",
    "incident_",
    "governance_",
)

# Legacy aliases → canonical kind (same string when already canonical)
LEGACY_ALIASES: dict[str, str] = {
    "execution_kernel_v0": "execution_state_running",
    "execution_kernel_v1": "execution_state_running",
    "s10_eternal_audit": "governance_audit",
    "review_submitted": "governance_review",
    "session_report": "governance_session",
    "loop_round_submitted": "governance_loop",
    "loop_complete": "governance_loop",
    "mind_share": "governance_mind_share",
    "founder_signal_impact": "governance_founder_signal",
    "maintainer_ref_relocated": "governance_remediation",
    "brain_master_memory_locked": "governance_lock",
    "old_brain_extraction_merged": "governance_remediation",
    "brain_pack_locked": "governance_lock",
    "brain_lane_harden": "governance_harden",
    "doc_tag_standard": "governance_harden",
    "doc_trace_retag": "governance_remediation",
    "incident": "incident_filed",
    "incidents_registry": "incident_consolidate",
    "INCIDENT_REPORT": "incident_filed",
    "INCIDENT_SUPERSESSION": "incident_consolidate",
    "drain_recovery_plan_implemented": "governance_remediation",
    "essay_governance_event_failed": "governance_remediation",
    "vault_auto_heal": "governance_vault_auto_heal",
    "founder_pick": "governance_founder_pick",
    "n8n_wire": "governance_n8n_wire",
    "layer_stack_sync": "governance_layer_stack_sync",
}

_HEAL_RE = re.compile(r"^HEAL-\d{4}-\d{2}-\d{2}-\d{3}$")
_INCIDENT_DASH_RE = re.compile(r"^INCIDENT-\d{3,}")


def _canonicalize(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    if raw in LEGACY_ALIASES:
        return LEGACY_ALIASES[raw]
    if raw in EXACT_KINDS:
        return raw
    for prefix in PREFIX_KINDS:
        if raw.startswith(prefix):
            return raw
    for prefix in (
        "execution_kernel_",
        "s10_",
        "review_",
        "session_",
        "loop_",
        "founder_signal_",
        "founder_",
        "maintainer_",
        "brain_",
        "doc_",
        "vault_",
        "n8n_",
        "layer_",
        "l1_",
    ):
        if raw.startswith(prefix):
            return f"governance_{raw}"
    if _HEAL_RE.match(raw):
        return "governance_remediation"
    if _INCIDENT_DASH_RE.match(raw):
        return "incident_filed"
    if raw.startswith("INCIDENT_"):
        return "incident_filed"
    if raw.startswith("GOVERNANCE_"):
        return raw.lower()
    if raw.startswith("POISON_TRACK_"):
        return f"governance_{raw.lower()}"
    if raw.startswith("HOSPITAL_"):
        return f"governance_{raw.lower()}"
    if raw.startswith("EXECUTOR_"):
        return f"governance_{raw.lower()}"
    return ""


def is_resolvable_kind(kind: str) -> bool:
    return bool(_canonicalize(kind))


def normalize_kind(row: dict) -> str:
    """Return canonical kind; empty if row has no resolvable event/kind."""
    raw = str(row.get("kind") or row.get("event") or row.get("type") or "").strip()
    return _canonicalize(raw)


def normalize_row(row: dict) -> dict:
    """Attach normalized kind; preserve legacy event field."""
    out = dict(row)
    kind = normalize_kind(out)
    if kind:
        out["kind"] = kind
        if not out.get("event"):
            out["event"] = kind
    return out
