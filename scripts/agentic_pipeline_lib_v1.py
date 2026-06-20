#!/usr/bin/env python3
"""Agentic pipeline shared lib — paths · agents · health · cross-ref checks."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"

PATHS = {
    "l1_pipeline": SINA / "l1-agent-pipeline-wire-v1.json",
    "l1_brain_alias": SINA / "l1-brain-pipeline-wire-v1.json",
    "brain_wire": SINA / "governance-brain-wire-v1.json",
    "brain_wire_alias": SINA / "brain-wire-v1.json",
    "pipeline_v2": SINA / "agentic-layer-pipeline-v2.json",
    "wire_sync_v1": SINA / "agentic-layer-wire-sync-v1.json",
    "chat_context": SINA / "governance-chat-context-v1.json",
    "run_inbox_truth": SINA / "run-inbox-disk-truth-v1.json",
    "factory_now": SINA / "factory-now-v1.json",
    "memory_mirror": SINA / "agent-memory-mirror-v1.json",
}

L1_AGENTS = (
    {"rank": 1, "role": "brain", "chat": "58148ac9"},
    {"rank": 2, "role": "governance", "chat": "e54ddfa8"},
    {"rank": 3, "role": "commercial", "chat": "6245d9dd"},
    {"rank": 4, "role": "brief_specialist", "chat": "85dd7cd4"},
)

L2_AGENTS = (
    {"rank": 5, "role": "worker", "chat": "fd67502f"},
    {"rank": 6, "role": "researcher_l2", "chat": "20b12e67"},
    {"rank": 7, "role": "maintainer_2", "chat": "74f5ccab"},
    {"rank": 8, "role": "maintainer_3", "chat": "3369d11c"},
)

L3_ROLES = ("trustfield", "noetfield", "forge", "other_repos")

STALE_WARN_SEC = 600
STALE_CRIT_SEC = 3600


def read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def parse_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def age_sec(path: Path, *, fallback_at: str | None = None) -> float | None:
    if path.is_file():
        try:
            return datetime.now(timezone.utc).timestamp() - path.stat().st_mtime
        except OSError:
            pass
    dt = parse_at(fallback_at)
    if dt:
        return (datetime.now(timezone.utc) - dt).total_seconds()
    return None


def staleness_label(age: float | None) -> str:
    if age is None:
        return "missing"
    if age >= STALE_CRIT_SEC:
        return "critical"
    if age >= STALE_WARN_SEC:
        return "stale"
    return "fresh"


def cross_ref_check(l1: dict, brain: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    l1_shared = (l1.get("l1_wired") or {}).get("shared") or {}
    l1_head = (l1_shared.get("queue_head") or {}).get("sa_id")
    brain_head = (brain.get("queue_head") or {}).get("sa_id")
    if l1_head and brain_head and l1_head != brain_head:
        issues.append(f"queue_head mismatch l1={l1_head} brain={brain_head}")

    l1_subs = len((l1.get("l1_to_brain") or {}).get("subordinates") or [])
    if l1_subs < 3:
        issues.append(f"l1_to_brain subordinates={l1_subs} < 3")

    l2_n = len((brain.get("l2_wired") or {}).get("agents") or [])
    if l2_n < 4:
        issues.append(f"l2_wired agents={l2_n} < 4")

    if not brain.get("l1_pipeline"):
        issues.append("brain wire missing l1_pipeline cross-ref")
    if not brain.get("l1_wired_to_brain"):
        issues.append("brain wire missing l1_wired_to_brain")
    if not l1.get("brain_hub"):
        issues.append("l1 pipeline missing brain_hub")

    return len(issues) == 0, issues


def _lawful_idle(truth: dict) -> bool:
    q = truth.get("queue") or {}
    if q.get("queue_exhausted"):
        return True
    fn = read_json(PATHS["factory_now"])
    return (
        int(fn.get("valid_yes") or 0) >= 1000
        and int(fn.get("backlog") or 0) == 0
        and bool(fn.get("dual_proof_ok"))
        and not str(fn.get("queue_sa") or "").strip()
    )


def _outbound_upgrade_queue(truth: dict) -> bool:
    q = truth.get("queue") or {}
    if str(q.get("phase") or "") == "phase-s6-outbound-factory-upgrade":
        return True
    hq = read_json(SINA / "healthy-queue-30-active.json")
    return bool(hq.get("upgrade_plan_schema")) or str(hq.get("phase") or "") == "phase-s6-outbound-factory-upgrade"


def dual_pick_check() -> dict:
    truth = read_json(PATHS["run_inbox_truth"])
    queue_sa = (truth.get("queue") or {}).get("sa_id") or truth.get("queue_sa") or ""
    live_sa = (truth.get("live_pick") or {}).get("id") or truth.get("live_pick_sa") or ""
    if not live_sa:
        gp_path = SINA / "goal-progress-v1.json"
        gp = read_json(gp_path)
        live_sa = (gp.get("live_pick") or {}).get("id") or ""
    if _lawful_idle(truth):
        return {
            "live_pick_sa": live_sa,
            "queue_sa": queue_sa,
            "aligned": True,
            "idle": True,
        }
    if _outbound_upgrade_queue(truth) and queue_sa:
        surfaces = read_json(PATHS.get("agent_surfaces", SINA / "agent-live-surfaces-v1.json"))
        fn = read_json(PATHS["factory_now"])
        surface_sa = str(surfaces.get("queue_sa") or fn.get("queue_sa") or "")
        pick_sa = live_sa or surface_sa or queue_sa
        if pick_sa == queue_sa:
            return {
                "live_pick_sa": queue_sa,
                "queue_sa": queue_sa,
                "aligned": True,
                "outbound_upgrade": True,
            }
    q = truth.get("queue") or {}
    fn = read_json(PATHS["factory_now"])
    if (
        queue_sa
        and not live_sa
        and str(fn.get("mode")) == "SINGLE_SA"
        and queue_sa == str(fn.get("queue_sa") or "")
        and not q.get("queue_exhausted")
    ):
        return {
            "live_pick_sa": queue_sa,
            "queue_sa": queue_sa,
            "aligned": True,
            "single_sa_queue": True,
            "phase": q.get("phase") or "",
        }
    aligned = bool(live_sa and queue_sa and live_sa == queue_sa)
    return {
        "live_pick_sa": live_sa,
        "queue_sa": queue_sa,
        "aligned": aligned,
    }


def stack_health(l1: dict, brain: dict) -> dict:
    dual = dual_pick_check()
    l1_age = age_sec(PATHS["l1_pipeline"], fallback_at=l1.get("at"))
    brain_age = age_sec(PATHS["brain_wire"], fallback_at=brain.get("at"))
    mirror = read_json(PATHS["memory_mirror"])
    return {
        "status": "ok",
        "L1": {
            "agents": len((l1.get("l1_wired") or {}).get("agents") or []),
            "wired_to_brain": len((l1.get("l1_to_brain") or {}).get("subordinates") or []),
            "brain_hub": bool(l1.get("brain_hub")),
            "wire_age_sec": l1_age,
            "wire_staleness": staleness_label(l1_age),
        },
        "L2": {
            "agents": len((brain.get("l2_wired") or {}).get("agents") or []),
            "wire_age_sec": brain_age,
            "wire_staleness": staleness_label(brain_age),
        },
        "brain": {
            "queue_head": (brain.get("queue_head") or {}).get("sa_id"),
            "reconciled_stale": (brain.get("reconciled_decision") or {}).get("stale"),
            "active_decisions": len(brain.get("active_decisions") or []),
        },
        "dual_pick": dual,
        "memory_mirror_ok": (mirror.get("validation") or {}).get("ok"),
    }
