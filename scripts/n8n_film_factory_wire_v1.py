#!/usr/bin/env python3
"""n8n ↔ cinematic film factory wire — P1 control plane actions.

Used by: n8n_integration_core.py · n8n_glue_runner_v1.py
Receipt: ~/.sina/enforcement/n8n-film-factory-wire-receipt-v1.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SCRIPTS = ROOT / "scripts"
RECEIPT = SINA / "enforcement" / "n8n-film-factory-wire-receipt-v1.json"
FREEZE_FLAG = SINA / "commercial-film-render-frozen-v1.flag"

LANE_ALIASES = {
    "sourcea": "sourcea",
    "sourcea_commercial": "sourcea",
    "witnessbc": "witnessbc",
    "sourcea_w1": "sourcea",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _write_receipt(action: str, result: dict[str, Any]) -> None:
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(
        json.dumps(
            {
                "schema": "n8n-film-factory-wire-receipt-v1",
                "at": _now(),
                "action": action,
                "ok": bool(result.get("ok")),
                "result": result,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _run_py(script: str, args: list[str], *, timeout: int = 900) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    data: dict[str, Any] = {}
    if out:
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            data = {"raw_stdout": out[:4000]}
    return {
        "exit": proc.returncode,
        "ok": proc.returncode == 0,
        "data": data,
        "stderr": err[-800:] if err else "",
    }


def _normalize_lane(lane: str) -> str:
    key = (lane or "sourcea").strip().lower()
    return LANE_ALIASES.get(key, key)


def _freeze_status() -> dict[str, Any]:
    if not FREEZE_FLAG.is_file():
        return {"frozen": False, "path": str(FREEZE_FLAG)}
    data = _read_json(FREEZE_FLAG)
    return {
        "frozen": True,
        "path": str(FREEZE_FLAG),
        "reason": data.get("reason"),
        "until": data.get("until"),
        "next_action": data.get("next_action"),
        "frozen_at": data.get("frozen_at"),
    }


def film_status() -> dict[str, Any]:
    freeze = _freeze_status()
    critic = _read_json(SINA / "enforcement/commercial-film-critic-circle-receipt-v1.json")
    ship = _read_json(SINA / "enforcement/commercial-film-ship-gate-receipt-v1.json")
    factory = _read_json(SINA / "enforcement/cinematic-film-factory-receipt-v1.json")
    result = {
        "ok": True,
        "freeze": freeze,
        "critic_verdict": critic.get("verdict"),
        "critic_lane": critic.get("lane"),
        "publish_allowed": ship.get("publish_allowed"),
        "ship_gate_lane": ship.get("lane"),
        "factory_now_line": ship.get("factory_now_line") or factory.get("factory_now_line"),
        "receipts": {
            "critic": str(SINA / "enforcement/commercial-film-critic-circle-receipt-v1.json"),
            "ship_gate": str(SINA / "enforcement/commercial-film-ship-gate-receipt-v1.json"),
            "cinematic_factory": str(SINA / "enforcement/cinematic-film-factory-receipt-v1.json"),
        },
        "entries": {
            "ship_gate_sourcea": "sourcea-commercial-film-ship.sh",
            "ship_gate_witnessbc": "witnessbc-commercial-film-ship.sh",
            "compile_witnessbc": "witness-film-build.sh",
            "compile_sourcea": "sourcea-film-build.sh",
        },
    }
    _write_receipt("film_status", result)
    return result


def film_critic(*, lane: str = "all", no_freeze: bool = False) -> dict[str, Any]:
    lane = _normalize_lane(lane) if lane not in ("all", "") else "all"
    args = ["--json", "--lane", lane]
    if no_freeze:
        args.append("--no-freeze")
    run = _run_py("commercial_film_critic_circle_v1.py", args, timeout=120)
    data = run.get("data") or {}
    result = {
        "ok": bool(data.get("ok")),
        "verdict": data.get("verdict"),
        "lane": lane,
        "judgments": data.get("judgments"),
        "freeze_cleared": data.get("freeze_cleared"),
        "render_frozen": data.get("render_frozen"),
        "next_action": data.get("next_action_only"),
        "critic_receipt": str(SINA / "enforcement/commercial-film-critic-circle-receipt-v1.json"),
        "run": run,
    }
    push_film_event_to_intelligence("film_critic", result)
    _write_receipt("film_critic", result)
    return result


def film_compile(*, lane: str = "witnessbc", skip_capture: bool = False) -> dict[str, Any]:
    lane = _normalize_lane(lane)
    if lane not in ("sourcea", "witnessbc"):
        return {"ok": False, "error": f"unsupported_lane:{lane}"}
    freeze = _freeze_status()
    if freeze.get("frozen"):
        result = {
            "ok": False,
            "error": "film_render_frozen",
            "lane": lane,
            "skip_capture": skip_capture,
            "freeze": freeze,
            "note": "Cinematic compile blocked — Playwright capture frozen for Mac health",
        }
        _write_receipt("film_compile", result)
        return result
    env = {"CINEMATIC_SKIP_CAPTURE": "1"} if skip_capture else {}
    proc = subprocess.run(
        ["bash", str(ROOT / "cinematic-film-factory/build.sh"), lane],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=1200,
        env={**dict(__import__("os").environ), **env},
    )
    out = (proc.stdout or "").strip()
    data: dict[str, Any] = {}
    if out:
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            data = {"raw_stdout": out[:4000]}
    result = {
        "ok": proc.returncode == 0,
        "lane": lane,
        "skip_capture": skip_capture,
        "factory_receipt": str(SINA / "enforcement/cinematic-film-factory-receipt-v1.json"),
        "data": data,
        "stderr": (proc.stderr or "")[-800:],
        "note": "Internal tier C compile — not public ship without ship_gate PASS",
    }
    push_film_event_to_intelligence("film_compile", result)
    _write_receipt("film_compile", result)
    return result


def film_ship_gate(
    *,
    lane: str = "sourcea",
    skip_ingest: bool = False,
    no_deploy: bool = False,
) -> dict[str, Any]:
    lane = _normalize_lane(lane)
    args = ["--lane", lane, "--json"]
    if skip_ingest:
        args.append("--skip-ingest")
    if no_deploy:
        args.append("--no-deploy")
    run = _run_py("commercial_film_ship_gate_v1.py", args, timeout=1200)
    data = run.get("data") or {}
    result = {
        "ok": bool(data.get("publish_allowed")),
        "lane": lane,
        "publish_allowed": data.get("publish_allowed"),
        "render_frozen": data.get("render_frozen"),
        "factory_now_line": data.get("factory_now_line"),
        "next_action": data.get("next_action"),
        "steps": data.get("steps"),
        "ship_gate_receipt": str(SINA / "enforcement/commercial-film-ship-gate-receipt-v1.json"),
        "run": run,
    }
    push_film_event_to_intelligence("film_ship_gate", result)
    _write_receipt("film_ship_gate", result)
    return result


def push_film_event_to_intelligence(event: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        sys.path.insert(0, str(SCRIPTS))
        from n8n_intelligence import ingest_webhook_payload  # noqa: WPS433

        body = {
            "action": "ingest",
            "source": "film_factory",
            "event": event,
            "data": {
                "ok": payload.get("ok"),
                "lane": payload.get("lane"),
                "verdict": payload.get("verdict") or payload.get("critic_verdict"),
                "publish_allowed": payload.get("publish_allowed"),
                "factory_now_line": payload.get("factory_now_line"),
                "next_action": payload.get("next_action"),
            },
        }
        return ingest_webhook_payload(body)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def film_factory_queue_note() -> dict[str, Any]:
    """For factory queue sweeper — surface film freeze without killing renders."""
    freeze = _freeze_status()
    status = film_status()
    return {
        "ok": True,
        "film_render_frozen": freeze.get("frozen", False),
        "critic_verdict": status.get("critic_verdict"),
        "publish_allowed": status.get("publish_allowed"),
        "skip_parallel_film_render": freeze.get("frozen", False),
        "next_action": freeze.get("next_action") or status.get("factory_now_line"),
    }


def handle_film_action(body: dict[str, Any] | None = None) -> dict[str, Any]:
    body = body or {}
    action = (body.get("action") or body.get("film_action") or "").strip().lower()
    lane = body.get("lane") or body.get("product") or "sourcea"

    if action in ("film_status", "status"):
        return film_status()
    if action in ("film_critic", "critic"):
        return film_critic(lane=lane, no_freeze=bool(body.get("no_freeze")))
    if action in ("film_compile", "compile"):
        return film_compile(lane=lane, skip_capture=bool(body.get("skip_capture")))
    if action in ("film_ship_gate", "ship_gate", "film_ship"):
        return film_ship_gate(
            lane=lane,
            skip_ingest=bool(body.get("skip_ingest")),
            no_deploy=bool(body.get("no_deploy")),
        )
    if action == "film_run_and_judge":
        compile_res = film_compile(lane=lane, skip_capture=bool(body.get("skip_capture", True)))
        critic_res = film_critic(lane=lane)
        return {
            "ok": bool(critic_res.get("ok")),
            "compile": compile_res,
            "critic": critic_res,
            "factory_now_line": critic_res.get("next_action"),
        }
    return {"ok": False, "error": f"unknown_film_action:{action}", "known": [
        "film_status", "film_critic", "film_compile", "film_ship_gate", "film_run_and_judge"
    ]}
