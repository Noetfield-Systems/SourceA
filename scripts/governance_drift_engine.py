#!/usr/bin/env python3
"""Governance drift engine — aggregate audit sensors into scored SSOT report."""
from __future__ import annotations

import json
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
SCRIPTS = SOURCE_A / "scripts"
SINA_HOME = Path.home() / ".sina"
REPORT_PATH = SINA_HOME / "governance_drift_report_v1.json"
EVENTS_PATH = SINA_HOME / "agent-governance-events.jsonl"
LAW_DOC = "GOVERNANCE_DRIFT_ENGINE_LOCKED_v1.md"
HUB_PORT = 13020


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_script(name: str) -> dict:
    path = SCRIPTS / name
    if not path.is_file():
        return {"id": name, "ok": False, "score": 0, "detail": "missing script"}
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(SCRIPTS),
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        ok = proc.returncode == 0
        return {
            "id": name,
            "ok": ok,
            "score": 100 if ok else 0,
            "detail": out.strip().splitlines()[-1][:240] if out.strip() else f"exit {proc.returncode}",
        }
    except subprocess.TimeoutExpired:
        return {"id": name, "ok": False, "score": 0, "detail": "timeout"}
    except OSError as e:
        return {"id": name, "ok": False, "score": 0, "detail": str(e)}


def _hub_liveness() -> dict:
    try:
        with socket.create_connection(("127.0.0.1", HUB_PORT), timeout=1.5):
            return {"id": "GD-OPS", "ok": True, "score": 100, "detail": f":{HUB_PORT} listening"}
    except OSError as e:
        return {"id": "GD-OPS", "ok": False, "score": 0, "detail": str(e)}


def _drift_json_sensor() -> dict:
    p = SOURCE_A / "sina-bowl" / "DRIFT.json"
    if not p.is_file():
        return {"id": "GD-BOWL", "ok": True, "score": 100, "detail": "no DRIFT.json"}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("items") or data.get("drift") or []
        n = len(items)
        score = max(0, 100 - n * 15)
        return {"id": "GD-BOWL", "ok": n == 0, "score": score, "detail": f"{n} drift item(s) in DRIFT.json"}
    except json.JSONDecodeError:
        return {"id": "GD-BOWL", "ok": False, "score": 0, "detail": "invalid DRIFT.json"}


def _l8_semantic_sensor() -> dict:
    """P05 Voyage + SHA-256 hybrid — semantic must be true when key in vault (INCIDENT-035 / COMM-PARTNER)."""
    try:
        sys.path.insert(0, str(SCRIPTS / "pre_llm" / "vector_retrieval"))
        from embedding_provider import provider_payload  # noqa: WPS433

        payload = provider_payload()
        semantic = payload.get("semantic") is True
        mode = str(payload.get("mode") or "")
        score = 100 if semantic else 70 if mode == "hash_local" else 0
        detail = f"mode={mode} semantic={payload.get('semantic')} model={payload.get('model')}"
        return {"id": "GD-L8", "ok": semantic, "score": score, "detail": detail}
    except Exception as exc:
        return {"id": "GD-L8", "ok": False, "score": 0, "detail": str(exc)}


def run_drift_report(*, write_ssot: bool = True) -> dict:
    sensors = [
        _run_script("audit_hub_source_alignment.py"),
        _run_script("audit_agent_governance_e2e.py"),
        _run_script("audit_essentials_nav.py"),
        _run_script("audit_private_agent_pages.py"),
        _drift_json_sensor(),
        _hub_liveness(),
        _l8_semantic_sensor(),
    ]
    total = sum(s["score"] for s in sensors)
    max_score = len(sensors) * 100
    aggregate = round(100 * total / max_score) if max_score else 0
    status = "ok" if aggregate >= 85 and all(s["ok"] for s in sensors[:4]) else "needs_review"
    report = {
        "ok": True,
        "schema": "governance_drift_v1",
        "built_at": _now(),
        "aggregate_score": aggregate,
        "status": status,
        "sensors": sensors,
        "ssot_path": str(REPORT_PATH),
        "law_doc": LAW_DOC,
    }
    if write_ssot:
        SINA_HOME.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        try:
            from agent_governance_events import log_governance_event  # noqa: WPS433

            log_governance_event(
                "governance_drift",
                detail=f"score={aggregate} status={status}",
                extra={"aggregate_score": aggregate, "sensor_count": len(sensors)},
            )
        except Exception:
            pass
    return report


def drift_payload() -> dict:
    if REPORT_PATH.is_file():
        try:
            data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
            data["ok"] = True
            return data
        except json.JSONDecodeError:
            pass
    return run_drift_report(write_ssot=True)


def handle_drift_action(body: dict) -> dict:
    action = (body.get("action") or "report").strip().lower()
    if action in ("report", "run", "refresh", ""):
        return run_drift_report(write_ssot=True)
    if action == "get":
        return drift_payload()
    return {"ok": False, "error": f"unknown action: {action}"}
