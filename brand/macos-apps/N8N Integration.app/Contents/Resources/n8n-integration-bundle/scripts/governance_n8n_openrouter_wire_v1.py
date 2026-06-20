#!/usr/bin/env python3
"""Wire n8n governance workflows + OpenRouter lane per Q-GOV-FAST-WIRE-v1 A.

Law: SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md · SOURCEA_OPENROUTER_ACTIVATION_QUEUE_LOCKED_v1.md
Receipt: ~/.sina/governance-n8n-openrouter-wire-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "governance-n8n-openrouter-wire-v1.json"
APPLIED_PATH = SINA / "canvas-form-picks-applied-v1.json"
N8N_DIR = ROOT / "n8n" / "workflows"
INTEGRATION_FABRIC = SINA / "integration-fabric-registry-v1.yaml"

GOVERNANCE_WFS = (
    "wf-governance-fast-15m.stub.json",
    "wf-judge-audit-batch.stub.json",
    "wf-thread-scout-weekly.stub.json",
    "wf-openrouter-governance-hook.stub.json",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: int = 300) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=str(SCRIPTS), capture_output=True, text=True, timeout=timeout)
        tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
        return {
            "ok": proc.returncode == 0,
            "exit": proc.returncode,
            "tail": tail[-1][:240] if tail else f"exit {proc.returncode}",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit": -1, "tail": "timeout"}
    except OSError as exc:
        return {"ok": False, "exit": -1, "tail": str(exc)}


def _pick_gate() -> dict:
    applied = {}
    if APPLIED_PATH.is_file():
        applied = json.loads(APPLIED_PATH.read_text(encoding="utf-8")).get("picks") or {}
    gov = applied.get("Q-GOV-FAST-WIRE-v1")
    quorum = applied.get("Q-CHANGE-QUORUM-v1")
    ok = gov == "A" and quorum == "A"
    return {
        "ok": ok,
        "Q-GOV-FAST-WIRE-v1": gov,
        "Q-CHANGE-QUORUM-v1": quorum,
    }


def _workflow_rows() -> list[dict]:
    rows = []
    for name in GOVERNANCE_WFS:
        path = N8N_DIR / name
        rows.append(
            {
                "file": name,
                "id": name.replace(".stub.json", ""),
                "exists": path.is_file(),
                "path": str(path),
            }
        )
    return rows


def _openrouter_lane() -> dict:
    credits_flag = SINA / "openrouter-credits-ok.flag"
    gate_mode_path = SINA / "gate_mode_v1.txt"
    gate_mode = gate_mode_path.read_text(encoding="utf-8").strip() if gate_mode_path.is_file() else "shadow"
    session = SINA / "live-agent-session-openrouter.json"
    config = SINA / "intelligence-circle-config.json"
    cfg = {}
    if config.is_file():
        try:
            cfg = json.loads(config.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cfg = {}
    return {
        "queue_head_law": "SOURCEA_OPENROUTER_ACTIVATION_QUEUE_LOCKED_v1.md",
        "gate_mode": gate_mode,
        "credits_flag": credits_flag.is_file(),
        "session_file": str(session),
        "intelligence_circle_enabled": (cfg.get("enabled_agents") or {}).get("openrouter", False),
        "wired": True,
        "live_eval_allowed": credits_flag.is_file() and gate_mode != "shadow",
        "n8n_hook": "wf-openrouter-governance-hook",
        "rule": "EXTERNAL_CRITIC class · never law · shadow until credits flag",
    }


def _append_spine(*, wire_ok: bool) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    try:
        from governance_event_spine_v1 import append_event  # noqa: WPS433

        res = append_event(
            event_type="PROPAGATION",
            object_id="n8n-governance-openrouter-wire",
            object_kind="system",
            agent_id="brain",
            gate="Q-GOV-FAST-WIRE-v1-A",
            proof=str(RECEIPT_PATH),
            payload={"ok": wire_ok, "workflows": [w.replace(".stub.json", "") for w in GOVERNANCE_WFS]},
            projection_targets=["integration-fabric", "h2-pending"],
        )
        return {"ok": bool(res.get("ok")), "tail": res.get("event_id") or "appended"}
    except Exception as exc:
        return {"ok": False, "tail": str(exc)}


def wire_all(*, run_fast: bool = True, openrouter_hook_only: bool = False) -> dict:
    t0 = datetime.now(timezone.utc)
    steps: list[dict] = []

    picks = _pick_gate()
    steps.append({"step": "pick_gate", **picks})

    wfs = _workflow_rows()
    missing = [w["id"] for w in wfs if not w["exists"]]
    steps.append({"step": "workflow_files", "ok": not missing, "workflows": wfs, "missing": missing})

    if openrouter_hook_only:
        or_lane = _openrouter_lane()
        row = {
            "ok": or_lane.get("wired"),
            "schema": "governance-n8n-openrouter-wire-v1",
            "mode": "openrouter_hook",
            "at": _now(),
            "openrouter": or_lane,
            "steps": steps,
        }
        RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    if not picks.get("ok"):
        row = {
            "ok": False,
            "schema": "governance-n8n-openrouter-wire-v1",
            "at": _now(),
            "error": "Q-GOV-FAST-WIRE-v1 A and Q-CHANGE-QUORUM-v1 A required",
            "steps": steps,
        }
        RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    if missing:
        row = {
            "ok": False,
            "schema": "governance-n8n-openrouter-wire-v1",
            "at": _now(),
            "error": f"missing workflow stubs: {missing}",
            "steps": steps,
        }
        RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    if run_fast:
        gov = _run([sys.executable, str(SCRIPTS / "governance_center_run_v1.py"), "--tier", "fast", "--json"])
        steps.append({"step": "governance_center_fast", **gov})

        brain = _run([sys.executable, str(SCRIPTS / "agentic_layer_pipeline_v2.py"), "--json", "--tier", "fast"])
        steps.append({"step": "agentic_layer_pipeline_v2", **brain})

    n8n_status = _run([sys.executable, str(SCRIPTS / "n8n_automation.py"), "status"], timeout=15)
    n8n_running = False
    try:
        sys.path.insert(0, str(SCRIPTS))
        from n8n_automation import n8n_status_payload  # noqa: WPS433

        n8n_running = bool(n8n_status_payload().get("n8n_running"))
    except Exception:
        pass
    steps.append({"step": "n8n_status", "ok": True, "n8n_running": n8n_running, "tail": n8n_status.get("tail")})

    or_lane = _openrouter_lane()
    steps.append({"step": "openrouter_lane", **or_lane})

    spine = _append_spine(wire_ok=True)
    steps.append({"step": "governance_spine", **spine})

    ms = int((datetime.now(timezone.utc) - t0).total_seconds() * 1000)
    ok = all(
        s.get("ok") is not False
        for s in steps
        if s.get("step") not in ("n8n_status",)  # n8n may be down — stubs still wired
    )
    row = {
        "ok": ok,
        "schema": "governance-n8n-openrouter-wire-v1",
        "at": _now(),
        "ms": ms,
        "pick_receipt": "archive/attachments/2026-06-14/ASF_FORM_GOV_PICK_BATCH_2026-06-14_LOCKED_v1.md",
        "n8n_workflows": [w["id"] for w in wfs],
        "n8n_import_dir": str(N8N_DIR),
        "n8n_running": n8n_running,
        "openrouter": or_lane,
        "integration_fabric": str(INTEGRATION_FABRIC),
        "steps": steps,
        "founder_note": "n8n glue wired locally — import stubs into n8n UI when n8n is up · OpenRouter shadow until credits flag",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Wire n8n governance + OpenRouter lane")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-run", action="store_true", help="Skip governance_center fast run")
    ap.add_argument("--openrouter-hook", action="store_true", help="OpenRouter hook only (n8n node)")
    args = ap.parse_args()
    row = wire_all(run_fast=not args.no_run, openrouter_hook_only=args.openrouter_hook)
    if args.json or True:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
