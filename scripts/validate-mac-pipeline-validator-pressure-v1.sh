#!/usr/bin/env bash
# validate-mac-pipeline-validator-pressure-v1.sh — Mac Law pipeline/validator tier gate v1.1
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAW="$HOME/Desktop/MacLaw/MAC_PIPELINE_VALIDATOR_PRESSURE_LAW_LOCKED_v1.md"
REG="$ROOT/data/mac-pipeline-validator-pressure-registry-v1.json"
fail() { echo "FAIL: validate-mac-pipeline-validator-pressure-v1 — $*" >&2; exit 1; }

[[ -f "$LAW" ]] || fail "missing law doc: $LAW"
[[ -f "$REG" ]] || fail "missing registry: $REG"
[[ -f "$ROOT/scripts/mac_pipeline_validator_pressure_v1.py" ]] || fail "missing enforce module"
[[ -f "$ROOT/scripts/founder_session_gate_v1.py" ]] || fail "missing founder_session_gate_v1.py"
[[ -f "$ROOT/scripts/_founder_session_gate_entry_v1.sh" ]] || fail "missing gate entry shim"

python3 -c "
import json
from pathlib import Path
reg = json.loads(Path('$REG').read_text())
assert reg.get('version','').startswith('1.1'), reg.get('version')
heavy = reg['tiers']['heavy']
assert len(heavy.get('globs') or []) >= 5
assert 'validate-*-e2e*.sh' in heavy['globs']
assert len(heavy.get('scripts') or []) >= 20
" || fail "registry v1.1 invalid"

grep -q 'mac_pipeline_validator_pressure_v1' "$ROOT/scripts/founder_session_gate_v1.py" \
  || fail "founder_session_gate must load pressure registry module"

# Auto-wire any heavy script still missing gate source
python3 "$ROOT/scripts/mac_pipeline_validator_pressure_v1.py" --wire-gates --json >/dev/null \
  || fail "wire-gates failed"

python3 "$ROOT/scripts/mac_pipeline_validator_pressure_v1.py" --strict-audit --json >/dev/null \
  || fail "strict gate audit failed — heavy script missing _founder_session_gate_or_exit"

# Pattern block: e2e must classify heavy
tier="$(python3 "$ROOT/scripts/mac_pipeline_validator_pressure_v1.py" --classify validate-mac-health-e2e-v1.sh)"
[[ "$tier" == "heavy" ]] || fail "e2e must classify as heavy got=$tier"

# Block during founder session
if [[ -f "$HOME/.sina/mac-control-plane-v1.flag" ]] || [[ -f "$HOME/.sina/mac-light-validators-only-v1.flag" ]]; then
  if python3 "$ROOT/scripts/founder_session_gate_v1.py" validate-all-e2e-v1.sh >/dev/null 2>&1; then
    fail "founder_session_gate must block validate-all-e2e-v1.sh"
  fi
  if python3 "$ROOT/scripts/founder_session_gate_v1.py" validate-mac-health-e2e-v1.sh >/dev/null 2>&1; then
    fail "founder_session_gate must block validate-mac-health-e2e-v1.sh"
  fi
fi

# Ship window allows heavy when flag present
if [[ -f "$HOME/.sina/asf-ship-window-v1.flag" ]]; then
  python3 "$ROOT/scripts/founder_session_gate_v1.py" validate-all-e2e-v1.sh --json | grep -q '"ok": true' \
    || fail "ship window must allow heavy gate"
fi

python3 "$ROOT/scripts/mac_pipeline_validator_pressure_v1.py" --json >/dev/null \
  || fail "pressure probe/enforce failed"

echo "PASS: validate-mac-pipeline-validator-pressure-v1.sh (v1.1)"
