#!/usr/bin/env python3
"""Stranger agent safety — identify · classify · control (shared lib v1.2).

Law companion: docs/STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent_workspace_registry import AGENT_WORKSPACES, list_workspace_ids
from agentic_pipeline_lib_v1 import L1_AGENTS, L2_AGENTS, read_json

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
CONFIG_PATH = SINA / "config" / "stranger-agent-safety-v1.json"
DEFAULT_CONFIG_PATH = ROOT / "config" / "stranger-agent-safety-v1.default.json"
EXTERNAL_TOKENS_PATH = SINA / "config" / "stranger-agent-external-tokens-v1.json"
REGISTRY_PATH = SINA / "stranger-agent-registry-v1.json"
RECEIPT_PATH = SINA / "stranger-agent-admission-receipt-v1.json"
MONITOR_PATH = SINA / "stranger-agent-monitor-v1.json"
WATCH_RECEIPT_PATH = SINA / "stranger-agent-watch-receipt-v1.json"
SESSION_GATE_RECEIPT = SINA / "agent_session_gate_receipt_v1.json"
MAC_EMERGENCY_FLAG = SINA / "mac-health-emergency-active-v1.flag"
AGENT_CANCEL_FLAG = SINA / "agent-cancel-v1.flag"
CURSOR_PROJECTS = Path.home() / ".cursor" / "projects"

TRUST_TIERS = (
    "T0_founder_elevated",
    "T1_fleet_L1",
    "T2_fleet_L2",
    "T3_portfolio",
    "T4_registered_lane",
    "T5_stranger_quarantine",
    "T6_hostile_block",
)

LANE_AGENT_IDS = frozenset(
    {
        "sourcea_execution_core",
        "sourcea_worker",
        "research_acquisitor",
        "cursor_os_pro_research_lane_b",
        "cursor_os_pro_product",
    }
)

ROLE_TO_LANE: dict[str, str] = {
    "worker": "sourcea_worker",
    "brain": "sourcea_execution_core",
    "maintainer": "sourcea_worker",
    "researcher": "research_acquisitor",
    "archive": "sourcea_worker",
    "governance": "sourcea_execution_core",
    "commercial": "sourcea_execution_core",
    "brief": "sourcea_execution_core",
}

L1_ROLES = frozenset(a["role"] for a in L1_AGENTS)
L2_ROLES = frozenset(a["role"] for a in L2_AGENTS)
FLEET_CHAT_IDS: dict[str, str] = {}
for a in list(L1_AGENTS) + list(L2_AGENTS):
    FLEET_CHAT_IDS[a["chat"]] = a["role"]

EDIT_ALLOWED_RE = re.compile(
    r"EDIT\s+ALLOWED:\s*(?P<path>.+?)(?:\s+ACTION:|\s*$)",
    re.I | re.M,
)
WORK_RE = re.compile(r"\bWORK:\s*\S", re.I)
SAVE_RE = re.compile(r"\bSAVE\s+TO:\s*\S", re.I)
BULK_PATH_RE = re.compile(r"(?:\*\*|glob:|all files|every file|bulk)", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def clear_stale_unattended_panic() -> dict[str, Any]:
    """Drop mac-health unattended false positives before session/heal gates (INCIDENT-035)."""
    cleared: list[str] = []
    unattended = False
    if MAC_EMERGENCY_FLAG.is_file():
        try:
            unattended = "trigger=unattended" in MAC_EMERGENCY_FLAG.read_text(encoding="utf-8")
        except OSError:
            unattended = False
    if not unattended:
        return {"ok": True, "cleared": cleared, "reason": "no_unattended_panic"}
    for flag in (MAC_EMERGENCY_FLAG, AGENT_CANCEL_FLAG):
        if flag.is_file():
            try:
                flag.unlink(missing_ok=True)
                cleared.append(flag.name)
            except OSError:
                pass
    return {"ok": True, "cleared": cleared, "reason": "unattended_panic_cleared"}


def _resolve(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def load_config() -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "schema": "stranger-agent-safety-v1.2",
        "version": "1.2.0",
        "enabled": True,
        "quarantine_strangers": True,
        "promote_on_session_gate_pass": True,
        "session_gate_max_age_sec": 900,
        "watch_max_age_sec": 3600,
        "mac_emergency_escalates_to_hostile": True,
        "risk_score_hostile_threshold": 85,
        "trusted_mcp_servers": [
            "cursor-app-control",
            "cursor-backend-control",
            "cursor-ide-browser",
            "plugin-linear-linear",
            "plugin-notion-workspace-notion",
            "plugin-supabase-supabase",
            "plugin-figma-figma",
            "plugin-datadog-datadog",
            "user-cloudflare",
            "user-cloudflare-docs",
            "user-cloudflare-bindings",
            "user-cloudflare-builds",
            "user-cloudflare-observability",
        ],
        "high_risk_mcp_patterns": ["shell", "exec", "terminal", "filesystem-write"],
        "controls": {
            "T5_stranger_quarantine": {
                "cross_lane_writes": "block",
                "bulk_edit": "block",
                "mac_health_watch": True,
                "require_session_gate": True,
                "require_founder_elevation_for_docs": True,
            },
            "T6_hostile_block": {
                "cross_lane_writes": "block",
                "bulk_edit": "block",
                "mac_health_watch": True,
                "require_session_gate": True,
                "factory_freeze_recommend": True,
            },
        },
        "workspace_roots": {
            str(ROOT): "sourcea_worker",
            str(Path.home() / "Desktop" / "Cursor OS Pro"): "cursor_os_pro_product",
        },
        "cursor_aliases": {
            "cursor": "sourcea_worker",
            "unknown": None,
        },
    }
    for path in (CONFIG_PATH, DEFAULT_CONFIG_PATH):
        if path.is_file():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                for k, v in raw.items():
                    if isinstance(v, dict) and isinstance(defaults.get(k), dict):
                        defaults[k].update(v)
                    else:
                        defaults[k] = v
            except (OSError, json.JSONDecodeError):
                pass
            if path == CONFIG_PATH:
                break
    return defaults


def load_registry() -> dict[str, Any]:
    if REGISTRY_PATH.is_file():
        try:
            return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {
        "schema": "stranger-agent-registry-v1.2",
        "agents": {},
        "stranger_events": [],
        "stats": {"total_admissions": 0, "stranger_count": 0, "hostile_count": 0},
    }


def save_registry(reg: dict[str, Any]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    reg["schema"] = "stranger-agent-registry-v1.2"
    reg["updated_at"] = _now()
    REGISTRY_PATH.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _session_gate_fresh(max_age_sec: int) -> dict[str, Any]:
    gate = read_json(SESSION_GATE_RECEIPT)
    if not gate:
        return {"ok": False, "reason": "missing_session_gate_receipt"}
    if not gate.get("ok"):
        return {"ok": False, "reason": "session_gate_failed", "gate_id": gate.get("gate_id")}
    at = gate.get("at") or ""
    try:
        dt = datetime.fromisoformat(at.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - dt).total_seconds()
    except (TypeError, ValueError):
        return {"ok": False, "reason": "session_gate_bad_timestamp"}
    if age > max_age_sec:
        return {"ok": False, "reason": "session_gate_stale", "age_sec": round(age, 1)}
    sascip_step = next((s for s in (gate.get("steps") or []) if s.get("step") == "stranger_agent_safety"), None)
    return {
        "ok": True,
        "gate_id": gate.get("gate_id"),
        "age_sec": round(age, 1),
        "sascip_wired": bool(sascip_step),
        "sascip_tier": (sascip_step or {}).get("trust_tier"),
    }


def _cursor_project_dir(workspace_root: Path) -> Path | None:
    if not CURSOR_PROJECTS.is_dir():
        return None
    ws = str(workspace_root)
    for d in CURSOR_PROJECTS.iterdir():
        if not d.is_dir():
            continue
        hint = d.name.replace("-", "/")
        if "SourceA" in hint or ws.endswith("SourceA"):
            if "SourceA" in hint:
                return d
        try:
            workspace_root.relative_to(_resolve(hint))
            return d
        except ValueError:
            if ws == str(_resolve(hint)):
                return d
    return None


def _cursor_project_hint() -> str | None:
    cwd = _resolve(os.getcwd())
    proj = _cursor_project_dir(cwd)
    return str(proj) if proj else None


def _mcp_fingerprint(workspace_root: Path | None = None) -> dict[str, Any]:
    ws = _resolve(workspace_root or os.getcwd())
    proj = _cursor_project_dir(ws)
    cfg = load_config()
    trusted = set(cfg.get("trusted_mcp_servers") or [])
    high_risk_patterns = [p.lower() for p in (cfg.get("high_risk_mcp_patterns") or [])]
    servers: list[dict[str, Any]] = []
    unknown: list[str] = []
    high_risk: list[str] = []
    if proj:
        mcps = proj / "mcps"
        if mcps.is_dir():
            for d in sorted(mcps.iterdir()):
                if not d.is_dir():
                    continue
                sid = d.name
                meta_path = d / "SERVER_METADATA.json"
                meta: dict[str, Any] = {}
                if meta_path.is_file():
                    try:
                        meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError):
                        meta = {}
                tool_count = len(list((d / "tools").glob("*.json"))) if (d / "tools").is_dir() else 0
                row = {
                    "server_id": sid,
                    "server_name": meta.get("serverName") or sid,
                    "trusted": sid in trusted,
                    "tool_count": tool_count,
                }
                servers.append(row)
                if sid not in trusted:
                    unknown.append(sid)
                name_blob = f"{sid} {meta.get('serverName', '')}".lower()
                if any(p in name_blob for p in high_risk_patterns):
                    high_risk.append(sid)
    return {
        "project_dir": str(proj) if proj else None,
        "server_count": len(servers),
        "servers": servers,
        "unknown_servers": unknown,
        "high_risk_servers": high_risk,
        "all_trusted": len(servers) > 0 and len(unknown) == 0,
    }


def _git_workspace_signal(workspace_root: Path) -> dict[str, Any]:
    try:
        branch = subprocess.run(
            ["git", "-C", str(workspace_root), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3.0,
        )
        dirty = subprocess.run(
            ["git", "-C", str(workspace_root), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=3.0,
        )
        if branch.returncode != 0:
            return {"ok": False, "reason": "not_git_repo"}
        return {
            "ok": True,
            "branch": (branch.stdout or "").strip(),
            "dirty_files": len([ln for ln in (dirty.stdout or "").splitlines() if ln.strip()]),
        }
    except (OSError, subprocess.TimeoutExpired):
        return {"ok": False, "reason": "git_probe_failed"}


def _fleet_chat_match(chat_id: str) -> dict[str, Any]:
    cid = (chat_id or "").strip()[:8]
    if not cid:
        return {"matched": False}
    for chat_hash, role in FLEET_CHAT_IDS.items():
        if chat_hash.startswith(cid) or cid.startswith(chat_hash[:8]):
            return {"matched": True, "fleet_role": role, "chat_hash": chat_hash}
    return {"matched": False}


def _transcript_hint(workspace_root: Path) -> dict[str, Any]:
    proj = _cursor_project_dir(workspace_root)
    if not proj:
        return {"found": False}
    transcripts = proj / "agent-transcripts"
    if not transcripts.is_dir():
        return {"found": False}
    files = sorted(transcripts.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return {"found": False}
    latest = files[0]
    try:
        age = datetime.now(timezone.utc).timestamp() - latest.stat().st_mtime
    except OSError:
        age = None
    return {
        "found": True,
        "latest_id": latest.stem[:12],
        "age_sec": round(age, 1) if age is not None else None,
        "count": len(files),
    }


def _process_signals() -> dict[str, Any]:
    try:
        out = subprocess.run(
            ["ps", "-axo", "pid,pcpu,rss,comm"],
            capture_output=True,
            text=True,
            timeout=5.0,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return {"cursor_processes": 0, "unknown_python_agents": 0, "playwright_zombies": 0}
    cursor_count = 0
    unknown_py = 0
    playwright = 0
    for line in out.splitlines()[1:]:
        low = line.lower()
        if "Cursor" in line or "cursor" in low:
            cursor_count += 1
        if "python" in low and "stranger_agent" not in line:
            if any(x in line for x in ("agent_", "cursor_entry", "run_inbox")):
                unknown_py += 1
        if "playwright" in low or "chromium" in low:
            parts = line.split(None, 3)
            if len(parts) >= 2:
                try:
                    if float(parts[1]) > 50:
                        playwright += 1
                except ValueError:
                    pass
    return {
        "cursor_processes": cursor_count,
        "unknown_python_agents": unknown_py,
        "playwright_zombies": playwright,
    }


def _founder_elevation(text: str) -> bool:
    if not text.strip():
        return False
    return bool(EDIT_ALLOWED_RE.search(text) or WORK_RE.search(text) or SAVE_RE.search(text))


def detect_bulk_edit_intent(text: str) -> bool:
    return bool(BULK_PATH_RE.search(text or ""))


def _portfolio_match(workspace_root: Path) -> str | None:
    root_s = str(workspace_root)
    sourcea = str(ROOT)
    if root_s == sourcea or root_s.startswith(sourcea + os.sep):
        for ws in AGENT_WORKSPACES:
            if ws["id"] == "semej":
                continue
            repo = ws.get("repo_root")
            if not repo or repo == sourcea:
                continue
            try:
                workspace_root.relative_to(_resolve(repo))
                return ws["id"]
            except ValueError:
                if root_s == str(_resolve(repo)):
                    return ws["id"]
        return None
    for ws in AGENT_WORKSPACES:
        repo = ws.get("repo_root")
        if not repo:
            continue
        forbidden = [_resolve(p) for p in (ws.get("forbidden_roots") or [])]
        try:
            workspace_root.relative_to(_resolve(repo))
            if any(workspace_root == fb or str(workspace_root).startswith(str(fb) + os.sep) for fb in forbidden):
                continue
            return ws["id"]
        except ValueError:
            if root_s == str(_resolve(repo)):
                if any(root_s == str(fb) or root_s.startswith(str(fb) + os.sep) for fb in forbidden):
                    continue
                return ws["id"]
    hint = os.environ.get("CURSOR_WORKSPACE", "") or os.environ.get("VSCODE_CWD", "")
    if hint:
        for ws in AGENT_WORKSPACES:
            if ws.get("cursor_workspace_hint") and ws["cursor_workspace_hint"] in hint:
                return ws["id"]
    return None


def compute_risk_score(fingerprint: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    cfg = load_config()
    score = 10
    factors: list[str] = []

    tier = classification.get("trust_tier") or "T5_stranger_quarantine"
    if tier.startswith("T0"):
        return {"score": 0, "level": "minimal", "factors": ["founder_elevated"]}
    if tier.startswith("T1"):
        score = max(0, score - 25)
        factors.append("fleet_L1")
    elif tier.startswith("T2"):
        score = max(0, score - 20)
        factors.append("fleet_L2")
    elif tier.startswith("T4"):
        score = max(0, score - 15)
        factors.append("registered_lane")
    elif tier.startswith("T5"):
        score += 35
        factors.append("stranger")
    elif tier.startswith("T6"):
        score += 55
        factors.append("hostile")

    sg = fingerprint.get("session_gate") or {}
    if not sg.get("ok"):
        score += 25
        factors.append("session_gate_stale")
    if fingerprint.get("mac_emergency_active"):
        score += 20
        factors.append("mac_emergency")

    mcp = fingerprint.get("mcp") or {}
    if mcp.get("unknown_servers"):
        score += min(15, 5 * len(mcp["unknown_servers"]))
        factors.append("unknown_mcp")
    if mcp.get("high_risk_servers"):
        score += 10
        factors.append("high_risk_mcp")

    ps = fingerprint.get("process_signals") or {}
    if ps.get("unknown_python_agents", 0) > 2:
        score += 10
        factors.append("agent_process_noise")
    if ps.get("playwright_zombies", 0) > 0:
        score += 8
        factors.append("playwright_hog")

    git = fingerprint.get("git") or {}
    if git.get("ok") and git.get("dirty_files", 0) > 50:
        score += 5
        factors.append("large_dirty_tree")

    score = max(0, min(100, score))
    threshold = int(cfg.get("risk_score_hostile_threshold") or 85)
    level = "minimal" if score < 25 else "low" if score < 45 else "medium" if score < 65 else "high" if score < threshold else "critical"
    return {"score": score, "level": level, "factors": factors, "hostile_threshold": threshold}


def build_fingerprint(
    *,
    agent_id: str = "",
    role_hint: str = "any",
    workspace_root: str | Path | None = None,
    explicit_order: str = "",
    chat_id: str = "",
) -> dict[str, Any]:
    ws = _resolve(workspace_root or os.getcwd())
    cfg = load_config()
    chat_id = chat_id or os.environ.get("CURSOR_CHAT_ID", "") or os.environ.get("SINA_CHAT_ID", "")
    fp_parts = [
        str(ws),
        (agent_id or "unknown").strip().lower(),
        (role_hint or "any").strip().lower(),
        (chat_id or "")[:16],
    ]
    digest = hashlib.sha256("|".join(fp_parts).encode()).hexdigest()[:16]
    fleet = _fleet_chat_match(chat_id)
    effective_role = role_hint
    if fleet.get("matched") and role_hint in ("any", ""):
        effective_role = fleet.get("fleet_role") or role_hint

    return {
        "fingerprint_id": f"SFP-{digest}",
        "schema": "stranger-agent-fingerprint-v1.2",
        "at": _now(),
        "workspace_root": str(ws),
        "agent_id_declared": (agent_id or "unknown").strip(),
        "role_hint": (effective_role or "any").strip(),
        "chat_id": chat_id or None,
        "fleet_chat_match": fleet,
        "cursor_project_hint": _cursor_project_hint(),
        "founder_elevation": _founder_elevation(explicit_order),
        "bulk_edit_intent": detect_bulk_edit_intent(explicit_order),
        "mac_emergency_active": MAC_EMERGENCY_FLAG.is_file(),
        "session_gate": _session_gate_fresh(int(cfg.get("session_gate_max_age_sec") or 900)),
        "process_signals": _process_signals(),
        "mcp": _mcp_fingerprint(ws),
        "git": _git_workspace_signal(ws),
        "transcript": _transcript_hint(ws),
        "env_workspace": os.environ.get("CURSOR_WORKSPACE") or os.environ.get("VSCODE_CWD") or None,
    }


def classify_agent(
    fingerprint: dict[str, Any],
    *,
    explicit_order: str = "",
) -> dict[str, Any]:
    cfg = load_config()
    reg = load_registry()
    declared = (fingerprint.get("agent_id_declared") or "unknown").strip()
    role = (fingerprint.get("role_hint") or "any").strip()
    ws = _resolve(fingerprint.get("workspace_root") or ROOT)
    founder_elev = _founder_elevation(explicit_order) or fingerprint.get("founder_elevation")

    resolved_id = declared
    tier = "T5_stranger_quarantine"
    reason = "unregistered_stranger"
    fleet_layer: str | None = None

    fleet = fingerprint.get("fleet_chat_match") or {}
    if fleet.get("matched") and not founder_elev:
        fr = fleet.get("fleet_role") or role
        if fr in L1_ROLES:
            tier = "T1_fleet_L1"
            reason = "fleet_chat_hash_L1"
            fleet_layer = "L1"
            resolved_id = ROLE_TO_LANE.get(fr, "sourcea_execution_core")
            role = fr
        elif fr in L2_ROLES:
            tier = "T2_fleet_L2"
            reason = "fleet_chat_hash_L2"
            fleet_layer = "L2"
            resolved_id = ROLE_TO_LANE.get(fr, "sourcea_worker")
            role = fr

    if tier == "T5_stranger_quarantine":
        if founder_elev:
            tier = "T0_founder_elevated"
            reason = "founder_explicit_order"
            resolved_id = declared if declared not in ("unknown", "cursor", "") else ROLE_TO_LANE.get(role, "sourcea_worker")
        elif declared in LANE_AGENT_IDS:
            tier = "T4_registered_lane"
            reason = "lane_registry_match"
            resolved_id = declared
        elif declared in list_workspace_ids():
            tier = "T3_portfolio"
            reason = "portfolio_registry_match"
            resolved_id = declared
        elif role in L1_ROLES:
            tier = "T1_fleet_L1"
            reason = "l1_role_match"
            fleet_layer = "L1"
            resolved_id = ROLE_TO_LANE.get(role, "sourcea_execution_core")
        elif role in L2_ROLES:
            tier = "T2_fleet_L2"
            reason = "l2_role_match"
            fleet_layer = "L2"
            resolved_id = ROLE_TO_LANE.get(role, "sourcea_worker")
        else:
            ws_map = cfg.get("workspace_roots") or {}
            mapped = False
            for root_prefix, lane_id in ws_map.items():
                try:
                    ws.relative_to(_resolve(root_prefix))
                    tier = "T4_registered_lane"
                    reason = "workspace_root_lane_map"
                    resolved_id = lane_id
                    mapped = True
                    break
                except ValueError:
                    if str(ws) == str(_resolve(root_prefix)):
                        tier = "T4_registered_lane"
                        reason = "workspace_root_lane_map"
                        resolved_id = lane_id
                        mapped = True
                        break
            if not mapped:
                portfolio_id = _portfolio_match(ws)
                if portfolio_id:
                    tier = "T3_portfolio"
                    reason = "workspace_portfolio_match"
                    resolved_id = portfolio_id
                elif declared in ("cursor", "unknown", ""):
                    aliases = cfg.get("cursor_aliases") or {}
                    alias = aliases.get("cursor")
                    if alias and str(ws).startswith(str(ROOT)):
                        tier = "T4_registered_lane"
                        reason = "sourcea_cursor_alias"
                        resolved_id = alias

    fp_id = fingerprint.get("fingerprint_id")
    known = (reg.get("agents") or {}).get(fp_id or "")
    if known and tier.startswith("T5") and known.get("promoted_agent_id"):
        tier = str(known.get("trust_tier") or "T4_registered_lane")
        resolved_id = str(known.get("promoted_agent_id"))
        reason = "registry_promotion"

    sg = fingerprint.get("session_gate") or {}
    if tier.startswith("T5") and sg.get("ok") and cfg.get("promote_on_session_gate_pass"):
        tier = "T4_registered_lane"
        resolved_id = ROLE_TO_LANE.get(role, "sourcea_worker")
        reason = "session_gate_promotion"

    risk = compute_risk_score(fingerprint, {"trust_tier": tier})
    if fingerprint.get("mac_emergency_active") and cfg.get("mac_emergency_escalates_to_hostile"):
        if tier.startswith("T5") or risk.get("score", 0) >= int(cfg.get("risk_score_hostile_threshold") or 85):
            tier = "T6_hostile_block"
            reason = "mac_emergency_or_critical_risk"

    controls = dict((cfg.get("controls") or {}).get(tier) or {})
    if tier.startswith("T5") or tier.startswith("T6"):
        controls.setdefault("cross_lane_writes", "block")
        controls.setdefault("require_session_gate", True)

    return {
        "trust_tier": tier,
        "resolved_agent_id": resolved_id,
        "reason": reason,
        "fleet_layer": fleet_layer,
        "stranger": tier.startswith("T5") or tier.startswith("T6"),
        "controls": controls,
        "fingerprint_id": fp_id,
        "risk": risk,
    }


def apply_control(classification: dict[str, Any], fingerprint: dict[str, Any]) -> dict[str, Any]:
    controls = classification.get("controls") or {}
    tier = classification.get("trust_tier") or "T5_stranger_quarantine"
    sg = fingerprint.get("session_gate") or {}
    violations: list[str] = []
    warnings: list[str] = []

    if controls.get("require_session_gate") and not sg.get("ok"):
        violations.append(f"session_gate:{sg.get('reason', 'missing')}")

    if fingerprint.get("mac_emergency_active"):
        warnings.append("mac_emergency_active")

    if fingerprint.get("bulk_edit_intent") and controls.get("bulk_edit") == "block":
        violations.append("bulk_edit_blocked")

    mcp = fingerprint.get("mcp") or {}
    if mcp.get("high_risk_servers"):
        warnings.append(f"high_risk_mcp:{','.join(mcp['high_risk_servers'][:3])}")

    if tier == "T6_hostile_block":
        violations.append("hostile_tier_block")

    ok = len(violations) == 0
    return {
        "ok": ok,
        "tier": tier,
        "violations": violations,
        "warnings": warnings,
        "cross_lane_writes": controls.get("cross_lane_writes", "block" if classification.get("stranger") else "allow"),
        "bulk_edit": controls.get("bulk_edit", "block" if classification.get("stranger") else "allow"),
        "mac_health_watch": bool(controls.get("mac_health_watch")),
        "factory_freeze_recommend": bool(controls.get("factory_freeze_recommend")),
        "risk_score": (classification.get("risk") or {}).get("score"),
        "risk_level": (classification.get("risk") or {}).get("level"),
    }


def resolve_cross_lane_agent(
    agent: str,
    *,
    role_hint: str = "any",
    workspace_root: str | Path | None = None,
    explicit_order: str = "",
) -> dict[str, Any]:
    agent = (agent or "unknown").strip()
    if agent not in ("cursor", "unknown", "") and agent in LANE_AGENT_IDS:
        return {"ok": True, "agent": agent, "reason": "already_registered_lane"}

    fp = build_fingerprint(
        agent_id=agent, role_hint=role_hint, workspace_root=workspace_root, explicit_order=explicit_order
    )
    cls = classify_agent(fp, explicit_order=explicit_order)
    resolved = cls.get("resolved_agent_id") or agent
    if cls.get("stranger") and not _founder_elevation(explicit_order):
        return {
            "ok": False,
            "agent": agent,
            "resolved_agent_id": resolved,
            "trust_tier": cls.get("trust_tier"),
            "reason": "STRANGER_QUARANTINE",
            "message": "Stranger agent — founder must issue EDIT ALLOWED + ACTION or WORK: bounded scope",
            "fingerprint_id": fp.get("fingerprint_id"),
            "risk_score": (cls.get("risk") or {}).get("score"),
        }
    return {
        "ok": True,
        "agent": resolved,
        "resolved_agent_id": resolved,
        "trust_tier": cls.get("trust_tier"),
        "reason": cls.get("reason"),
        "fingerprint_id": fp.get("fingerprint_id"),
        "risk_score": (cls.get("risk") or {}).get("score"),
    }


def verify_external_admit(*, orchestrator_id: str, token: str, agent_id: str) -> dict[str, Any]:
    if not EXTERNAL_TOKENS_PATH.is_file():
        return {"ok": False, "reason": "external_tokens_missing"}
    try:
        raw = json.loads(EXTERNAL_TOKENS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"ok": False, "reason": "external_tokens_bad_json"}
    rows = raw.get("orchestrators") or []
    for row in rows:
        if row.get("id") != orchestrator_id:
            continue
        if row.get("token") != token:
            return {"ok": False, "reason": "token_mismatch"}
        allowed = row.get("allowed_agent_ids") or LANE_AGENT_IDS
        if agent_id not in allowed:
            return {"ok": False, "reason": "agent_not_allowed_for_orchestrator"}
        return {"ok": True, "orchestrator_id": orchestrator_id, "agent_id": agent_id}
    return {"ok": False, "reason": "orchestrator_unknown"}


def build_monitor_snapshot(receipt: dict[str, Any] | None = None) -> dict[str, Any]:
    reg = load_registry()
    receipt = receipt or read_json(RECEIPT_PATH)
    agents = reg.get("agents") or {}
    now = datetime.now(timezone.utc)
    active_strangers = 0
    hostile = 0
    for row in agents.values():
        if row.get("stranger"):
            active_strangers += 1
        if str(row.get("trust_tier", "")).startswith("T6"):
            hostile += 1
    cls = (receipt or {}).get("classification") or {}
    ctrl = (receipt or {}).get("control") or {}
    inj = (receipt or {}).get("inject") or {}
    events = reg.get("stranger_events") or []
    fp_mcp = ((receipt or {}).get("fingerprint") or {}).get("mcp") or {}
    unknown_mcp = fp_mcp.get("unknown_servers") or []
    return {
        "schema": "stranger-agent-monitor-v1.2",
        "at": _now(),
        "one_line": inj.get("one_line") or "sascip · monitor · idle",
        "last_admission_ok": (receipt or {}).get("ok"),
        "last_pipeline_id": (receipt or {}).get("pipeline_id"),
        "resolved_agent_id": cls.get("resolved_agent_id"),
        "trust_tier": cls.get("trust_tier"),
        "risk_score": (cls.get("risk") or {}).get("score"),
        "risk_level": (cls.get("risk") or {}).get("level"),
        "stranger_active_count": active_strangers,
        "hostile_count": hostile,
        "registry_agents": len(agents),
        "recent_stranger_events": len(events),
        "last_stranger_at": events[-1].get("at") if events else None,
        "mcp_unknown_count": len(unknown_mcp),
        "mac_emergency": MAC_EMERGENCY_FLAG.is_file(),
        "factory_freeze_recommend": bool(ctrl.get("factory_freeze_recommend")),
        "hub_tile": {
            "title": "Stranger Agent Safety",
            "badge": "QUARANTINE" if cls.get("stranger") else "ADMIT",
            "subtitle": f"risk {(cls.get('risk') or {}).get('score', 0)} · {cls.get('trust_tier', 'unknown')}",
            "url": "http://127.0.0.1:13024/",
        },
    }


def write_monitor_projection(receipt: dict[str, Any]) -> dict[str, Any]:
    snap = build_monitor_snapshot(receipt)
    MONITOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    MONITOR_PATH.write_text(json.dumps(snap, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return snap


def record_admission(
    fingerprint: dict[str, Any],
    classification: dict[str, Any],
    control: dict[str, Any],
    *,
    gate_id: str | None = None,
) -> dict[str, Any]:
    reg = load_registry()
    fp_id = fingerprint.get("fingerprint_id") or "SFP-unknown"
    agents = reg.setdefault("agents", {})
    prev = agents.get(fp_id) or {}
    now = _now()
    row = {
        "fingerprint_id": fp_id,
        "first_seen": prev.get("first_seen") or now,
        "last_seen": now,
        "admit_count": int(prev.get("admit_count") or 0) + 1,
        "workspace_root": fingerprint.get("workspace_root"),
        "resolved_agent_id": classification.get("resolved_agent_id"),
        "trust_tier": classification.get("trust_tier"),
        "stranger": classification.get("stranger"),
        "reason": classification.get("reason"),
        "admission_ok": control.get("ok"),
        "risk_score": (classification.get("risk") or {}).get("score"),
        "risk_level": (classification.get("risk") or {}).get("level"),
        "mcp_servers": len((fingerprint.get("mcp") or {}).get("servers") or []),
        "gate_id": gate_id,
    }
    if classification.get("stranger") and control.get("ok"):
        row["promoted_agent_id"] = classification.get("resolved_agent_id")
    agents[fp_id] = {**prev, **row}

    stats = reg.setdefault("stats", {})
    stats["total_admissions"] = int(stats.get("total_admissions") or 0) + 1
    if classification.get("stranger"):
        stats["stranger_count"] = int(stats.get("stranger_count") or 0) + 1
    if str(classification.get("trust_tier", "")).startswith("T6"):
        stats["hostile_count"] = int(stats.get("hostile_count") or 0) + 1

    if classification.get("stranger"):
        events = reg.setdefault("stranger_events", [])
        events.append(
            {
                "at": now,
                "fingerprint_id": fp_id,
                "tier": classification.get("trust_tier"),
                "resolved_agent_id": classification.get("resolved_agent_id"),
                "admission_ok": control.get("ok"),
                "risk_score": row.get("risk_score"),
            }
        )
        reg["stranger_events"] = events[-500:]

    save_registry(reg)
    return row


def run_watch_pulse() -> dict[str, Any]:
    """Re-classify recently seen fingerprints (continuous watch v1.2)."""
    cfg = load_config()
    reg = load_registry()
    max_age = int(cfg.get("watch_max_age_sec") or 3600)
    agents = reg.get("agents") or {}
    now = datetime.now(timezone.utc)
    checked = 0
    strangers = 0
    rows: list[dict] = []

    for fp_id, prev in list(agents.items())[-50:]:
        last = prev.get("last_seen") or ""
        try:
            age = (now - datetime.fromisoformat(last.replace("Z", "+00:00"))).total_seconds()
        except (TypeError, ValueError):
            age = max_age + 1
        if age > max_age:
            continue
        checked += 1
        fp = build_fingerprint(
            agent_id=prev.get("resolved_agent_id") or "cursor",
            role_hint="any",
            workspace_root=prev.get("workspace_root") or ROOT,
        )
        fp["fingerprint_id"] = fp_id
        cls = classify_agent(fp)
        if cls.get("stranger"):
            strangers += 1
        rows.append(
            {
                "fingerprint_id": fp_id,
                "trust_tier": cls.get("trust_tier"),
                "stranger": cls.get("stranger"),
                "risk_score": (cls.get("risk") or {}).get("score"),
            }
        )

    receipt = read_json(RECEIPT_PATH)
    monitor = write_monitor_projection(receipt) if receipt else build_monitor_snapshot()
    if not receipt:
        MONITOR_PATH.write_text(json.dumps(monitor, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out = {
        "schema": "stranger-agent-watch-v1.2",
        "ok": True,
        "at": _now(),
        "checked": checked,
        "active_strangers": strangers,
        "monitor_path": str(MONITOR_PATH),
        "rows": rows[:20],
        "monitor_one_line": monitor.get("one_line"),
    }
    WATCH_RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    WATCH_RECEIPT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
