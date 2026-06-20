#!/usr/bin/env bash
# validate-phase0-freemium-sandbox-v1.sh — internal Phase 0 reference policy gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-phase0-freemium-sandbox-v1 — $*" >&2; exit 1; }

test -f data/phase0-freemium-sandbox-reference-v1.json || fail "SSOT missing"
test -f scripts/phase0_freemium_sandbox_pulse_v1.py || fail "pulse script missing"

python3 - <<'PY' || fail "SSOT schema"
import json
from pathlib import Path
p = Path("data/phase0-freemium-sandbox-reference-v1.json")
d = json.loads(p.read_text())
assert d.get("schema") == "phase0-freemium-sandbox-reference-v1"
assert d.get("internal_policy") is True
assert len(d.get("inventory") or []) >= 10
assert d.get("aligned_policies", {}).get("tool_pick_two_phase")
print("OK: phase0 SSOT schema")
PY

python3 scripts/phase0_freemium_sandbox_pulse_v1.py --json >/dev/null || fail "pulse failed"

bash scripts/validate-noetfield-freemium-bay-v1.sh || fail "noetfield freemium bay gate"

echo "OK: validate-phase0-freemium-sandbox-v1 · internal Phase 0 reference policy wired"
