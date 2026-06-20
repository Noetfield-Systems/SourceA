"""Causal links between actions, outcomes, and failure patterns."""
from __future__ import annotations

from collections import defaultdict

from execution_intelligence.pattern_engine.api import load_patterns_v1 as load_patterns
from execution_intelligence.reader import read_execution_memory


def build_causal_links() -> list[dict]:
    records = sorted(read_execution_memory(), key=lambda r: r.get("timestamp") or "")
    patterns = load_patterns()
    links: list[dict] = []

    # Sequential: prior action outcome → next action outcome
    for i in range(1, len(records)):
        prev, curr = records[i - 1], records[i]
        pa = prev.get("action_id") or "unknown"
        ca = curr.get("action_id") or "unknown"
        if pa == ca:
            continue
        if prev.get("status") != "success" and curr.get("status") == "success":
            links.append(
                {
                    "cause": pa,
                    "effect": f"success_on:{ca}",
                    "confidence": 0.55,
                    "link_type": "recovery_sequence",
                }
            )
        elif prev.get("status") == "success" and curr.get("status") != "success":
            links.append(
                {
                    "cause": pa,
                    "effect": f"failure_on:{ca}",
                    "confidence": 0.45,
                    "link_type": "post_success_failure",
                }
            )

    # Action → failure pattern
    fail_by_action: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for rec in records:
        if rec.get("status") == "success":
            continue
        action = rec.get("action_id") or "unknown"
        sig = rec.get("error_signature") or "unknown_error"
        fail_by_action[action][sig] += 1

    for action, sigs in fail_by_action.items():
        for sig, n in sigs.items():
            conf = min(0.95, 0.4 + n * 0.12)
            links.append(
                {
                    "cause": action,
                    "effect": f"failure_pattern:{sig[:80]}",
                    "confidence": round(conf, 2),
                    "link_type": "action_failure",
                }
            )

    # Pattern registry reinforcement
    for p in patterns:
        if p.get("type") != "failure":
            continue
        from execution_intelligence.pattern_engine.helpers import action_from_pattern

        links.append(
            {
                "cause": action_from_pattern(p) or p.get("signature", ""),
                "effect": p.get("pattern_id", ""),
                "confidence": min(0.9, 0.35 + (p.get("frequency", 0) * 0.1)),
                "link_type": "registered_pattern",
            }
        )

    # Merge duplicate causes/effects — keep max confidence
    merged: dict[tuple[str, str], dict] = {}
    for link in links:
        key = (link["cause"], link["effect"])
        if key not in merged or link["confidence"] > merged[key]["confidence"]:
            merged[key] = link

    out = sorted(merged.values(), key=lambda x: -x["confidence"])
    return out[:40]


def causal_graph_summary() -> dict:
    links = build_causal_links()
    causes = sorted({l["cause"] for l in links})
    effects = sorted({l["effect"] for l in links})
    return {
        "link_count": len(links),
        "unique_causes": len(causes),
        "unique_effects": len(effects),
        "top_links": links[:12],
        "causes": causes[:15],
    }
