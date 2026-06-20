#!/usr/bin/env bash
# validate-ui-zero-drift-v1 — ZERO TOLERANCE: no UI drift · no upgrade drift
# Founder law: NO UI DRIFT NO UPGRADE DRIFT WILL BE TOLERATED
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-ui-zero-drift-v1 — $*" >&2; exit 1; }

[[ -f "$HOME/.sina/founder-zero-ui-drift-v1.flag" ]] \
  || fail "founder-zero-ui-drift-v1.flag missing — zero-tolerance not armed"

# Live wire (mandatory ledgers + wire receipt + pre_write) — do NOT nest validate-ui-first-check-mandatory (recursion)
bash scripts/validate-ui-upgrade-first-check-live-wire-v1.sh \
  || fail "UI FIRST CHECK live wire"
bash scripts/validate-ui-upgrade-no-downgrade-v1.sh \
  || fail "UI upgrade no-downgrade"
bash scripts/validate-ui-wiring-v1.sh \
  || fail "UI wiring"
bash scripts/validate-copy-safety-hub-v1.sh \
  || fail "hub copy safety"

for rule in 024-ui-upgrade-mandatory-checklist.mdc 025-ui-upgrade-first-check-live-wire.mdc 026-ui-first-check-zero-exception.mdc; do
  [[ -f ".cursor/rules/$rule" ]] || fail "missing rule $rule"
done
grep -q 'ui_upgrade_first_check' scripts/agent_session_gate_run_v1.py || fail "session gate missing ui_fc"
grep -q 'founder_zero_ui_drift' data/agent-behavior-settings-v1.json || fail "behavior SSOT missing founder_zero_ui_drift"

python3 scripts/ui_upgrade_ledger_v1.py --validate --json > /tmp/ui-ledger-val.json \
  || fail "ledger validate"
python3 - <<'PY' || fail "ledger issues"
import json
from pathlib import Path
row = json.loads(Path("/tmp/ui-ledger-val.json").read_text())
assert row.get("ok") is True, row.get("issues")
print(f"OK: ledgers {row.get('ledger_count')} · issues=0")
PY

python3 scripts/ui_upgrade_baseline_guard_v1.py verify-all \
  || fail "UI baseline verify-all"

bash scripts/validate-witnessbc-ui-zero-drift-v1.sh \
  || fail "WitnessBC surface drift"

python3 - <<'PY' || fail "hub must_do stale copy"
import json
from pathlib import Path
p = Path("agent-control-panel/command-data.json")
if not p.is_file():
    print("WARN: command-data missing — skip must_do scan")
    raise SystemExit(0)
d = json.loads(p.read_text())
md = " ".join(((d.get("command_center") or {}).get("founder") or {}).get("must_do_today") or [])
forbidden = (
    "automatic recommended picks",
    "Open form · Submit only",
    "submit only",
)
for bad in forbidden:
    assert bad.lower() not in md.lower(), f"stale hub copy: {bad!r}"
print("OK: hub must_do_today — no stale form copy")
PY

echo "PASS: validate-ui-zero-drift-v1 · ZERO TOLERANCE · no UI drift · no upgrade drift"
