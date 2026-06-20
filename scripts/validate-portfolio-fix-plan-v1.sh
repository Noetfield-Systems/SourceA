#!/usr/bin/env bash
# validate-portfolio-fix-plan-v1 — SSOT + pulse receipt + surfaces line
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-portfolio-fix-plan-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/data/portfolio-fix-plan-v1.json" ]] || fail "missing SSOT"
[[ -f "$ROOT/docs/SOURCEA_PORTFOLIO_FIX_PLAN_LOCKED_v1.md" ]] || fail "missing LOCKED doc"
[[ -f "$ROOT/scripts/portfolio_fix_plan_pulse_v1.py" ]] || fail "missing pulse script"
[[ -f "$ROOT/scripts/portfolio_fix_execute_v1.sh" ]] || fail "missing execute script"

python3 <<'PY' || fail "SSOT schema"
import json
from pathlib import Path
row = json.loads(Path("data/portfolio-fix-plan-v1.json").read_text())
assert row.get("schema") == "portfolio-fix-plan-v1"
assert len(row.get("tasks") or []) >= 8
assert row.get("roles", {}).get("trustfield_agent")
assert row.get("roles", {}).get("sourcea_worker")
print("OK: portfolio-fix-plan SSOT schema")
PY

python3 scripts/portfolio_fix_plan_pulse_v1.py --wire --json >/dev/null || true

REC="$HOME/.sina/portfolio-fix-plan-pulse-v1.json"
[[ -f "$REC" ]] || fail "missing pulse receipt — run portfolio_fix_plan_pulse_v1.py --wire"

python3 <<'PY' || fail "receipt schema"
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/portfolio-fix-plan-pulse-v1.json").read_text())
assert r.get("schema") == "portfolio-fix-plan-pulse-v1"
assert r.get("portfolio_fix_line")
print("OK: pulse receipt", r.get("portfolio_fix_line")[:80])
PY

SURF="$HOME/.sina/agent-live-surfaces-v1.json"
python3 <<'PY' || fail "surfaces line"
import json
from pathlib import Path
s = json.loads(Path.home().joinpath(".sina/agent-live-surfaces-v1.json").read_text())
assert s.get("portfolio_fix_line"), "portfolio_fix_line missing on surfaces"
print("OK: surfaces portfolio_fix_line wired")
PY

echo "PASS: validate-portfolio-fix-plan-v1"
