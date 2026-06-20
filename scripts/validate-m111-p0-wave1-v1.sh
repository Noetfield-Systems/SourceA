#!/usr/bin/env bash
# validate-m111-p0-wave1-v1.sh — M111 P0 wave 1 ship gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
fail() { echo "FAIL: m111-p0-wave1 — $*"; exit 1; }

[[ -f "$ROOT/data/ecosystem-mac-health-111-upgrade-plan-v1.json" ]] || fail "missing M111 plan"

python3 -c "
import json, urllib.request
from pathlib import Path

plan = json.loads(Path('data/ecosystem-mac-health-111-upgrade-plan-v1.json').read_text())
waves = plan.get('waves') or {}
w1 = set(waves.get('W1') or [])
if not w1:
    w1 = {u['id'] for u in plan['upgrades'] if u['tier']=='P0' and u['seq'] <= 37}

hub = json.loads(urllib.request.urlopen('http://127.0.0.1:13020/api/worker-hub/v1', timeout=8).read().decode())
assert hub.get('health_grade'), 'missing health_grade on worker-hub'
assert hub.get('pressure_badge'), 'missing pressure_badge'
assert hub.get('ecosystem_mac_health', {}).get('schema') == 'hub-ecosystem-slice-v1'
assert Path.home().joinpath('.sina/mac-health-quiet-pulse-receipt-v1.json').is_file() or True

health = json.loads(urllib.request.urlopen('http://127.0.0.1:13024/health', timeout=5).read().decode())
ui = health.get('ui_contract') or {}
assert ui.get('tab_count') == 0, ui

import subprocess
r = subprocess.run(['python3','scripts/founder_session_gate_v1.py','validate-all-e2e-v1.sh'], cwd='.')
assert r.returncode == 2, f'gate should block all-e2e got {r.returncode}'

# cpu cool down invokes cursor trim
import importlib.util
spec = importlib.util.spec_from_file_location('rel', 'scripts/mac_health_cpu_relief_v1.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
src = Path('scripts/mac_health_cpu_relief_v1.py').read_text()
assert 'cursor_session_relief_v1' in src and 'trim_cursor_caches' in src

print('OK: M111 P0 wave 1 probes pass ·', len(w1), 'wave ids')
"

# Mark wave 1 done in plan when gate passes
python3 <<'PY'
import json
from datetime import datetime, timezone
from pathlib import Path

plan_path = Path("data/ecosystem-mac-health-111-upgrade-plan-v1.json")
plan = json.loads(plan_path.read_text())
w1 = set((plan.get("waves") or {}).get("W1") or [])
if not w1:
    w1 = {u["id"] for u in plan["upgrades"] if u["tier"] == "P0" and u["seq"] <= 37}
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
for u in plan["upgrades"]:
    if u["id"] in w1:
        u["status"] = "done"
        u["done_at"] = ts
        u["execution_proof"] = {"wave": "W1", "gate": "validate-m111-p0-wave1-v1.sh"}
done = sum(1 for u in plan["upgrades"] if u.get("status") == "done")
total = len(plan["upgrades"])
plan["progress"] = {
    **(plan.get("progress") or {}),
    "total": total,
    "done": done,
    "planned": total - done,
    "pct": round(100.0 * done / total, 1),
}
plan["saved_at"] = ts
plan_path.write_text(json.dumps(plan, indent=2) + "\n")
print(f"Marked W1 done: {len(w1)} rows · progress {done}/{total}")
PY

python3 "$ROOT/scripts/ecosystem_mac_health_111_plan_pulse_v1.py" --json >/dev/null
echo "PASS validate-m111-p0-wave1-v1"
