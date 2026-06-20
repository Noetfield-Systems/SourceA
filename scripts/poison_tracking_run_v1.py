#!/usr/bin/env python3
"""Poison Tracking Method — one command SCAN→REGISTER.

Law: SOURCEA_POISON_TRACKING_METHOD_STRATEGY_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
REGISTRY = SINA / "poison-tracking-registry-v1.jsonl"
LATEST = SINA / "poison-tracking-latest-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_meta() -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "governance_meta_audit_v1.py"), "--tier", "fast", "--json"],
        capture_output=True,
        text=True,
        timeout=240,
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "parse_error": proc.stdout[:500]}


def _run_spine() -> bool:
    proc = subprocess.run(
        ["bash", str(SCRIPTS / "validate-daily-spine-v1.sh")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=300,
    )
    return proc.returncode == 0


def _classify(meta: dict, *, symptom: str) -> list[str]:
    classes: list[str] = []
    sym = symptom.lower()
    failures = meta.get("failures") or []
    ids = {f.get("id") for f in failures}

    if not meta.get("ok"):
        classes.append("P5")
    if "museum" in ids or "prompt_feed" in ids or "museum_founder_hero" in ids:
        classes.extend(["P0", "P2"])
    if "brain_not_command_data_ssot" in ids:
        classes.append("P1")
    if "memory_mirror" in ids:
        classes.append("P2")
    if "judge_temporal" in ids:
        classes.append("P6")
    if any(x in sym for x in ("both", "dual", "brain and gov")):
        if "P6" not in classes:
            classes.append("P6")
    if any(x in sym for x in ("erased", "museum", "archive")):
        if "P4" not in classes:
            classes.append("P4")
    if any(x in sym for x in ("not present locally", "still logged")):
        if "P5" not in classes:
            classes.append("P5")
    if not classes and not meta.get("ok"):
        classes.append("P0")
    if meta.get("ok") and not classes:
        classes.append("CLEAR")
    return sorted(set(classes))


def run_ptm(*, symptom: str = "", write: bool = True) -> dict:
    meta = _run_meta()
    spine_ok = _run_spine()
    classes = _classify(meta, symptom=symptom)
    event = {
        "schema": "poison-tracking-event-v1",
        "id": f"PTM-{uuid.uuid4().hex[:12]}",
        "at": _now(),
        "symptom": symptom or "(scheduled scan)",
        "classes": classes,
        "meta_audit_ok": bool(meta.get("ok")),
        "daily_spine_ok": spine_ok,
        "failure_count": meta.get("failure_count", len(meta.get("failures") or [])),
        "failures": meta.get("failures") or [],
        "ok": bool(meta.get("ok")) and spine_ok,
        "law": "SOURCEA_POISON_TRACKING_METHOD_STRATEGY_LOCKED_v1.md",
        "closed": bool(meta.get("ok")) and spine_ok,
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        with REGISTRY.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        LATEST.write_text(json.dumps(event, indent=2) + "\n", encoding="utf-8")
    return event


def main() -> int:
    ap = argparse.ArgumentParser(description="Poison Tracking Method — one command")
    ap.add_argument("--symptom", default="", help="Founder symptom text")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    event = run_ptm(symptom=args.symptom, write=not args.no_write)
    if args.json:
        print(json.dumps(event, indent=2))
    else:
        print(f"PTM: ok={event['ok']} classes={event['classes']} failures={event['failure_count']}")
    return 0 if event.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
