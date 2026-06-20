#!/usr/bin/env python3
"""SSOT for three agent pipelines — Orientation · Hospital · Maze (tiered).

Law: AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md (v2 body)
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
UNIFIED_BUNDLE = ROOT / "data" / "sourcea_agentic_unified_bundle_v1.json"

LAW = "AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md"

FOUNDER_TRIGGER_POLICY: dict[str, Any] = {
    "session_start": "agent_session_gate_run_v1.py only",
    "forbidden_on_session_start": ["orientation", "hospital", "maze"],
    "founder_triggers": ["orientation", "hospital", "maze"],
    "law_section": "Session start vs founder triggers",
}

TIERS: dict[str, dict[str, Any]] = {
    "orientation": {
        "tier": 1,
        "label": "Atlas",
        "trigger": "orientation",
        "duration_class": "short",
        "duration_hint": "15–30 min read · mandatory for every new arrival",
        "authority": False,
        "purpose": "WHY we exist · good gate · good tree · full ecosystem map · zero execution",
        "founder_word_only": True,
    },
    "hospital": {
        "tier": 2,
        "label": "Clinic",
        "trigger": "hospital",
        "duration_class": "medium",
        "duration_hint": "5–15 min machine · shorter than Maze",
        "authority": False,
        "purpose": "Remember · remind · memory sync · heal disk · discharge note",
        "founder_word_only": True,
    },
    "maze": {
        "tier": 3,
        "label": "Quarantine",
        "trigger": "maze",
        "duration_class": "long",
        "duration_hint": "speed ~15–90 s when disk green · full 30–90+ min · SINA_MAZE_FORCE_FULL=1",
        "duration_speed_hint": "~15–90 s · reuses fresh find_critical + bundle receipts (INCIDENT-035)",
        "duration_full_hint": "30–90+ min · full clarification gauntlet · all validators",
        "authority": False,
        "quarantine": True,
        "purpose": "Sick patient passport · speed when green · full when critical>0 or repeat incident",
        "founder_word_only": True,
    },
}

# O-stations: gate + tree + why + map (read-only file checks + light machine probes)
ORIENTATION_READS: tuple[tuple[str, str, str], ...] = (
    ("O1", "start_here", "brain-os/law/entry/START_HERE_LOCKED_v1.md"),
    ("O2", "governance_gate", "brain-os/law/entry/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md"),
    ("O3", "authority_index", "brain-os/system/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md"),
    ("O4", "decision_stack_gate_tree", "AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md"),
    ("O5", "why_entry", "README_SOURCE_A.md"),
    ("O6", "agentic_stack", "SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md"),
    ("O7", "two_hub_law", "SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md"),
    ("O8", "three_pipelines_law", LAW),
    ("O9", "roles_map", "UNDERSTANDING_ROLES_CURSOR_ECOSYSTEM_v1.md"),
    ("O10", "architecture", "docs/ARCHITECTURE.md"),
    ("O11", "onboarding", "docs/ONBOARDING.md"),
    ("O15", "orient_routing", "docs/SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md"),
    ("O16", "node_mesh_plan", "docs/SOURCEA_NODE_MESH_SYNESTM_BUILD_PLAN_LOCKED_v1.md"),
    ("O17", "foundational_index", "docs/SOURCEA_FOUNDATIONAL_AGENTIC_SYSTEMS_INDEX_LOCKED_v1.md"),
)


def load_orientation_reads() -> tuple[tuple[str, str, str], ...]:
    """Canonical O-reads from unified bundle SSOT; fallback to ORIENTATION_READS."""
    if not UNIFIED_BUNDLE.is_file():
        return ORIENTATION_READS
    try:
        bundle = json.loads(UNIFIED_BUNDLE.read_text(encoding="utf-8"))
        rows = bundle.get("orientation_stations", {}).get("reads") or []
        out: list[tuple[str, str, str]] = []
        for row in rows:
            if isinstance(row, dict) and row.get("id") and row.get("path"):
                out.append((str(row["id"]), str(row.get("name") or row["id"]), str(row["path"])))
        return tuple(out) if out else ORIENTATION_READS
    except (OSError, json.JSONDecodeError):
        return ORIENTATION_READS

GATE_TREE: dict[str, Any] = {
    "root": "brain-os/law/entry/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md",
    "rule": "Pick ONE branch · never read 49 files",
    "branches": [
        {"id": "role", "pick": "brain-os/law/entry/START_HERE_LOCKED_v1.md", "then": "MANDATORY_READ_BY_ROLE"},
        {"id": "daily_ops", "pick": "README_SOURCE_A.md + docs/ONBOARDING.md", "then": "Loop auto · Brain work-order · Hub glance"},
        {"id": "build_wtm", "pick": "system_roadmap.py CURRENT_*_STEP", "then": "WTM map v5"},
        {"id": "critic_paste", "pick": "CHATGPT_EXTERNAL_CRITIC_LAW", "then": "INPUT CLASS: EXTERNAL_CRITIC"},
        {"id": "hub", "pick": "SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md", "then": "H1 daily · H2 deep · never legacy"},
        {"id": "incident", "pick": "brain-os/incidents/", "then": "read before repeat fix"},
    ],
}

ROLE_SKILL: dict[str, str] = {
    "worker": "agent-skills/sourcea_worker/SKILL.md",
    "brain": "agent-skills/sourcea_brain/SKILL.md",
    "governance": "agent-skills/shared/conscious-recovery/SKILL.md",
    "commercial": "agent-skills/shared/agentic-commercial/SKILL.md",
    "any": "agent-skills/shared/conscious-recovery/SKILL.md",
}

MAZE_MANDATORY_READS: tuple[str, ...] = (
    "brain-os/law/entry/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md",
    "AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md",
    "SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md",
    "SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md",
    LAW,
    "brain-os/law/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md",
    "AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1.md",
    "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md",
    "archive/legacy/sina-command/SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md",
    "brain-os/law/entry/START_HERE_LOCKED_v1.md",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def file_station(sid: str, name: str, rel: str) -> dict[str, Any]:
    path = ROOT / rel
    ok = path.is_file()
    return {
        "id": sid,
        "name": name,
        "path": rel,
        "ok": ok,
        "bytes": path.stat().st_size if ok else 0,
    }


def build_reading_pack(*, role: str = "any") -> dict[str, Any]:
    rows = []
    for sid, name, rel in load_orientation_reads():
        p = ROOT / rel
        rows.append(
            {
                "id": sid,
                "name": name,
                "path": rel,
                "exists": p.is_file(),
                "why": _why_for(name),
            }
        )
    pack = {
        "schema": "agent-orientation-reading-pack-v1",
        "at": now_iso(),
        "role_hint": role,
        "gate_tree": GATE_TREE,
        "reads": rows,
        "execution_authority": False,
        "founder_bookmark": "http://127.0.0.1:13020/",
        "worker_rule": "H1 + disk only · never H2 on routine INBOX",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    out = SINA / "agent-orientation-reading-pack-v1.json"
    out.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    return pack


def _why_for(name: str) -> str:
    why = {
        "start_here": "Pick role before any work",
        "governance_gate": "Single router — good gate",
        "authority_index": "Which law wins per topic",
        "decision_stack_gate_tree": "Authority stack + smart judgment line",
        "why_entry": "WHY SourceA exists — 30 min entry",
        "agentic_stack": "L0–L3 machines connected",
        "two_hub_law": "H1 daily fast · H2 heavy sibling",
        "three_pipelines_law": "orientation · hospital · maze triggers",
        "roles_map": "Which lane am I?",
        "architecture": "System shape",
        "onboarding": "≤30 min checklist",
        "orient_routing": "Daily ladder · cascade · role routing",
        "node_mesh_plan": "Synestm parallel mesh · N01–N20",
        "foundational_index": "Skill load order · SSOT index",
    }
    return why.get(name, "mandatory read")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


CRIT_PATH = SINA / "find-bugs" / "last-run.json"
QUARANTINE_PATH = SINA / "agent-maze-quarantine-v1.json"
HOSPITAL_RECEIPT = SINA / "agent-hospital-receipt-v1.json"
ORIENT_RECEIPT = SINA / "agent-orientation-receipt-v1.json"
BUNDLE_RECEIPT = SINA / "anti-staleness-auto-wire-v1.json"


def _parse_iso_age_hours(iso: str) -> float | None:
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0
    except (TypeError, ValueError):
        return None


def _receipt_age_hours(path: Path) -> float | None:
    row = load_json(path)
    for key in ("at", "ran_at", "synced_at", "built_at"):
        age = _parse_iso_age_hours(str(row.get(key) or ""))
        if age is not None:
            return age
    if path.is_file():
        return (datetime.now(timezone.utc).timestamp() - path.stat().st_mtime) / 3600.0
    return None


def find_critical_fresh(*, max_age_hours: float = 4.0) -> dict[str, Any]:
    """Trust find-bugs last-run when critical=0 and fresh (INCIDENT-035 speed balance)."""
    row = load_json(CRIT_PATH)
    critical = int(row.get("critical_count") or 0)
    age = _receipt_age_hours(CRIT_PATH)
    fresh = age is not None and age <= max_age_hours and row.get("ok") is True and critical == 0
    return {
        "fresh": fresh,
        "critical_count": critical,
        "age_hours": age,
        "path": str(CRIT_PATH),
        "verdict": row.get("verdict"),
    }


def hospital_green_fresh(*, max_age_hours: float = 24.0) -> dict[str, Any]:
    """Hospital discharge still valid — do not re-run full fleet (INCIDENT-035)."""
    row = load_json(HOSPITAL_RECEIPT)
    age = _receipt_age_hours(HOSPITAL_RECEIPT)
    green = (
        row.get("ok") is True
        and row.get("escalate_maze") is False
        and age is not None
        and age <= max_age_hours
    )
    return {
        "fresh": green,
        "ok": row.get("ok"),
        "escalate_maze": row.get("escalate_maze"),
        "age_hours": age,
        "path": str(HOSPITAL_RECEIPT),
    }


def anti_staleness_bundle_fresh(*, max_age_hours: float = 6.0) -> dict[str, Any]:
    row = load_json(BUNDLE_RECEIPT)
    age = _receipt_age_hours(BUNDLE_RECEIPT)
    fresh = row.get("ok") is True and age is not None and age <= max_age_hours
    return {"fresh": fresh, "age_hours": age, "queue_sa": row.get("queue_sa"), "path": str(BUNDLE_RECEIPT)}


def maze_speed_mode(*, role: str = "any") -> dict[str, Any]:
    """Fast Maze when disk proof is already green — founder word maze still runs passport."""
    force_full = os.environ.get("SINA_MAZE_FORCE_FULL", "").strip().lower() in ("1", "true", "yes")
    fc = find_critical_fresh()
    hg = hospital_green_fresh()
    bundle = anti_staleness_bundle_fresh()
    orient_age = _receipt_age_hours(ORIENT_RECEIPT)
    orient = load_json(ORIENT_RECEIPT)
    orient_ok = orient.get("orientation_complete") is True or orient.get("ok") is True
    skip_orientation = (
        not force_full
        and orient_ok
        and orient_age is not None
        and orient_age <= 24.0
    )
    enabled = not force_full and fc.get("fresh") and int(fc.get("critical_count") or 0) == 0
    return {
        "enabled": enabled,
        "force_full": force_full,
        "role": role,
        "find_critical": fc,
        "hospital_green": hg,
        "anti_staleness_bundle": bundle,
        "skip_orientation_replay": skip_orientation,
        "skip_find_critical_rerun": enabled,
        "skip_anti_staleness_bundle": not force_full and bundle.get("fresh"),
        "governance_tier": "fast" if enabled or not force_full else "full",
        "session_gate_roles": [role] if role not in ("any", "") else ["worker"],
        "law": "INCIDENT-035 speed balance · SINA_MAZE_FORCE_FULL=1 for full gauntlet",
    }


def maze_status_line(*, receipt: dict | None = None) -> str:
    """One-line maze posture for truth bundle / H1 — not a daily blocker."""
    receipt = receipt if receipt is not None else load_json(SINA / "agent-maze-receipt-v1.json")
    passport = load_json(SINA / "agent-maze-passport-v1.json")
    quarantine = load_json(QUARANTINE_PATH)
    crit = find_critical_fresh(max_age_hours=4.0)
    critical = int(crit.get("critical_count") or 0)

    if passport.get("ok") is True:
        mode = receipt.get("duration_mode") or ("speed" if (receipt.get("speed_mode") or {}).get("enabled") else "full")
        elapsed = receipt.get("elapsed_sec")
        tail = f" · {elapsed}s" if elapsed is not None else ""
        return f"MAZE PASSPORT · {mode}{tail} · quarantine=clear · optional not daily"

    if quarantine.get("active") is True:
        passed = quarantine.get("passed")
        total = quarantine.get("total")
        score = f"{passed}/{total}" if passed is not None and total else "incomplete"
        return f"MAZE QUARANTINE · {score} · RUN INBOX primary · say maze to refresh passport"

    if critical > 0:
        return f"MAZE ESCALATE · critical={critical} · hospital may route to full gauntlet"

    speed = maze_speed_mode(role="worker")
    if speed.get("enabled"):
        return "MAZE READY · speed_mode · disk green · founder says maze for passport refresh"

    return "MAZE IDLE · no passport · not a session-start step · founder word maze only"


def sync_pipelines_registry(*, maze_receipt: dict | None = None) -> dict[str, Any]:
    """Keep ~/.sina registry aligned with lib TIERS + latest maze receipt (anti-staleness)."""
    path = registry_path()
    reg = load_json(path) if path.is_file() else {}
    if reg.get("schema") not in ("agent-three-pipelines-registry-v1", "agent-three-pipelines-registry-v2"):
        reg = {"schema": "agent-three-pipelines-registry-v2", "pipelines": {}, "escalation": {}, "founder_trigger_policy": {}}

    reg["at"] = now_iso()
    reg["lib"] = "agent_three_pipelines_lib_v1.py"
    reg["router"] = "agent_three_pipelines_router_v1.py"
    reg["tier_model"] = {
        "1": {"pipeline": "orientation", "length": TIERS["orientation"]["duration_class"]},
        "2": {"pipeline": "hospital", "length": TIERS["hospital"]["duration_class"]},
        "3": {"pipeline": "maze", "length": TIERS["maze"]["duration_class"]},
    }
    reg["founder_trigger_policy"] = FOUNDER_TRIGGER_POLICY
    reg["escalation"] = {
        "hospital_to_maze_if_critical": True,
        "never_skip_orientation_for_new": True,
        "maze_not_session_start": True,
        "run_inbox_beats_passport": True,
    }
    for key, meta in TIERS.items():
        script = f"agent_{key}_pipeline_v1.py" if key != "orientation" else "agent_orientation_pipeline_v1.py"
        entry = dict(reg.get("pipelines", {}).get(key) or {})
        entry.update(
            {
                "tier": meta["tier"],
                "trigger": meta["trigger"],
                "script": script,
                "label": meta["label"],
                "duration_class": meta["duration_class"],
                "duration_hint": meta.get("duration_hint"),
                "founder_word_only": meta.get("founder_word_only", True),
            }
        )
        if key == "maze":
            entry["duration_speed_hint"] = meta.get("duration_speed_hint")
            entry["duration_full_hint"] = meta.get("duration_full_hint")
            entry["speed_mode"] = {
                "env_force_full": "SINA_MAZE_FORCE_FULL=1",
                "law": "INCIDENT-035",
                "helpers": [
                    "find_critical_fresh",
                    "hospital_green_fresh",
                    "anti_staleness_bundle_fresh",
                    "maze_speed_mode",
                ],
            }
            if maze_receipt:
                entry["last_run"] = {
                    "at": maze_receipt.get("at"),
                    "ok": maze_receipt.get("ok"),
                    "duration_mode": maze_receipt.get("duration_mode"),
                    "elapsed_sec": maze_receipt.get("elapsed_sec"),
                    "stations": f"{maze_receipt.get('stations_passed')}/{maze_receipt.get('stations_total')}",
                }
        reg.setdefault("pipelines", {})[key] = entry

    SINA.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "path": str(path), "at": reg["at"]}


def clear_maze_quarantine_if_critical_zero(*, role: str = "any", caller: str = "pipeline") -> dict[str, Any]:
    """H8 / maze exit — active:false when critical_count=0 (not repeat_incident)."""
    critical = 0
    if CRIT_PATH.is_file():
        try:
            critical = int(json.loads(CRIT_PATH.read_text(encoding="utf-8")).get("critical_count") or 0)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    if critical != 0:
        return {"cleared": False, "reason": "critical_nonzero", "critical_count": critical}
    if not QUARANTINE_PATH.is_file():
        return {"cleared": False, "reason": "no_quarantine_file"}
    prior = load_json(QUARANTINE_PATH)
    prior_reason = str(prior.get("reason") or "unknown")
    if prior_reason == "repeat_incident":
        return {"cleared": False, "reason": "repeat_incident_blocked", "prior_reason": prior_reason}
    if prior.get("active") is False:
        return {"cleared": False, "reason": "already_cleared", "prior_reason": prior_reason}
    row = {
        "active": False,
        "cleared_at": now_iso(),
        "reason": "critical_zero",
        "prior_reason": prior_reason,
        "cleared_by": caller,
        "role": role,
    }
    QUARANTINE_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return {"cleared": True, "action": "active_false", **row}


def registry_path() -> Path:
    return SINA / "agent-three-pipelines-registry-v1.json"
