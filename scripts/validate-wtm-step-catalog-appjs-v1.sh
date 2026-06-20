#!/usr/bin/env bash
# sa-0617 / sa-0642 — WORLD_TARGET_MODEL step catalog vs app.js srStrategicStepCount
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
import re
from pathlib import Path

import system_roadmap as sr

ROOT = Path.cwd()
app_js = (ROOT / "agent-control-panel/assets/app.js").read_text(encoding="utf-8")

assert "function srStrategicStepCount" in app_js, "srStrategicStepCount missing from app.js"
assert "strategic_build_phases" in app_js, "app.js must read strategic_build_phases"
for forbidden in ("build order — 12 steps", "Next build order — 12 steps"):
    assert forbidden not in app_js, f"hardcoded step count still in app.js: {forbidden}"

payload = sr.system_roadmap_payload()
ssot_count = sr._strategic_build_step_count()
phases = payload.get("strategic_build_phases") or []
payload_count = sum(len(p.get("steps") or []) for p in phases)
ui_count = int((payload.get("ui_contract") or {}).get("strategic_build_step_count") or 0)

assert ssot_count == payload_count == ui_count, (ssot_count, payload_count, ui_count)
assert ssot_count >= 1, "strategic build step catalog empty"

# Mirror app.js reduce logic
app_mirror = sum(len(p.get("steps") or []) for p in phases)
assert app_mirror == ssot_count

catalog_ids = set(sr.STEP_CATALOG.keys())
phase_ids = {s.get("roadmap_id") for p in phases for s in (p.get("steps") or []) if s.get("roadmap_id")}
assert phase_ids.issubset(catalog_ids | {"STRATEGIC-SLICE", "P0-RUNRECEIPT"}), phase_ids - catalog_ids

print(f"OK: validate-wtm-step-catalog-appjs-v1 · steps={ssot_count} phases={len(phases)} ui_contract={ui_count}")
PY
