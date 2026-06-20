"""Eval-1 — packet-driven vs raw structural benchmark (no live LLM required)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
TASKS_PATH = Path(__file__).resolve().parent / "tasks.json"
REPORT_PATH = Path.home() / ".sina" / "eval_packet_v1_report.json"
SCHEMA = "eval-packet-v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_tasks() -> list[dict]:
    data = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    return list(data.get("tasks") or [])


def _score_raw() -> dict[str, Any]:
    from pre_llm.context_packet.schema import empty_packet_template, validate_packet  # noqa: WPS433

    pkt = empty_packet_template(task_id="eval-raw")
    check = validate_packet(pkt)
    return {
        "arm": "raw",
        "readiness_score": check.get("readiness_score"),
        "gate_eligible": check.get("gate_eligible"),
        "missing_for_gate": check.get("missing_for_gate"),
    }


def _score_packet(prompt: str, task_id: str) -> dict[str, Any]:
    from pre_llm.context_assembly.assembly_engine import run_context_assembly  # noqa: WPS433

    assembled = run_context_assembly(text=prompt, task_id=task_id, force_refresh=False)
    if assembled.get("ok") and assembled.get("validation"):
        val = assembled["validation"]
    else:
        import model_dispatch  # noqa: WPS433

        prep = model_dispatch.prepare_packet(task_id=task_id, query_text=prompt)
        val = prep.get("validation") or {}
    return {
        "arm": "packet",
        "readiness_score": val.get("readiness_score"),
        "gate_eligible": val.get("gate_eligible"),
        "missing_for_gate": val.get("missing_for_gate"),
        "populated_sections": val.get("populated_sections"),
    }


def run_eval(*, write_report: bool = True) -> dict[str, Any]:
    tasks = _load_tasks()
    rows: list[dict] = []
    packet_wins = 0
    for t in tasks:
        tid = t.get("id") or "task"
        prompt = t.get("prompt") or ""
        raw = _score_raw()
        pkt = _score_packet(prompt, tid)
        pkt_score = float(pkt.get("readiness_score") or 0)
        raw_score = float(raw.get("readiness_score") or 0)
        win = pkt_score > raw_score or (
            bool(pkt.get("gate_eligible")) and not bool(raw.get("gate_eligible"))
        )
        if win:
            packet_wins += 1
        rows.append(
            {
                "id": tid,
                "category": t.get("category"),
                "prompt": prompt[:120],
                "raw": raw,
                "packet": pkt,
                "packet_wins": win,
            }
        )
    n = max(len(rows), 1)
    pct = int(round(100 * packet_wins / n))
    out = {
        "ok": pct >= 80,
        "schema": SCHEMA,
        "generated_at": _now(),
        "path": str(REPORT_PATH),
        "task_count": len(rows),
        "packet_wins": packet_wins,
        "packet_win_pct": pct,
        "threshold_pct": 80,
        "summary": f"Packet arm wins on {packet_wins}/{len(rows)} tasks ({pct}%)",
        "rows": rows,
        "producer": "Eval-1",
        "api": "/api/eval-packet-v1",
    }
    if write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def hub_payload() -> dict[str, Any]:
    if REPORT_PATH.is_file():
        try:
            return {**json.loads(REPORT_PATH.read_text(encoding="utf-8")), "from_disk": True}
        except (json.JSONDecodeError, OSError):
            pass
    return run_eval(write_report=True)
