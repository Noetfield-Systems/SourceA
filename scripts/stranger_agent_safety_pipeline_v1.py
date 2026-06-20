#!/usr/bin/env python3
"""Stranger agent safety control + identifier pipeline (SASCIP v1.2).

Stages: IDENTIFY → CLASSIFY → CONTROL → PROVE → SERVE

Law: docs/STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md
Receipt: ~/.sina/stranger-agent-admission-receipt-v1.json
Monitor: ~/.sina/stranger-agent-monitor-v1.json
"""
from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

from stranger_agent_safety_lib_v1 import (
    RECEIPT_PATH,
    apply_control,
    build_fingerprint,
    classify_agent,
    load_config,
    record_admission,
    resolve_cross_lane_agent,
    run_watch_pulse,
    verify_external_admit,
    write_monitor_projection,
)

ROOT = Path(__file__).resolve().parents[1]
LAW_DOC = "docs/STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md"
SCHEMA = "stranger-agent-admission-v1.2"


def run_pipeline(
    *,
    agent_id: str = "cursor",
    role_hint: str = "any",
    workspace_root: str | Path | None = None,
    explicit_order: str = "",
    chat_id: str = "",
    record: bool = True,
    external_orchestrator: str = "",
    external_token: str = "",
) -> dict:
    cfg = load_config()
    if not cfg.get("enabled", True):
        return {
            "schema": SCHEMA,
            "ok": True,
            "skipped": True,
            "reason": "pipeline_disabled",
        }

    stages: list[dict] = []
    pipeline_id = f"SASCIP-{uuid.uuid4().hex[:12]}"

    if external_orchestrator:
        ext = verify_external_admit(
            orchestrator_id=external_orchestrator,
            token=external_token,
            agent_id=agent_id,
        )
        stages.append({"stage": "EXTERNAL_ADMIT", "ok": ext.get("ok"), **ext})
        if not ext.get("ok"):
            return {
                "schema": SCHEMA,
                "pipeline_id": pipeline_id,
                "ok": False,
                "stages": stages,
                "reason": ext.get("reason"),
            }

    fp = build_fingerprint(
        agent_id=agent_id,
        role_hint=role_hint,
        workspace_root=workspace_root,
        explicit_order=explicit_order,
        chat_id=chat_id,
    )
    stages.append(
        {
            "stage": "IDENTIFY",
            "ok": True,
            "fingerprint_id": fp.get("fingerprint_id"),
            "mcp_servers": (fp.get("mcp") or {}).get("server_count"),
            "git_branch": (fp.get("git") or {}).get("branch"),
        }
    )

    cls = classify_agent(fp, explicit_order=explicit_order)
    stages.append(
        {
            "stage": "CLASSIFY",
            "ok": True,
            "trust_tier": cls.get("trust_tier"),
            "resolved_agent_id": cls.get("resolved_agent_id"),
            "stranger": cls.get("stranger"),
            "reason": cls.get("reason"),
            "risk_score": (cls.get("risk") or {}).get("score"),
            "risk_level": (cls.get("risk") or {}).get("level"),
        }
    )

    control = apply_control(cls, fp)
    stages.append(
        {
            "stage": "CONTROL",
            "ok": control.get("ok"),
            "violations": control.get("violations") or [],
            "warnings": control.get("warnings") or [],
            "cross_lane_writes": control.get("cross_lane_writes"),
            "risk_score": control.get("risk_score"),
        }
    )

    ok = bool(control.get("ok"))
    if cfg.get("quarantine_strangers") and cls.get("stranger") and not explicit_order.strip():
        ok = False
        control.setdefault("violations", []).append("stranger_quarantine_active")

    gate_id = (fp.get("session_gate") or {}).get("gate_id")
    if record:
        record_admission(fp, cls, control, gate_id=gate_id)

    inject = {
        "resolved_agent_id": cls.get("resolved_agent_id"),
        "trust_tier": cls.get("trust_tier"),
        "stranger": cls.get("stranger"),
        "cross_lane_policy": control.get("cross_lane_writes"),
        "risk_score": (cls.get("risk") or {}).get("score"),
        "risk_level": (cls.get("risk") or {}).get("level"),
        "one_line": (
            f"sascip · {cls.get('resolved_agent_id')} · {cls.get('trust_tier')} · "
            f"risk {(cls.get('risk') or {}).get('score', 0)} · "
            f"{'QUARANTINE' if cls.get('stranger') else 'ADMIT'}"
        ),
    }

    receipt = {
        "schema": SCHEMA,
        "version": cfg.get("version") or "1.2.0",
        "pipeline_id": pipeline_id,
        "ok": ok,
        "at": fp.get("at"),
        "law_doc": LAW_DOC,
        "stages": stages,
        "fingerprint": fp,
        "classification": cls,
        "control": control,
        "inject": inject,
        "receipt_path": str(RECEIPT_PATH),
    }

    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)

    monitor = write_monitor_projection(receipt)
    stages.append({"stage": "SERVE", "ok": True, "monitor_path": str(Path.home() / ".sina/stranger-agent-monitor-v1.json"), "one_line": inject.get("one_line")})
    receipt["stages"] = stages
    receipt["monitor"] = {"path": str(Path.home() / ".sina/stranger-agent-monitor-v1.json"), "one_line": monitor.get("one_line")}

    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    try:
        from governance_event_spine_v1 import append_event  # noqa: WPS433

        append_event(
            event_type="STRANGER_AGENT_ADMISSION",
            object_id=f"stranger_agent:{pipeline_id}",
            object_kind="system",
            agent_id=str(cls.get("resolved_agent_id") or agent_id),
            law_id="STRANGER_AGENT_SAFETY_v1.2",
            skill_id="stranger-agent-safety",
            validator_set=["validate-stranger-agent-safety-v1.sh"],
            affected_objects=[f"receipt:{RECEIPT_PATH.name}"],
            payload={
                "ok": ok,
                "trust_tier": cls.get("trust_tier"),
                "stranger": cls.get("stranger"),
                "fingerprint_id": fp.get("fingerprint_id"),
                "risk_score": (cls.get("risk") or {}).get("score"),
            },
            projection_targets=["hub", "monitor", "mac_health"],
            gate="stranger_agent_safety_pipeline_v1",
            proof=str(RECEIPT_PATH),
            status="committed" if ok else "quarantine",
        )
    except Exception:
        pass

    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Stranger agent safety control + identifier pipeline v1.2")
    ap.add_argument("--agent", default="cursor", help="Declared agent id")
    ap.add_argument("--role", default="any", help="Role hint (brain, worker, any, …)")
    ap.add_argument("--workspace", default="", help="Workspace root override")
    ap.add_argument("--explicit-order", default="", help="Founder message for elevation check")
    ap.add_argument("--chat-id", default="", help="Optional chat id fragment")
    ap.add_argument("--resolve-only", action="store_true", help="Resolve cross-lane agent only")
    ap.add_argument("--watch", action="store_true", help="Run continuous watch pulse")
    ap.add_argument("--external-orchestrator", default="", help="Partner orchestrator id")
    ap.add_argument("--external-token", default="", help="Partner admission token")
    ap.add_argument("--no-record", action="store_true", help="Skip registry write")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.watch:
        out = run_watch_pulse()
        if args.json:
            print(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            print(f"WATCH checked={out.get('checked')} strangers={out.get('active_strangers')}")
        return 0 if out.get("ok") else 1

    ws = args.workspace or None
    if args.resolve_only:
        row = resolve_cross_lane_agent(
            args.agent,
            role_hint=args.role,
            workspace_root=ws,
            explicit_order=args.explicit_order,
        )
        if args.json:
            print(json.dumps(row, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(row))
        return 0 if row.get("ok") else 1

    receipt = run_pipeline(
        agent_id=args.agent,
        role_hint=args.role,
        workspace_root=ws,
        explicit_order=args.explicit_order,
        chat_id=args.chat_id,
        record=not args.no_record,
        external_orchestrator=args.external_orchestrator,
        external_token=args.external_token,
    )
    if args.json:
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
    else:
        inj = receipt.get("inject") or {}
        print(f"SASCIP ok={receipt.get('ok')} {inj.get('one_line', '')}")
        print(f"RECEIPT={RECEIPT_PATH}")
    return 0 if receipt.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
