"""Shared PLAN WITH NO ASF pick order — phase-first drain (law: REGISTRY_DRAIN_RAIL §PICK ORDER)."""
from __future__ import annotations

SKIP_SNIPPETS = (
    "Founder-only:",
    "Founder:",
    "founder Action",
    "founder/lanes:",
    "Wire lane:",
    "TrustField:",
)

PHASE_ORDER = (
    "phase-s0-ssot-alignment",
    "phase-s1-eval-dispatch",
    "phase-s2-hub-build-ci",
    "phase-s3-scoreboard-fleet",
    "phase-s4-spine-loop",
    "phase-s6-wtm-pre-llm",
    "phase-s5-commercial-lanes",  # T2b parallel only — after Pre-LLM (GOAL_HIERARCHY_LOCKED_v1)
    "phase-s7-council-governance",
    "phase-s8-hub-ui-ux",
    "phase-s9-research-models",
)

TIER_ORDER = ("T0", "T1", "T2", "T3")


def agent_runnable(title: str) -> bool:
    t = title.lower()
    return not any(s.lower() in t for s in SKIP_SNIPPETS)


def pick_backlog_plans(
    plans: list[dict],
    *,
    tiers: list[str] | tuple[str, ...] | None = None,
    limit: int = 1,
    order: str = "phase-first",
) -> list[dict]:
    """Return next backlog plans. Default: phase-first (finish earlier phase tiers before later phases)."""
    tier_list = list(tiers or TIER_ORDER)
    picked: list[dict] = []

    if order == "tier-global":
        for tier in tier_list:
            for pl in plans:
                if pl.get("tier") != tier or pl.get("status") != "backlog":
                    continue
                if not agent_runnable(pl.get("title", "")):
                    continue
                picked.append(pl)
                if len(picked) >= limit:
                    return picked
        return picked

    if order != "phase-first":
        raise ValueError(f"unknown pick order: {order}")

    for phase in PHASE_ORDER:
        for tier in tier_list:
            candidates = [
                pl
                for pl in plans
                if pl.get("phase") == phase
                and pl.get("tier") == tier
                and pl.get("status") == "backlog"
                and agent_runnable(pl.get("title", ""))
            ]
            candidates.sort(key=lambda pl: pl.get("id", ""))
            for pl in candidates:
                picked.append(pl)
                if len(picked) >= limit:
                    return picked
    return picked
