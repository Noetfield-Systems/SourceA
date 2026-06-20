#!/usr/bin/env python3
"""Brain wire — L1 Governance + all L2 agents MUST read Brain decisions from disk, not chat memory.

Law: Brain routes + locks · L1 Governance + L2 Worker/R2/M2/M3 bound to Brain SSOT.
Receipt: ~/.sina/governance-brain-wire-v1.json · alias ~/.sina/brain-wire-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from governance_paths_v1 import (
    AGENTIC_LAYER_STACK,
    LIVE_ONGOING_PROMPTS,
    NO_FAKE_PROGRESS,
    OPENROUTER_ACTIVATION_QUEUE,
    PHASE_STRICT_RUN_INBOX,
    SUPER_FAST_HUB,
)

SINA = Path.home() / ".sina"
WIRE_PATH = SINA / "governance-brain-wire-v1.json"
BRAIN_WIRE_ALIAS = SINA / "brain-wire-v1.json"
L1_PIPELINE_PATH = SINA / "l1-agent-pipeline-wire-v1.json"
RECONCILED = SINA / "brain" / "reconciled_decision.yaml"
BRAIN_ACTION = SINA / "brain-current-action-v1.json"
CHAT_CTX = SINA / "governance-chat-context-v1.json"

# Brain-bound laws Governance must obey (mtime + path proof)
BRAIN_LAW_PATHS = (
    AGENTIC_LAYER_STACK,
    SUPER_FAST_HUB,
    LIVE_ONGOING_PROMPTS,
    PHASE_STRICT_RUN_INBOX,
    OPENROUTER_ACTIVATION_QUEUE,
    NO_FAKE_PROGRESS,
)

STALE_RECONCILED_PATS = (
    re.compile(r"AUTO[- ]?RUN", re.I),
    re.compile(r"governance complete", re.I),
    re.compile(r"sa-0790", re.I),
)

# L2 second layer — all wired to Brain before act/reply (ASF order 2026-06-14)
L2_AGENTS = (
    {"rank": 5, "role": "worker", "chat": "fd67502f", "label": "SourceA Worker"},
    {"rank": 6, "role": "researcher_l2", "chat": "20b12e67", "label": "Researcher 2"},
    {"rank": 7, "role": "maintainer_2", "chat": "74f5ccab", "label": "Maintainer 2"},
    {"rank": 8, "role": "maintainer_3", "chat": "3369d11c", "label": "Maintainer 3"},
)
BRAIN_CHAT = "58148ac9"
L1_SUBORDINATE_ROLES = ("governance", "commercial", "brief_specialist")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _read_yaml_flat(path: Path) -> dict:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip().strip("'\"")
    return out


def _queue_head() -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from run_inbox_disk_truth_v1 import write_truth  # noqa: WPS433

        truth = write_truth(sync=False)
        q = truth.get("queue") or {}
        exhausted = bool(q.get("queue_exhausted"))
        sa_id = "" if exhausted else (q.get("sa_id") or truth.get("queue_sa") or "")
        return {
            "sa_id": sa_id,
            "role": q.get("role") if not exhausted else "",
            "pos": q.get("pos"),
            "phase_strict_order": truth.get("phase_strict_order"),
            "queue_exhausted": exhausted,
        }
    except Exception as exc:
        return {"error": str(exc)}


def _brain_laws() -> list[dict]:
    rows = []
    for path in BRAIN_LAW_PATHS:
        if not path.is_file():
            continue
        st = path.stat()
        rel = path.relative_to(ROOT).as_posix()
        summary = ""
        if path.name == "SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md":
            summary = "Two-hub: H1 Super Fast daily · H2 /machines/ heavy · legacy archive — not three daily surfaces"
        rows.append(
            {
                "path": rel,
                "mtime": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "summary": summary or rel,
            }
        )
    return rows


def _l1_pipeline_ref(existing_wire: dict, l1_pipe_disk: dict) -> dict:
    ref = existing_wire.get("l1_pipeline") or {}
    if l1_pipe_disk:
        wired = l1_pipe_disk.get("l1_wired") or {}
        return {
            "ssot": str(L1_PIPELINE_PATH),
            "alias": str(SINA / "l1-brain-pipeline-wire-v1.json"),
            "script": "l1_agent_pipeline_wire_v1.py",
            "at": l1_pipe_disk.get("at"),
            "present": True,
            "l1_agent_count": len(wired.get("agents") or []),
            "l1_to_brain_count": len((l1_pipe_disk.get("l1_to_brain") or {}).get("subordinates") or []),
            "brain_hub": bool(l1_pipe_disk.get("brain_hub")),
        }
    if ref.get("present") or ref.get("at"):
        return ref
    return {
        "ssot": str(L1_PIPELINE_PATH),
        "alias": str(SINA / "l1-brain-pipeline-wire-v1.json"),
        "script": "l1_agent_pipeline_wire_v1.py",
        "present": False,
        "rule": "Run l1_agent_pipeline_wire_v1.py for L1→Brain mesh",
    }


def wire_brain_governance(*, sync_brain: bool = True) -> dict:
    t0 = datetime.now(timezone.utc)
    steps: list[dict] = []

    if sync_brain:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

            snap = sync_brain_snapshot(mode="light", caller="brain_governance_wire")
            steps.append({"step": "brain_snapshot_sync", "ok": bool(snap.get("ok")), "synced": snap.get("synced")})
        except Exception as exc:
            steps.append({"step": "brain_snapshot_sync", "ok": False, "error": str(exc)})

    reconciled = _read_yaml_flat(RECONCILED)
    brain_action = _read_json(BRAIN_ACTION)
    chat_ctx = _read_json(CHAT_CTX)
    existing_wire = _read_json(WIRE_PATH)
    l1_pipe_disk = _read_json(L1_PIPELINE_PATH)
    head = _queue_head()

    stale_reasons: list[str] = []
    decision_text = reconciled.get("decision") or ""
    for pat in STALE_RECONCILED_PATS:
        if pat.search(decision_text):
            stale_reasons.append(f"reconciled_decision matches stale pattern: {pat.pattern}")
    rec_sa = reconciled.get("next_sa") or ""
    live_sa = str(head.get("sa_id") or "")
    if rec_sa and live_sa and rec_sa != live_sa:
        stale_reasons.append(f"reconciled next_sa={rec_sa} != queue_head={live_sa}")

    act_sa = (brain_action.get("inbox") or {}).get("sa_id") or brain_action.get("next_action", "")
    if act_sa and live_sa and "sa-" in str(act_sa) and live_sa not in str(act_sa):
        stale_reasons.append(f"brain-current-action stale vs queue (mentions {act_sa}, head {live_sa})")

    active_decisions = [
        {
            "id": "agentic_layer_stack",
            "authority": "ASF order 2026-06-14",
            "law": "SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md",
            "bind": "L1: Brain(1) > Gov(2) > Commercial(3) > Brief(4) · L2: Worker(5) > R2(6) > M2(7) > M3(8) · L3: portfolio repos(9+)",
        },
        {
            "id": "two_hub_model",
            "authority": "ASF order 2026-06-14",
            "law": "SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md",
            "bind": "Worker Hub optional · RUN INBOX primary · legacy /legacy/ archive",
        },
        {
            "id": "openrouter_first_queue",
            "authority": "phase-strict-drain-v1.json",
            "law": "SOURCEA_OPENROUTER_ACTIVATION_QUEUE_LOCKED_v1.md",
            "bind": f"Queue head {live_sa} · OpenRouter s1 pack first",
        },
        {
            "id": "factory_freeze",
            "authority": "ASF enterprise ship law",
            "law": "SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md",
            "bind": "FREEZE until W1 receipt · no AUTO-RUN P0",
        },
        {
            "id": "next_steps_rename",
            "authority": "Governance rename 2026-06-14",
            "law": "SOURCEA_FOUNDER_MACHINE_TERMINOLOGY_DICTIONARY_LOCKED_v1.md",
            "bind": "Daily surface = Worker Hub Next steps · disk live-ongoing-prompts-next-10-v1.json",
        },
    ]

    role_map = chat_ctx.get("role_map") or {}
    brain_id = role_map.get("brain") or BRAIN_CHAT
    brain_chats = [
        t for t in (chat_ctx.get("threads") or [])
        if t.get("role") == "brain" or t.get("id") == brain_id
    ]
    if not brain_chats:
        brain_chats = [{"id": brain_id, "role": "brain", "label": "SourceA Brain — route · pick · handoff"}]

    l2_from_ctx = (chat_ctx.get("layer_stack") or {}).get("L2_agentic_second") or []
    l2_agents = []
    for spec in L2_AGENTS:
        row_l2 = dict(spec)
        row_l2["wire_path"] = str(WIRE_PATH)
        row_l2["sync_before_act"] = True
        row_l2["rule"] = "Load active_decisions[] before build/heal/reply — IGNORE stale reconciled_decision"
        for ctx_row in l2_from_ctx:
            if ctx_row.get("chat") == spec["chat"] or ctx_row.get("role") == spec["role"]:
                row_l2["rank"] = ctx_row.get("rank", spec["rank"])
                break
        l2_agents.append(row_l2)

    ok = len(stale_reasons) == 0 or bool(active_decisions)
    ms = int((datetime.now(timezone.utc) - t0).total_seconds() * 1000)
    row = {
        "ok": ok,
        "schema": "brain-wire-v1",
        "schema_legacy": "governance-brain-wire-v1",
        "at": _now(),
        "ms": ms,
        "brain_chats": brain_chats,
        "l1_wired_to_brain": {
            "mandatory": True,
            "pipeline_script": "l1_agent_pipeline_wire_v1.py",
            "pipeline_ssot": str(L1_PIPELINE_PATH),
            "brain_hub_chat": BRAIN_CHAT,
            "subordinates": list(L1_SUBORDINATE_ROLES),
            "rule": "ALL L1 subordinates wired TO Brain via Python pipeline",
        },
        "l1_pipeline": _l1_pipeline_ref(existing_wire, l1_pipe_disk),
        "l2_wired": {
            "mandatory": True,
            "wire_paths": [str(WIRE_PATH), str(BRAIN_WIRE_ALIAS)],
            "agents": l2_agents,
            "rule": "ALL L2 MUST read Brain wire before act/reply — queue_head + active_decisions[] win over chat",
        },
        "reconciled_decision": {
            "path": str(RECONCILED),
            "updated_at": reconciled.get("updated_at"),
            "decision_preview": decision_text[:120],
            "next_sa": rec_sa,
            "stale": bool(stale_reasons),
            "stale_reasons": stale_reasons,
            "governance_rule": "IGNORE reconciled_decision when stale=true — obey active_decisions[]",
        },
        "brain_current_action": {
            "path": str(BRAIN_ACTION),
            "at": brain_action.get("at"),
            "stale_hint": stale_reasons[-1] if stale_reasons else None,
        },
        "queue_head": head,
        "active_decisions": active_decisions,
        "brain_laws": _brain_laws(),
        "steps": steps,
        "law": "Brain wire for L1→Brain pipeline + ALL L2 — load active_decisions[] before act",
    }

    SINA.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(row, indent=2) + "\n"
    WIRE_PATH.write_text(payload, encoding="utf-8")
    BRAIN_WIRE_ALIAS.write_text(payload, encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Wire Brain decisions into L1 Governance + L2 agent SSOT")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-sync", action="store_true", help="Skip brain snapshot sync")
    args = ap.parse_args()
    row = wire_brain_governance(sync_brain=not args.no_sync)
    if args.json or True:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
