#!/usr/bin/env python3
"""L1 → Brain pipeline — ALL first-layer agents wired TO Brain through machine Python.

Law: Brain is L1 hub · Gov · Commercial · Brief read Brain decisions via pipeline — chat is input only.
Receipt: ~/.sina/l1-agent-pipeline-wire-v1.json · alias ~/.sina/l1-brain-pipeline-wire-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SCRIPTS = ROOT / "scripts"
L1_PIPELINE_PATH = SINA / "l1-agent-pipeline-wire-v1.json"
L1_BRAIN_PIPELINE_ALIAS = SINA / "l1-brain-pipeline-wire-v1.json"
BRAIN_WIRE_PATH = SINA / "governance-brain-wire-v1.json"
CHAT_CTX = SINA / "governance-chat-context-v1.json"

L1_AGENTS = (
    {
        "rank": 1,
        "role": "brain",
        "chat": "58148ac9",
        "label": "SourceA Brain",
        "execution_authority": True,
        "writes": ["brain/reconciled_decision.yaml", "brain-current-action-v1.json"],
    },
    {
        "rank": 2,
        "role": "governance",
        "chat": "e54ddfa8",
        "label": "Governance Specialist",
        "execution_authority": False,
        "writes": ["governance-center-receipt-v1.json"],
    },
    {
        "rank": 3,
        "role": "commercial",
        "chat": "6245d9dd",
        "label": "Commercial Specialist",
        "execution_authority": False,
        "writes": ["goal-progress-v1.json"],
    },
    {
        "rank": 4,
        "role": "brief_specialist",
        "chat": "85dd7cd4",
        "label": "Brief Specialist",
        "execution_authority": False,
        "writes": [],
    },
)

L1_READ_PATHS = (
    "l1-agent-pipeline-wire-v1.json",
    "governance-brain-wire-v1.json",
    "governance-chat-context-v1.json",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _receipt_hint(path: Path) -> dict:
    row = _read_json(path)
    if not row:
        return {"path": str(path), "present": False}
    return {
        "path": str(path.name),
        "present": True,
        "at": row.get("at") or row.get("built_at") or row.get("receipt_id"),
        "ok": row.get("ok"),
    }


def wire_l1_pipeline(*, sync_brain: bool = True) -> dict:
    t0 = datetime.now(timezone.utc)
    steps: list[dict] = []

    sys.path.insert(0, str(SCRIPTS))
    try:
        from brain_governance_wire_v1 import wire_brain_governance  # noqa: WPS433

        brain_wire = wire_brain_governance(sync_brain=sync_brain)
        steps.append(
            {
                "step": "brain_governance_wire",
                "ok": bool(brain_wire.get("ok")),
                "queue_head": (brain_wire.get("queue_head") or {}).get("sa_id"),
            }
        )
    except Exception as exc:
        brain_wire = _read_json(BRAIN_WIRE_PATH)
        steps.append({"step": "brain_governance_wire", "ok": False, "error": str(exc)})

    chat_ctx = _read_json(CHAT_CTX)
    layer_l1 = (chat_ctx.get("layer_stack") or {}).get("L1_agentic_first") or []

    agents = []
    for spec in L1_AGENTS:
        row = dict(spec)
        row["reads"] = [f"~/.sina/{p}" for p in L1_READ_PATHS]
        row["sync_before_reply"] = True
        row["pipeline_script"] = "l1_agent_pipeline_wire_v1.py"
        if spec["role"] == "brain":
            row["hub"] = True
            row["feeds"] = ["governance", "commercial", "brief_specialist"]
        else:
            row["wired_to_brain"] = True
            row["brain_wire_path"] = str(BRAIN_WIRE_PATH)
            row["bind_rule"] = "Read Brain via pipeline l1_wired.shared — never chat-only Brain memory"
        for ctx_row in layer_l1:
            if ctx_row.get("chat") == spec["chat"] or ctx_row.get("role") == spec["role"]:
                row["execution_authority"] = ctx_row.get("execution_authority", spec["execution_authority"])
                break
        agents.append(row)

    brain_hub = {
        "chat": "58148ac9",
        "role": "brain",
        "rank": 1,
        "execution_authority": True,
        "pipeline_script": "l1_agent_pipeline_wire_v1.py",
        "brain_wire_ssot": str(BRAIN_WIRE_PATH),
        "writes": ["brain/reconciled_decision.yaml", "brain-current-action-v1.json"],
        "feeds_l1": ["governance", "commercial", "brief_specialist"],
    }

    l1_to_brain = [
        {
            "rank": a["rank"],
            "role": a["role"],
            "chat": a["chat"],
            "label": a["label"],
            "wired_to_brain": True,
            "reads_via": f"{L1_PIPELINE_PATH.name} → l1_wired.shared",
            "brain_decisions_via": f"{BRAIN_WIRE_PATH.name} → active_decisions[]",
        }
        for a in L1_AGENTS
        if a["role"] != "brain"
    ]

    peer_state = {
        "brain": _receipt_hint(SINA / "brain-current-action-v1.json"),
        "governance": _receipt_hint(SINA / "governance-center-receipt-v1.json"),
        "commercial": _receipt_hint(SINA / "goal-progress-v1.json"),
        "brief": _receipt_hint(SINA / "agent-memory-mirror-v1.json"),
    }

    shared = {
        "brain_authority": True,
        "brain_chat": "58148ac9",
        "active_decisions": brain_wire.get("active_decisions") or [],
        "queue_head": brain_wire.get("queue_head") or {},
        "reconciled_decision": brain_wire.get("reconciled_decision") or {},
        "brain_current_action": brain_wire.get("brain_current_action") or {},
        "specialist_precedence": (chat_ctx.get("layer_stack") or {}).get("specialist_precedence")
        or "governance > commercial > brief",
        "execution_authority_role": "brain",
        "execution_authority_chat": "58148ac9",
        "reconciled_stale": (brain_wire.get("reconciled_decision") or {}).get("stale"),
        "rule": "ALL L1 subordinates wired TO Brain via this pipeline — obey active_decisions[] + queue_head",
    }

    ok = bool(brain_wire.get("ok")) and len(agents) >= 4
    ms = int((datetime.now(timezone.utc) - t0).total_seconds() * 1000)
    row = {
        "ok": ok,
        "schema": "l1-agent-pipeline-wire-v1",
        "at": _now(),
        "ms": ms,
        "pipeline_script": "l1_agent_pipeline_wire_v1.py",
        "wire_paths": {
            "l1_pipeline": str(L1_PIPELINE_PATH),
            "l1_brain_pipeline_alias": str(L1_BRAIN_PIPELINE_ALIAS),
            "brain_wire": str(BRAIN_WIRE_PATH),
            "brain_wire_alias": str(SINA / "brain-wire-v1.json"),
            "chat_context": str(CHAT_CTX),
        },
        "brain_hub": brain_hub,
        "l1_to_brain": {
            "mandatory": True,
            "rule": "ALL L1 (Governance · Commercial · Brief) wired TO Brain through Python pipeline",
            "subordinates": l1_to_brain,
        },
        "l1_wired": {
            "mandatory": True,
            "rule": "ALL L1 wired TO Brain via Python pipeline before reply — Brain hub · chat is input only",
            "agents": agents,
            "peer_state": peer_state,
            "shared": shared,
        },
        "brain_wire_at": brain_wire.get("at"),
        "steps": steps,
        "law": "SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md — ALL L1 wired TO Brain via machine pipeline",
    }

    SINA.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(row, indent=2) + "\n"
    L1_PIPELINE_PATH.write_text(payload, encoding="utf-8")
    L1_BRAIN_PIPELINE_ALIAS.write_text(payload, encoding="utf-8")

    if brain_wire:
        brain_wire["l1_pipeline"] = {
            "ssot": str(L1_PIPELINE_PATH),
            "alias": str(L1_BRAIN_PIPELINE_ALIAS),
            "script": "l1_agent_pipeline_wire_v1.py",
            "at": row["at"],
            "l1_agent_count": len(agents),
            "l1_to_brain_count": len(l1_to_brain),
            "brain_hub": True,
        }
        payload = json.dumps(brain_wire, indent=2) + "\n"
        BRAIN_WIRE_PATH.write_text(payload, encoding="utf-8")
        alias = SINA / "brain-wire-v1.json"
        alias.write_text(payload, encoding="utf-8")

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="L1 → Brain pipeline — wire Gov Commercial Brief TO Brain")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-sync", action="store_true", help="Skip brain snapshot sync inside brain wire")
    args = ap.parse_args()
    row = wire_l1_pipeline(sync_brain=not args.no_sync)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
