#!/usr/bin/env bash
# validate-full-stack-100-fix-plan-v1.sh — plan SSOT + pulse receipt
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PLAN="$ROOT/data/sourcea-full-stack-100-fix-plan-v1.json"
PULSE="${HOME}/.sina/full-stack-fix-plan-pulse-v1.json"

fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -f "$PLAN" ]] || fail "missing plan $PLAN"

python3 - <<'PY' "$PLAN" || fail "plan schema"
import json, sys
p = json.load(open(sys.argv[1]))
assert p.get("schema") in ("sourcea-full-stack-100-fix-plan-v1", "sourcea-full-stack-100-fix-plan-v2")
fixes = p.get("fixes") or []
assert len(fixes) == 100, len(fixes)
ids = [f["id"] for f in fixes]
assert ids[0] == "F001" and ids[-1] == "F100", (ids[0], ids[-1])
waves = p.get("waves") or []
assert len(waves) >= 9
all_wave_ids = []
for w in waves:
    all_wave_ids.extend(w.get("plan_ids") or [])
assert len(all_wave_ids) == 100
assert "F001" in all_wave_ids
for f in fixes:
    assert f.get("tier") in ("P0", "P1", "P2")
    assert f.get("wave")
    assert f.get("owner_role") in ("worker", "founder", "brain", "system")
print("OK: plan fixes=100 waves=", len(waves), "schema=", p.get("schema"))
PY

python3 scripts/full_stack_fix_plan_pulse_v1.py --json >/dev/null || fail "pulse run"

[[ -f "$PULSE" ]] || fail "missing pulse $PULSE"

python3 - <<'PY' "$PULSE" || fail "pulse schema"
import json, sys
r = json.load(open(sys.argv[1]))
assert r.get("schema") == "full-stack-fix-plan-pulse-v1"
assert r.get("ok") is True
assert str(r.get("critical_path_head") or "").startswith("F")
assert (r.get("progress") or {}).get("total") == 100
print("OK: pulse", r.get("full_stack_fix_line", "")[:80])
PY

echo "PASS: validate-full-stack-100-fix-plan-v1"
