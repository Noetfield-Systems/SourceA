#!/usr/bin/env python3
"""Agent memory mirror — single SSOT for forbidden stale law across all surfaces.

Law: AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md
Writes: ~/.sina/agent-memory-mirror-v1.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIRROR_PATH = Path.home() / ".sina" / "agent-memory-mirror-v1.json"
ARCHIVE_MARKERS = ("archive/superseded/", "archive/attachments/")

# id, pattern, incident, label
FORBIDDEN_STALE: list[tuple[str, str, str, str]] = [
    ("F01", r"confirm\s+to\s+auto[- ]?send", "028", "confirm to auto-send"),
    ("F02", r"auto[- ]?send\s+10\s+prompts", "028", "auto-send 10 prompts"),
    ("F03", r"tap\s+Confirm.*auto[- ]?send", "028", "tap Confirm auto-send"),
    ("F09", r"review\s+the\s+10\s+steps", "028", "review the 10 steps"),
    ("F04", r"10\s+related\s+Cursor\s+prompts", "024", "10 related Cursor prompts"),
    ("F05", r"Goal\s+1\s+auto[- ]?run", "022", "Goal 1 auto-run"),
    ("F06", r"Hub\s*▶\s*AUTO[- ]?RUN", "022", "Hub AUTO-RUN hero"),
    ("F07", r"START\s+AUTO\s+RUN", "022", "START AUTO RUN"),
    ("F08", r"Live\s+Rail\s+A\s+AUTO[- ]?RUN", "022", "Rail A AUTO-RUN"),
    ("F10", r"Sina\s+Command\s*→\s*Prompt\s+feed", "028", "Sina Command Prompt feed (legacy)"),
    ("F11", r"Open\s+Sina\s+Command.*Prompt\s+feed", "028", "Open Sina Command Prompt feed"),
    ("F12", r"Super\s+Fast\s+Hub\s*→\s*Prompt\s+feed", "028", "Super Fast Hub Prompt feed (stale daily name)"),
    ("F13", r"Hub\s*→\s*Prompt\s+feed", "028", "Hub Prompt feed (stale daily name)"),
    ("F14", r"python3\s+~/Desktop/SourceA/scripts/live_founder_decision_form", "016", "founder Terminal form CLI"),
    ("F15", r"Refresh\s+Hub\s+Track", "028", "Refresh Hub Track legacy daily"),
    ("F16", r"Sina\s+Command\s*→\s*Backlog", "028", "legacy Backlog tab navigation"),
    ("F17", r"(?:founder|you).{0,30}bash\s+verify-vault-unified", "016", "founder Terminal vault verify"),
    ("F18", r"read\s+all\s+incidents?", "031", "read all incidents"),
    ("F19", r"read\s+every\s+incident", "031", "read every incident"),
    ("F20", r"Open\s+Sina\s+Command\b", "028", "Open Sina Command (deactivated)"),
    ("F21", r"\bSina\s+Command\s*→", "028", "Sina Command arrow navigation"),
    ("F22", r"(?:Read|read|paste|Acknowledge).{0,40}INCIDENT_REPORT_ALWAYS", "031", "instruct INCIDENT_REPORT_ALWAYS read"),
]

# Close-line only — not scanned across codebase (documented in rules/scripts)
FORBIDDEN_INVITATION: list[tuple[str, str, str, str]] = [
    ("F24", r"one\s+next\s+tap", "037", "founder invitation — one next tap"),
    ("F25", r"hard\s+refresh", "037", "founder invitation — hard refresh"),
    ("F26", r"submit\s+when\s+ready", "037", "founder invitation — submit when ready"),
    ("F27", r"tap\s+here\b", "037", "founder invitation — tap here"),
    ("F28", r"(?:open|visit|go\s+to)\s+https?://[^\s]+", "037", "founder invitation — open URL in chat"),
]

FORBIDDEN: list[tuple[str, str, str, str]] = FORBIDDEN_STALE + FORBIDDEN_INVITATION

SCAN_ROOTS: list[str] = [
    "scripts",
    "agent-skills",
    ".cursor/rules",
    ".cursor/skills",
    "brain-os/law/entry",
]

EXCLUDE_REL_PATHS = frozenset(
    {
        "scripts/agent_memory_mirror_v1.py",
        "AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md",
        ".cursor/rules/000-dead-law-stubs.mdc",
        ".cursor/rules/agent-memory-mirror.mdc",
        ".cursor/rules/prompt-queue.mdc",
        "brain-os/law/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md",
        "scripts/validate-prompt-feed-no-autosend-copy-v1.sh",
        "scripts/validate-law-supersession-surfaces-v1.sh",
        "scripts/validate-hub-p0-no-autorun-v1.sh",
        "scripts/worker_hub_staleness_v1.py",
        "SINA_COMMAND_DEACTIVATED_INCIDENT_READ_POLICY_LOCKED_v1.md",
        "scripts/cursor_agent_self_audit.py",
        "scripts/agent_incident_system.py",
        "scripts/sina-command-server.py",
        "scripts/serve-sina-command.sh",
        "scripts/kill-sina-command.sh",
        "scripts/agent_workspace_mirror.py",
        "scripts/agent_council_room.py",
    }
)

SCAN_FILES: list[str] = [
    "SINA_CURSOR_PROMPT_QUEUE_ORDER_v1.md",
    "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md",
    "AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md",
    "SINA_COMMAND_DEACTIVATED_INCIDENT_READ_POLICY_LOCKED_v1.md",
]

REQUIRED_ALWAYS_RULES = (
    "000-dead-law-stubs.mdc",
    "agent-disk-live-wire-first.mdc",
    "002-hospital-trigger-only.mdc",
    "agent-daily-duty-card.mdc",
    "agent-memory-mirror.mdc",
    "agent-founder-intent-first.mdc",
    "031-mac-law-machine-enforceable-v1.mdc",
)

MANDATORY_INCIDENTS = ("024", "028", "016", "002")

def _daily_duty_inject() -> dict:
    try:
        from agent_daily_duty_card_v1 import inject_slice  # noqa: WPS433

        return inject_slice()
    except Exception:
        return {"read_first": str(Path.home() / ".sina/agent-executor-daily-duty-card-v1.json")}


def _thread_room_inject() -> dict:
    """Big-picture THREAD-* arcs — read every session (H2 registry brain_organized_reasoning)."""
    curation_path = Path.home() / ".sina/thread-room/latest-curation-v1.json"
    catalog = "SOURCEA_ECOSYSTEM_MASTER_CATALOG_LOCKED_v1.md"
    out: dict = {
        "read_every_session": str(curation_path),
        "catalog_law": catalog,
        "catalog_threads": "T0–T12 chain in catalog §2 — ECOSYSTEM anchor a53f3fa1",
        "boundary": "Thread Room maps arcs · Judge Center alarms RIGHT/STALE/BAD",
        "h2_url": "http://127.0.0.1:13020/machines/",
        "activate": "POST /api/worker-hub/rooms/run · room=thread · or thread_room_run_v1.py",
    }
    if not curation_path.is_file():
        out["status"] = "missing — run thread_room_run_v1.py"
        return out
    try:
        row = json.loads(curation_path.read_text(encoding="utf-8"))
        drafts = row.get("form_row_drafts") or []
        out["case_id"] = row.get("case_id")
        out["executive_summary"] = (row.get("executive_summary") or "")[:240]
        out["thread_arcs"] = [
            d.get("thread_arc") or d.get("id")
            for d in drafts
            if isinstance(d, dict)
        ][:8]
        out["founder_continuity"] = (row.get("founder_continuity") or [])[:6]
        out["status"] = "active"
    except (OSError, json.JSONDecodeError):
        out["status"] = "corrupt curation json"
    return out


def _behavior_settings_inject() -> dict:
    try:
        from agent_behavior_settings_v1 import inject_slice, sync_receipt  # noqa: WPS433

        sync_receipt(write=True)
        return inject_slice()
    except Exception:
        return {
            "one_law": "Always care about founder intent before mechanics, blame, or path substitution.",
            "ssot": "data/agent-behavior-settings-v1.json",
        }


def _main_problem_trigger_inject() -> dict:
    try:
        from main_problem_trigger_v1 import inject_slice  # noqa: WPS433

        return inject_slice()
    except Exception:
        return {"ssot": "data/sourcea-main-problem-trigger-v1.json"}


def _comprehension_pipeline_inject() -> dict:
    try:
        from mac_law_machine_enforce_v1 import inject_slice as mac_inject  # noqa: WPS433

        mac = mac_inject()
        return {
            "one_law": "Comprehension on cloud — POST Hub /api/comprehension-loop/v1 · not Mac validators",
            "ssot": "data/cloud-comprehension-bay-v1.json",
            "mac_law": mac,
            "comprehension_hub": mac.get("comprehension_hub"),
        }
    except Exception:
        return {"ssot": "data/cloud-comprehension-bay-v1.json"}


def _mac_law_machine_inject() -> dict:
    try:
        from mac_law_machine_enforce_v1 import inject_slice, sync_receipt  # noqa: WPS433

        sync_receipt()
        return inject_slice()
    except Exception:
        return {"ssot": "data/mac-law-machine-enforceable-v1.json"}


def _factory_cost_intelligence_inject() -> dict:
    try:
        from factory_cost_intelligence_v1 import inject_slice, sync_receipt  # noqa: WPS433

        sync_receipt(write=True)
        return inject_slice()
    except Exception:
        return {
            "one_law": "Cost is a control variable — measure receipts not theater.",
            "ssot": "data/factory-cost-intelligence-loop-v1.json",
        }


INJECT_LAW = {
    "execution_path": "brain work-order dispatch + loop auto",
    "daily_surface": "Worker Hub ZONE A — GET /api/worker-hub/v1 + Next steps disk",
    "next_steps": "Disk live next-10 + optional Worker Hub display — founder confirm optional",
    "cursor_autorun": "does_not_exist — FREEZE unless ASF resume order",
    "hub_daily": "H1 Worker Hub http://127.0.0.1:13020/ — Form official · H2 machines sibling",
    "incident_read_policy": "session gate only — mirror ids 024/028/016/002 — incident room ids not bulk read",
    "three_pipelines": "orientation | hospital | maze ONLY on founder one word — session start = agent_session_gate_run_v1.py only",
    "thread_room": "Scout→map→curate THREAD-* — read latest-curation every session for big picture · weekly machine run · H2 canonical",
    "big_picture_threads": "SOURCEA_ECOSYSTEM_MASTER_CATALOG §2 T0–T12 + thread-room arcs — disk wins over chat tail summary",
    "daily_duty_card": "AGENT_EXECUTOR_DAILY_DUTY_CARD_LOCKED_v1.md — D01–D23 founder must not re-remind",
    "founder_intent_first": "data/agent-behavior-settings-v1.json — clarify before substitute · disk truth · no green theater",
    "brain_truth_hard": "Brain — route · handoff Worker · RED stays RED · no sweet lies · real market posture",
    "factory_cost_intelligence": "data/factory-cost-intelligence-loop-v1.json — 6-layer cost loop · 100 GLN/agentic factories · planner→inbox auto-prompt",
    "ui_upgrade_first_check": "FIRST CHECK mandatory before ANY UI edit — UP-0..UP-7 + per-app ledger · pre_write blocks without ack · ZERO EXCEPTION",
    "ui_first_check_zero_exception": "Rule 026 — no agent edits form/app/website/hub/canvas without classifier + ack",
    "form_official": "Hub form INCIDENT-037 guard ON · agent-submit forbidden · hub_form surface",
    "founder_close_line": "Loop auto · guards ON · disk truth only · no invitation.",
    "founder_no_invitation": "NO INVITATION — agents report Problem · fix · guards · STOP (~/.sina/founder-no-agent-invitation-v1.flag)",
    "founder_zero_ui_drift": "ZERO UI DRIFT — no UI drift · no upgrade drift tolerated · validate-ui-zero-drift-v1 (~/.sina/founder-zero-ui-drift-v1.flag)",
    "main_problem_trigger": "Founder says main problem → PREPARE next north-star action · not report · data/sourcea-main-problem-trigger-v1.json",
    "comprehension_pipeline": "Cloud bay only — POST /api/comprehension-loop/v1 · Mac Law forbids local validator stacks",
    "mac_law_machine": "Mac = control panel · cloud executes · data/mac-law-machine-enforceable-v1.json",
    "positive_close_lines": [
        "Loop auto · factory_now_line from agent-live-surfaces-v1.json",
        "Daily H1 Worker Hub + Form official — no legacy monolith on daily path",
        "Incident room: mirror ids only — session gate receipt",
        "FREEZE default — factory background only when ASF resume",
        "Founder taps Actions/Refresh — executor runs shell",
        "Read daily duty card D01–D23 — do not re-remind founder",
        "Pipelines orientation/hospital/maze: founder one word only",
        "Thread Room: read ~/.sina/thread-room/latest-curation-v1.json — map THREAD-* before big-picture advice",
        "On conflict: agent_truth_bundle + agent-memory-mirror-v1.json win",
        "Quote factory_now_line + better_loop_line + best_loop_oqg_line from agent-live-surfaces-v1.json",
        "Quote ui_upgrade_first_check_line — FIRST CHECK before any form/app/website UI edit — ZERO EXCEPTION rule 026",
        "Hub form: INCIDENT-037 guard ON · agent-submit forbidden · founder supremacy active",
        "NO INVITATION — guards + disk truth only · never one next tap · never open/submit CTAs in chat",
        "ZERO UI DRIFT — FIRST CHECK + baseline + ledger + no-downgrade validators must PASS before any UI ship",
        "Quote nerve_system_line for unified queue + drift + loop + OQG health",
        "Founder intent first — read latest message · clarify path mismatches · never silent substitution",
        "Brain truth-first — disk receipts · FAIL/RED before wins · stay in Brain title · no green theater",
        "Main problem trigger — PREPARE cloud/form next action · forbidden report theater when founder says main problem",
        "Comprehension pipeline — C1→C5 translate every answer · no buzzwords · bug signals from disk",
    ],
}


def _live_surfaces_inject() -> dict:
    """Zero-latency lines from L0.5 surfaces — refreshed every mirror sync."""
    path = Path.home() / ".sina/agent-live-surfaces-v1.json"
    if not path.is_file():
        return {}
    try:
        surf = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {
        "synced_at": surf.get("synced_at"),
        "factory_now_line": surf.get("factory_now_line"),
        "queue_sa": surf.get("queue_sa"),
        "zero_drift_line": surf.get("zero_drift_line"),
        "better_loop_line": surf.get("better_loop_line"),
        "best_loop_oqg_line": surf.get("best_loop_oqg_line"),
        "sascip_safety_line": surf.get("sascip_safety_line") or surf.get("sascip_line"),
        "nerve_system_line": surf.get("nerve_system_line"),
        "ui_upgrade_first_check_line": surf.get("ui_upgrade_first_check_line"),
        "form_official_line": surf.get("form_official_line"),
    }


def _ui_upgrade_first_check_inject() -> dict:
    path = Path.home() / ".sina/ui-upgrade-first-check-receipt-v1.json"
    surf_path = Path.home() / ".sina/agent-live-surfaces-v1.json"
    row = {}
    if path.is_file():
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            row = {}
    surf = {}
    if surf_path.is_file():
        try:
            surf = json.loads(surf_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            surf = {}
    return {
        "one_law": "FIRST CHECK before ANY UI edit — general UP-0..UP-7 + per-app ledger",
        "wire_ok": bool(row.get("wire_ok")),
        "line": surf.get("ui_upgrade_first_check_line") or row.get("line"),
        "surfaces_count": 7,
        "ack_cmd": "python3 scripts/ui_upgrade_first_check_v1.py --surface <id> --ack --json",
        "classifier_cmd": "python3 scripts/ui_upgrade_path_classifier_v1.py --path <file> --json",
        "validator": "scripts/validate-ui-upgrade-first-check-live-wire-v1.sh",
        "law_doc": "brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md",
    }


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_scannable(path: Path) -> bool:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    if any(m in rel for m in ARCHIVE_MARKERS):
        return False
    if "__pycache__" in rel:
        return False
    if rel.startswith("agent-control-panel/command-data") and rel.endswith(".json"):
        return False  # projection — rebuilt from scripts; AS-01 validators cover P0
    if path.suffix.lower() in {".png", ".jpg", ".gif", ".woff", ".woff2", ".ico", ".pdf", ".zip", ".pyc"}:
        return False
    if path.name.startswith(".") and path.suffix not in {".mdc", ".md", ".py", ".js", ".json", ".sh", ".tsx", ".ts", ".yaml", ".yml"}:
        return False
    return True


def _is_detector_file(path: Path) -> bool:
    """Validators, stop scripts, and pattern libraries — may contain forbidden strings to detect them."""
    name = path.name
    if name.startswith("validate-"):
        return True
    detectors = (
        "stop_goal1",
        "goal1_auto_run",
        "generate-automation",
        "generate-broker",
        "ecosystem_incidents",
        "s10_eternal",
        "authority_enforce",
        "founder_p0_next_action",
        "dashboard_server",
        "governance_meta_audit",
        "sina_command_lib",
        "vocabulary_guard",
    )
    return any(d in name for d in detectors) or name == "SKILL.md"


def _collect_files() -> list[Path]:
    out: list[Path] = []
    for rel in SCAN_ROOTS:
        base = ROOT / rel
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.is_file() and _is_scannable(p) and not _is_detector_file(p):
                out.append(p)
    for rel in SCAN_FILES:
        p = ROOT / rel
        if p.is_file():
            out.append(p)
    return sorted(set(out))


def validate_surfaces() -> dict:
    violations: list[dict] = []
    compiled = [(fid, re.compile(pat, re.I), inc, label) for fid, pat, inc, label in FORBIDDEN_STALE]
    for path in _collect_files():
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if rel in EXCLUDE_REL_PATHS:
            continue
        for fid, pat, inc, label in compiled:
            for m in pat.finditer(text):
                line_start = text.rfind("\n", 0, m.start()) + 1
                line_end = text.find("\n", m.start())
                line = text[line_start : line_end if line_end != -1 else len(text)]
                if re.search(r"\bNEVER\b|FORBIDDEN|Never:", line, re.I):
                    continue
                if "forbidden" in label.lower() and "Never:" in m.group(0):
                    continue
                violations.append(
                    {
                        "id": fid,
                        "incident": inc,
                        "label": label,
                        "file": rel,
                        "excerpt": m.group(0)[:120],
                    }
                )
    rules_dir = ROOT / ".cursor" / "rules"
    missing_rules: list[str] = []
    for name in REQUIRED_ALWAYS_RULES:
        p = rules_dir / name
        if not p.is_file():
            missing_rules.append(name)
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        if "alwaysApply: true" not in t:
            missing_rules.append(f"{name} (not alwaysApply)")
    mandatory_missing: list[str] = []
    for inc in MANDATORY_INCIDENTS:
        hits = list((ROOT / "brain-os/incidents").glob(f"*INCIDENT*{inc}*LOCKED*.md"))
        if inc == "002":
            hits = hits or [ROOT / "brain-os/incidents/CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md"]
        if not any(h.is_file() for h in hits):
            mandatory_missing.append(inc)
    ok = not violations and not missing_rules and not mandatory_missing
    return {
        "ok": ok,
        "schema": "agent-memory-mirror-validate-v1",
        "validated_at": _now(),
        "violations": violations[:50],
        "violation_count": len(violations),
        "missing_always_rules": missing_rules,
        "missing_mandatory_incidents": mandatory_missing,
        "files_scanned": len(_collect_files()),
    }


def build_mirror_state() -> dict:
    val = validate_surfaces()
    files = _collect_files()
    digest = hashlib.sha256()
    for p in files:
        digest.update(str(p.relative_to(ROOT)).encode())
        try:
            digest.update(p.read_bytes())
        except OSError:
            pass
    inject = dict(INJECT_LAW)
    inject["daily_duty_card_detail"] = _daily_duty_inject()
    inject["thread_room_detail"] = _thread_room_inject()
    inject["founder_intent_first_detail"] = _behavior_settings_inject()
    inject["main_problem_trigger_detail"] = _main_problem_trigger_inject()
    inject["comprehension_pipeline_detail"] = _comprehension_pipeline_inject()
    inject["mac_law_machine_detail"] = _mac_law_machine_inject()
    inject["factory_cost_intelligence_detail"] = _factory_cost_intelligence_inject()
    inject["ui_upgrade_first_check_detail"] = _ui_upgrade_first_check_inject()
    inject["live_surfaces"] = _live_surfaces_inject()
    return {
        "schema": "agent-memory-mirror-v1",
        "synced_at": _now(),
        "mirror_hash8": digest.hexdigest()[:8],
        "validation": val,
        "forbidden": [{"id": f[0], "pattern": f[1], "incident": f[2], "label": f[3]} for f in FORBIDDEN],
        "mandatory_incidents": list(MANDATORY_INCIDENTS),
        "required_always_rules": list(REQUIRED_ALWAYS_RULES),
        "daily_duty_card_path": str(Path.home() / ".sina/agent-executor-daily-duty-card-v1.json"),
        "inject": inject,
        "surfaces": {
            "scan_roots": SCAN_ROOTS,
            "scan_files": SCAN_FILES,
            "mirror_json": str(MIRROR_PATH),
            "truth_bundle": "scripts/agent_truth_bundle_v1.py",
            "session_gate": "scripts/agent_session_gate_run_v1.py",
            "entry_gate_receipt": str(Path.home() / ".sina/cursor_entry_gate_receipt_v1.json"),
            "session_gate_receipt": str(Path.home() / ".sina/agent_session_gate_receipt_v1.json"),
        },
    }


def _sync_user_cursor_skills() -> list[str]:
    """Copy canonical repo skills into ~/.cursor/skills (second memory surface)."""
    synced: list[str] = []
    pairs = [
        (ROOT / ".cursor/skills/sina-sourcea-worker/SKILL.md", Path.home() / ".cursor/skills/sina-sourcea-worker/SKILL.md"),
    ]
    for src, dst in pairs:
        if not src.is_file():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        body = src.read_text(encoding="utf-8")
        if not dst.is_file() or dst.read_text(encoding="utf-8") != body:
            dst.write_text(body, encoding="utf-8")
            synced.append(str(dst))
    return synced


def sync_mirror() -> dict:
    user_skill_sync = _sync_user_cursor_skills()
    state = build_mirror_state()
    if user_skill_sync:
        state["user_skill_sync"] = user_skill_sync
    MIRROR_PATH.parent.mkdir(parents=True, exist_ok=True)
    MIRROR_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    mp_detail = (state.get("inject") or {}).get("main_problem_trigger_detail") or {}
    if mp_detail.get("active") and mp_detail.get("main_problem_line"):
        surfaces_path = MIRROR_PATH.parent / "agent-live-surfaces-v1.json"
        if surfaces_path.is_file():
            try:
                surfaces = json.loads(surfaces_path.read_text(encoding="utf-8"))
                surfaces["main_problem_line"] = mp_detail["main_problem_line"]
                surfaces["main_problem_trigger"] = {
                    "active": True,
                    "mode": mp_detail.get("mode"),
                    "next_action": mp_detail.get("next_action"),
                    "ssot": mp_detail.get("ssot"),
                }
                surfaces_path.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
            except (OSError, json.JSONDecodeError):
                pass
    comp_detail = (state.get("inject") or {}).get("comprehension_pipeline_detail") or {}
    if comp_detail.get("output_quality_line") or comp_detail.get("comprehension_line"):
        surfaces_path = MIRROR_PATH.parent / "agent-live-surfaces-v1.json"
        if surfaces_path.is_file():
            try:
                surfaces = json.loads(surfaces_path.read_text(encoding="utf-8"))
                if comp_detail.get("output_quality_line"):
                    surfaces["output_quality_line"] = comp_detail["output_quality_line"]
                if comp_detail.get("comprehension_line"):
                    surfaces["comprehension_line"] = comp_detail["comprehension_line"]
                surfaces["comprehension_pipeline"] = {
                    "circles": "C1→C7",
                    "last_output_verdict": comp_detail.get("last_output_verdict"),
                    "ssot": comp_detail.get("ssot"),
                }
                surfaces_path.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
            except (OSError, json.JSONDecodeError):
                pass
    return state


def main() -> int:
    ap = argparse.ArgumentParser(description="Agent memory mirror SSOT")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--sync", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.sync or not args.validate:
        state = sync_mirror()
        if args.json:
            print(json.dumps(state, indent=2, ensure_ascii=False))
        else:
            v = state["validation"]
            print(f"MIRROR_SYNC ok={v['ok']} hash={state['mirror_hash8']} violations={v['violation_count']}")
        return 0 if state["validation"]["ok"] else 1
    val = validate_surfaces()
    if args.json:
        print(json.dumps(val, indent=2, ensure_ascii=False))
    else:
        print(f"MIRROR_VALIDATE ok={val['ok']} violations={val['violation_count']}")
        for v in val.get("violations") or []:
            print(f"  {v['file']}: {v['label']} ({v['excerpt'][:60]})")
    return 0 if val.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
