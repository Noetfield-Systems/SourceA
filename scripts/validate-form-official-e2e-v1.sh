#!/usr/bin/env bash
# validate-form-official-e2e-v1.sh — FORM_OFFICIAL nerve map + wire receipt + path hygiene
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
fail() { echo "FAIL: validate-form-official-e2e-v1 — $*" >&2; exit 1; }

NERVE_MAP="$ROOT/data/form_official_nerve_map_v1.json"
WIRE_RECEIPT="$HOME/.sina/form-official-wire-receipt-v1.json"

[[ -f "$NERVE_MAP" ]] || fail "missing nerve map data/form_official_nerve_map_v1.json"
[[ -f "$ROOT/scripts/form_official_wire_e2e_v1.py" ]] || fail "missing form_official_wire_e2e_v1.py"

python3 - <<PY || fail "nerve map schema"
import json
from pathlib import Path
root = Path("$ROOT")
nerve = json.loads((root / "data/form_official_nerve_map_v1.json").read_text())
assert nerve.get("schema") == "form-official-nerve-map-v1"
assert nerve.get("canvas", {}).get("m1_canvas")
assert nerve.get("scripts", {}).get("wire_e2e")
assert nerve.get("editions", {}).get("third")
assert len(nerve.get("pipeline") or []) >= 5
print("OK: nerve map schema · editions · pipeline")
PY

bash "$ROOT/scripts/validate-integrity-form-canvas-ssot-v1.sh"
bash "$ROOT/scripts/validate-hub-form-automatic-v1.sh"
bash "$ROOT/scripts/validate-form-founder-supremacy-v1.sh"
bash "$ROOT/scripts/validate-no-agent-invitation-v1.sh"
bash "$ROOT/scripts/validate-ui-upgrade-first-check-live-wire-v1.sh"
bash "$ROOT/scripts/validate-ui-first-check-mandatory-all-agents-v1.sh"

python3 "$ROOT/scripts/form_open_questions_reconcile_v1.py" --json >/dev/null || fail "reconcile mismatch"

[[ -f "$WIRE_RECEIPT" ]] || python3 "$ROOT/scripts/form_official_wire_e2e_v1.py" --no-regen --no-validate --json >/dev/null

python3 - <<PY || fail "wire receipt"
import json
from pathlib import Path
p = Path.home() / ".sina/form-official-wire-receipt-v1.json"
row = json.loads(p.read_text())
assert row.get("schema") == "form-official-wire-receipt-v1"
assert row.get("form_official_line")
assert row.get("open_questions_count") is not None
assert row.get("canvas_open_count") == row.get("open_questions_count")
print(f"OK: wire receipt · {row.get('form_official_line')[:72]}")
PY

echo "OK: validate-form-official-e2e-v1 · nerve map · canvas SSOT · reconcile · wire receipt"
