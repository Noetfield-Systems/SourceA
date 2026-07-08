#!/usr/bin/env python3
"""Gate-aware Brain refresh — less dirty tree, smarter corpus updates."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json"


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=600)


def _py(script: str, *extra: str) -> subprocess.CompletedProcess[str]:
    return _run([sys.executable, str(ROOT / "scripts" / script), *extra])


def main() -> int:
    ap = argparse.ArgumentParser(description="Smart Brain refresh (skip/light/full via gate)")
    ap.add_argument("--force", choices=["skip", "light", "full"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    gate_cmd = [sys.executable, str(ROOT / "scripts" / "brain_refresh_gate_v1.py"), "--json"]
    if args.force:
        gate_cmd.extend(["--force", args.force])
    gate_proc = _run(gate_cmd)
    try:
        gate = json.loads(gate_proc.stdout)
    except json.JSONDecodeError:
        gate = {"action": "light", "reason": "gate_parse_failed"}

    action = str(gate.get("action") or "light")
    steps: list[str] = []

    if action == "skip" and BUNDLE.is_file():
        payload = {
            "ok": True,
            "action": "skip",
            "reason": gate.get("reason"),
            "bundle": str(BUNDLE.relative_to(ROOT)),
            "steps": ["gate_skip"],
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"SKIP — brain fresh enough ({gate.get('reason')})")
        return 0

    _py("distill_brain_public_rules_v1.py")
    steps.append("rules")

    if action == "full":
        _py("distill_brain_live_sources_v1.py", "--json")
        steps.append("live_sources_full")
    else:
        _py("distill_brain_live_sources_v1.py", "--light", "--json")
        steps.append("live_sources_light")

    _py("distill_docs_to_brain_knowledge_v1.py")
    steps.append("docs")
    _py("distill_www_to_brain_knowledge_v1.py")
    steps.append("manifest_www")

    sync = _py("sync_brain_chat_knowledge_v1.py", "--json")
    sync_row: dict = {}
    try:
        sync_row = json.loads(sync.stdout)
    except json.JSONDecodeError:
        sync_row = {"ok": sync.returncode == 0}

    save_gate = _run(
        [sys.executable, str(ROOT / "scripts" / "brain_refresh_gate_v1.py"), "--save", "--json"]
    )

    payload = {
        "ok": bool(sync_row.get("ok", sync.returncode == 0)),
        "action": action,
        "reason": gate.get("reason"),
        "steps": steps,
        "sync": sync_row,
        "gate_saved": save_gate.returncode == 0,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        chunks = sync_row.get("chunk_count", "?")
        print(f"OK smart refresh ({action}) — {chunks} chunks · steps: {', '.join(steps)}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
