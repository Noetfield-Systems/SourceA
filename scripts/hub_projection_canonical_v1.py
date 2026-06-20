#!/usr/bin/env python3
"""P1 — Hub projection split: canonical (deterministic SSOT) vs runtime (ephemeral live mirrors)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

CANONICAL_PROJECTION_SCHEMA = "hub-canonical-projection-v1"
RUNTIME_PROJECTION_SCHEMA = "hub-runtime-projection-v1"

# Derives from laws · skills · graph · catalog · queue truth locally (GPT P1 spec).
# Fixed materializer stamp fields — not law content (closed set; not a growing exclude list).
PROJECTION_META_KEYS = frozenset(
    {
        "built_at",
        "updated_at",
        "generated_at",
        "last_evaluated_at",
        "materialized_at",
        "probe_at",
        "aligned_at",
        "_aligned_at",
    }
)

CANONICAL_ROOT_KEYS = frozenset(
    {
        "schema_version",
        "source_a_root",
        "command_center",
        "sourcea_sa_queue",
        "system_roadmap",
        "agent_scoreboard",
        "strategic_synthesis",
        "essay_discourse",
        "branches",
        "rules",
        "master_orders",
        "thread_index",
        "founder_threads",
        "full_threads",
        "ecosystem",
        "bowl",
        "signals",
        "ops_blockers",
        "mergepack_kpi",
        "drift_hints",
        "roles_detail",
        "hq_duties_full",
        "personal_db",
        "prompt_os",
        "founder_actions",
        "mini_apps",
        "live_products",
        "sources",
        "guides",
        "daily_hub",
        "emergency_stop",
        "todos_editable",
        "brief_text",
        "brief_fa",
        "asf_notes",
        "governance_drift",
        "governance_unification",
        "important_docs",
        "roadmaps_goals",
        "execution_spine",
    }
)

# Never fingerprinted — live runtime mirrors (validator blind by design, not exclusion list).
RUNTIME_ROOT_KEYS = frozenset(
    {
        "built_at",
        "refresh_log",
        "generation_id",
        "generation",
        "agent_loop",
        "runtime",
        "fleet",
        "worker_inbox",
        "healthy_drain_rail",
        "healthy_drain_orchestrator",
        "goal1_auto_run",
        "goal1_loop",
        "semej",
        "home_founder_view",
        "worker_drain_next_10",
        "missed_actions_card",
        "live_ongoing_prompts",
        "prompt_queue",
        "prompt_direction",
        "recent_subjects",
        "commitments",
        "agent_workspaces",
        "incident_room",
        "conflict_room",
        "council_room",
        "lane_briefs",
        "audit_backlog",
        "agent_reviews",
        "anti_staleness_as01",
        "founder_notes",
        "ai_advisory",
        "hq_audit",
    }
)


def strip_projection_meta(obj: Any) -> Any:
    """Remove materializer stamps from canonical subtrees (fixed meta schema only)."""
    if isinstance(obj, dict):
        return {
            k: strip_projection_meta(v)
            for k, v in obj.items()
            if k not in PROJECTION_META_KEYS
        }
    if isinstance(obj, list):
        return [strip_projection_meta(x) for x in obj]
    return obj


def split_hub_projection(full: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Materializer produces two views — validator hashes canonical only."""
    canonical: dict[str, Any] = {
        "projection_schema": CANONICAL_PROJECTION_SCHEMA,
        "source_a_root": full.get("source_a_root"),
        "schema_version": full.get("schema_version"),
    }
    for key in sorted(CANONICAL_ROOT_KEYS):
        if key in full and key not in ("source_a_root", "schema_version"):
            canonical[key] = strip_projection_meta(full[key])

    runtime: dict[str, Any] = {
        "projection_schema": RUNTIME_PROJECTION_SCHEMA,
        "built_at": full.get("built_at"),
        "refresh_log": full.get("refresh_log"),
    }
    for key, value in full.items():
        if key in canonical or key in ("projection_schema",):
            continue
        runtime[key] = value
    return canonical, runtime


def canonical_fingerprint(data: dict[str, Any]) -> str:
    canon = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def canonical_fingerprint_file(path: Path) -> str:
    return canonical_fingerprint(json.loads(path.read_text(encoding="utf-8")))


def projection_paths(panel_dir: Path) -> dict[str, Path]:
    return {
        "full": panel_dir / "command-data.json",
        "canonical": panel_dir / "command-data-canonical.json",
        "runtime": panel_dir / "command-data-runtime.json",
        "shell": panel_dir / "command-data-shell.json",
    }
