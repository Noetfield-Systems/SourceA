#!/usr/bin/env python3
"""Agent filing registry gate.

Resolves pathless SAVE/LOCK/EDIT intent from a machine-readable registry so ASF
does not need to provide exact save paths when the system can route accurately.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "agent-filing-registry-v1.json"

PATH_ASKING_MARKERS = (
    "no path named",
    "which path",
    "what path",
    "provide a path",
    "provide exact path",
    "exact save path",
    "where should i save",
    "where to save",
    "ask asf for a path",
    "ask which file",
)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _slug(text: str) -> str:
    normalized = _intent_for_slug(text)
    cleaned = re.sub(
        r"\b(save|lock|and|implement|please|asf|to|as|the|this|file|doc|document|action|i|can|will|would|should|but|use|path|named)\b",
        " ",
        normalized,
    )
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", cleaned).strip("_")
    clean = re.sub(r"_+", "_", clean)
    return (clean or "agent_filing")[:72]


def _normalize_intent(text: str) -> str:
    normalized = re.sub(r"[_-]+", " ", (text or "").strip().lower())
    typo_map = {
        " batc": " batch",
        "unificaton": "unification",
        "unifcation": "unification",
    }
    for bad, good in typo_map.items():
        normalized = normalized.replace(bad, good)
    return normalized


def _intent_for_slug(text: str) -> str:
    """Keep filename slugs semantic even when scanning a full bad agent reply."""
    normalized = _normalize_intent(text)
    cut_at = min(
        (idx for marker in PATH_ASKING_MARKERS if (idx := normalized.find(marker)) >= 0),
        default=-1,
    )
    if cut_at >= 0:
        normalized = normalized[:cut_at]
    normalized = re.sub(r"\b(i can|i will|i would|i should|i need to|let me)\b", " ", normalized)
    return normalized.strip(" .,;:-")


def _next_steps_for(route: dict[str, Any], path: str) -> list[str]:
    edit_policy = str(route.get("edit_policy") or "")
    steps = [
        "report route_id and resolved path before writing",
        "run cross-lane/pre-write guard for the resolved path",
    ]
    if edit_policy == "apply_registry_unification_batch":
        steps.append("apply the registry unification batch across rules, skills, memory, and CI")
    elif edit_policy == "prefer_existing_rule_when_trigger_matches":
        steps.append("edit the preferred existing rule; do not create a duplicate rule file")
    elif edit_policy == "requires_code_context_resolution":
        steps.append("inspect code context before choosing the concrete file under the resolved scope")
    elif edit_policy == "new_incident_uses_registry_next_id":
        steps.append("allocate the next incident id from the incident registry before writing")
    else:
        steps.append(f"write or edit only the resolved target: {path}")
    steps.append("stop and ask ASF only if guard fails or registry returns no match/ambiguous")
    return steps


def _score(route: dict[str, Any], text: str) -> int:
    blob = _normalize_intent(text)
    score = int(route.get("priority") or 0)
    for trigger in route.get("triggers_any") or []:
        if str(trigger).lower() in blob:
            score += 100
    for token in route.get("intent") or []:
        if str(token).lower() in blob:
            score += 15
    return score


def _existing_preferred(route: dict[str, Any]) -> str:
    for rel in route.get("preferred_existing") or []:
        path = (ROOT / str(rel)).resolve()
        if path.is_file():
            return str(path)
    return ""


def _candidate_path(route: dict[str, Any], text: str) -> str:
    preferred = _existing_preferred(route)
    if preferred and route.get("edit_policy") == "prefer_existing_rule_when_trigger_matches":
        return preferred
    save_dir = str(route.get("save_dir") or "docs")
    template = str(route.get("filename_template") or "{slug}.md")
    slug = _slug(text)
    filename = template.replace("{slug}", slug.upper() if "LOCKED" in template else slug)
    return str((ROOT / save_dir / filename).resolve())


def resolve(*, intent: str, agent: str = "cursor") -> dict[str, Any]:
    registry = _read_json(REGISTRY)
    routes = list(registry.get("routes") or [])
    scored = []
    for route in routes:
        allowed_agents = route.get("allowed_agents") or []
        if allowed_agents and agent not in allowed_agents and "cursor" not in allowed_agents:
            continue
        score = _score(route, intent)
        if score > int(route.get("priority") or 0):
            scored.append((score, route))
    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored:
        return {
            "ok": False,
            "reason": "REGISTRY_NO_MATCH",
            "message": "No filing registry route matched; ask ASF one clarifying question.",
            "next_steps": ["ask ASF to choose category/scope, not an exact path"],
            "registry": str(REGISTRY),
        }
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return {
            "ok": False,
            "reason": "REGISTRY_AMBIGUOUS",
            "message": "Multiple filing registry routes matched equally; ask ASF to choose category, not exact path.",
            "matches": [scored[0][1].get("id"), scored[1][1].get("id")],
            "next_steps": ["ask ASF to choose one matched category/scope, not an exact path"],
            "registry": str(REGISTRY),
        }
    route = scored[0][1]
    path = _candidate_path(route, intent)
    return {
        "ok": True,
        "route_id": route.get("id"),
        "path": path,
        "edit_policy": route.get("edit_policy"),
        "next_steps": _next_steps_for(route, path),
        "registry": str(REGISTRY),
        "message": "resolved from filing registry; do not ask ASF for exact path",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Resolve pathless agent SAVE/EDIT routing from registry")
    ap.add_argument("cmd", choices=("resolve",))
    ap.add_argument("--intent", required=True, help="Founder message or summarized save/edit intent")
    ap.add_argument("--agent", default="cursor")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = resolve(intent=args.intent, agent=args.agent)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("path") or row.get("message"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
