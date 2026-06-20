#!/usr/bin/env bash
# validate-active-now-factory-now-v1.sh — ACTIVE_NOW blocker must match factory-now (AS-08)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from factory_control_v1 import load_factory_now

active = Path("ACTIVE_NOW.md")
if not active.is_file():
    print("FAIL: ACTIVE_NOW.md missing")
    sys.exit(1)

fn = load_factory_now()
text = active.read_text(encoding="utf-8")
line = str(fn.get("line") or "")
queue = str(fn.get("queue_sa") or "")

if queue and queue not in text:
    print(f"FAIL: ACTIVE_NOW missing queue_sa {queue}")
    sys.exit(1)

if "factory-now" not in text.lower() and line and line[:24] not in text:
    print("FAIL: ACTIVE_NOW blocker does not cite factory-now line")
    sys.exit(1)

mode = str(fn.get("mode") or "FREEZE")
if fn.get("kill_flag") and "FREEZE" not in text.upper():
    print("FAIL: kill_flag ON but ACTIVE_NOW missing FREEZE")
    sys.exit(1)

print("OK: validate-active-now-factory-now-v1")
PY
