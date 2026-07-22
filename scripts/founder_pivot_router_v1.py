#!/usr/bin/env python3
"""Founder pivot router — complex founder asks → route_pack on disk (no repeat briefings).

Law: data/founder-pivot-pattern-v1.json
Receipt: ~/.sina/founder-pivot-routing-receipt-v1.json
Wired: brain_intent_gate_v1 · founder_input_cascade_v1 · founder_routing_panel_v1
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "founder-pivot-pattern-v1.json"
RECEIPT = SINA / "founder-pivot-routing-receipt-v1.json"
EVENTS = SINA / "founder-pivot-routing-events.jsonl"
FRESH_SEC = 7 * 86400


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _text_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode()).hexdigest()[:12]


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_ssot() -> dict:
    return _read_json(SSOT)


def match_patterns(text: str, *, ssot: dict | None = None) -> list[dict]:
    spec = ssot or load_ssot()
    low = (text or "").strip()
    if len(low) < 12:
        return []
    matches: list[dict] = []
    for row in spec.get("patterns") or []:
        pid = str(row.get("id") or "")
        for pat in row.get("match") or []:
            try:
                if re.search(pat, low, re.I):
                    matches.append({**row, "matched_pattern": pat})
                    break
            except re.error:
                continue
    matches.sort(key=lambda x: int(x.get("priority") or 999))
    return matches


def best_match(text: str) -> dict | None:
    hits = match_patterns(text)
    return hits[0] if hits else None


def _run_machine(script_name: str, *, timeout: int = 90) -> dict:
    name = script_name.strip()
    if not name.endswith(".py"):
        name = f"{name}.py" if not name.endswith(".sh") else name
    path = SCRIPTS / name
    if not path.is_file():
        return {"ok": False, "script": name, "error": "missing"}
    if name.endswith(".sh"):
        cmd = ["bash", str(path)]
    else:
        cmd = [sys.executable, str(path), "--json"]
        if name == "governance_center_run_v1.py":
            cmd = [sys.executable, str(path), "--tier", "fast", "--json"]
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        tail = ((proc.stdout or "") + (proc.stderr or "")).strip()[-300:]
        return {"ok": proc.returncode == 0, "script": name, "exit": proc.returncode, "tail": tail}
    except subprocess.TimeoutExpired:
        return {"ok": False, "script": name, "error": "timeout"}
    except Exception as exc:
        return {"ok": False, "script": name, "error": str(exc)}


def _age_sec(ts: str | None) -> float | None:
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds())
    except (TypeError, ValueError):
        return None


def active_pivot_receipt(*, max_age_sec: int = FRESH_SEC) -> dict:
    rec = _read_json(RECEIPT)
    if rec.get("schema") != "founder-pivot-routing-receipt-v1" or not rec.get("matched"):
        return {}
    age = _age_sec(rec.get("at"))
    if age is not None and age > max_age_sec:
        return {}
    return rec


def route_founder_pivot(
    text: str,
    *,
    source: str = "founder",
    run_machines: bool = False,
    write: bool = True,
) -> dict:
    t0 = time.monotonic()
    text = (text or "").strip()
    hit = best_match(text)
    if not hit:
        row = {
            "ok": True,
            "matched": False,
            "schema": "founder-pivot-routing-receipt-v1",
            "at": _now(),
            "source": source,
            "text_hash": _text_hash(text) if text else "",
            "text_preview": text[:160] if text else "",
            "law": "No pivot pattern — normal intent gate + cascade",
        }
        if write:
            SINA.mkdir(parents=True, exist_ok=True)
            RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    machine_runs: list[dict] = []
    if run_machines:
        for script in hit.get("machines_to_run") or []:
            if script == "governance_center_run_v1.py":
                machine_runs.append(_run_machine(script, timeout=120))
            elif script in ("thread_room_run_v1.py",):
                machine_runs.append(_run_machine(script, timeout=120))
            else:
                machine_runs.append(_run_machine(str(script), timeout=60))

    ms = int((time.monotonic() - t0) * 1000)
    row = {
        "ok": True,
        "matched": True,
        "schema": "founder-pivot-routing-receipt-v1",
        "at": _now(),
        "ms": ms,
        "source": source,
        "text_hash": _text_hash(text),
        "text_preview": text[:160],
        "pivot_id": hit.get("id"),
        "pivot_label": hit.get("label"),
        "matched_pattern": hit.get("matched_pattern"),
        "priority": hit.get("priority"),
        "route_pack": hit.get("route_pack") or {},
        "routing_override": hit.get("routing_override") or {},
        "work_template": hit.get("work_template"),
        "inject_line": hit.get("inject_line"),
        "machines_to_run": hit.get("machines_to_run") or [],
        "machine_runs": machine_runs if run_machines else [],
        "founder_one_tap": (hit.get("routing_override") or {}).get("founder_action"),
        "law": "Complex founder pivot on disk — agents read receipt; founder does not repeat",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        with EVENTS.open("a", encoding="utf-8") as f:
            f.write(json.dumps({**row, "event": "PIVOT_ROUTE"}, ensure_ascii=False) + "\n")
    return row


def apply_routing_override(active: dict) -> dict:
    """Merge pivot receipt into routing panel active_route when fresh."""
    rec = active_pivot_receipt()
    if not rec:
        return active
    override = rec.get("routing_override") or {}
    merged = dict(active)
    if override.get("primary"):
        merged["primary"] = override["primary"]
        merged["pivot_primary"] = True
    if override.get("secondary"):
        merged["secondary"] = override["secondary"]
    if override.get("founder_action"):
        merged["founder_action"] = override["founder_action"]
    merged["pivot_id"] = rec.get("pivot_id")
    merged["pivot_label"] = rec.get("pivot_label")
    merged["inject_line"] = rec.get("inject_line")
    merged["work_template"] = rec.get("work_template")
    return merged


def panel_line_suffix() -> str:
    rec = active_pivot_receipt()
    if not rec:
        return ""
    pid = rec.get("pivot_id") or "?"
    return f" · pivot={pid}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Founder pivot pattern router")
    ap.add_argument("--text", default="", help="Founder message to classify")
    ap.add_argument("--source", default="cli")
    ap.add_argument("--run-machines", action="store_true", help="Execute machines_to_run (slow)")
    ap.add_argument("--match-only", action="store_true")
    ap.add_argument("--show", action="store_true", help="Print active receipt")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.show:
        row = _read_json(RECEIPT) or active_pivot_receipt()
        print(json.dumps(row or {"matched": False}, indent=2))
        return 0

    if args.match_only:
        hits = match_patterns(args.text)
        row = {"matches": [{"id": h.get("id"), "label": h.get("label")} for h in hits]}
        print(json.dumps(row, indent=2))
        return 0

    row = route_founder_pivot(
        args.text,
        source=args.source,
        run_machines=args.run_machines,
        write=bool(args.text),
    )
    if args.json or True:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
