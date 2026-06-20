#!/usr/bin/env bash
# sa-0515 — PROGRAM_PROGRESS signals_auto.wire matches locked_plan.json wire_summary
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0515-program-progress-wire-summary_LOCKED_v1.md"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }
python3 - <<'PY'
import json
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("upp", Path("scripts/update-program-progress.py"))
upp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upp)

expected = upp.wire_summary()
if expected.get("error"):
    raise SystemExit(f"FAIL: wire_summary error {expected['error']}")

pp = json.loads(Path("PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
wire = (pp.get("signals_auto") or {}).get("wire") or {}
for key in ("physical_iphone", "full_m8_iphone", "g3_tailscale", "current_phase"):
    if wire.get(key) != expected.get(key):
        raise SystemExit(f"FAIL: wire.{key} pp={wire.get(key)!r} expected={expected.get(key)!r}")
if not (pp.get("signals_auto") or {}).get("synced_at"):
    raise SystemExit("FAIL: signals_auto.synced_at missing")
print("OK: validate-program-progress-wire-summary-v1 · sa-0515")
PY
