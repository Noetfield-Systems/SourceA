#!/usr/bin/env bash
# UI upgrade mandatory gate validator
# Law: brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== validate-ui-upgrade-mandatory-v1 ==="

fail=0

if [[ ! -f brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md ]]; then
  echo "FAIL: law doc missing"
  fail=1
fi

if [[ ! -f data/ui-upgrade-surface-registry-v1.json ]]; then
  echo "FAIL: surface registry missing"
  fail=1
fi

if [[ ! -f .cursor/rules/024-ui-upgrade-mandatory-checklist.mdc ]]; then
  echo "FAIL: cursor rule 024 missing"
  fail=1
fi

if ! python3 scripts/ui_upgrade_ledger_v1.py --validate --json >/dev/null 2>&1; then
  echo "FAIL: ui_upgrade_ledger_v1 --validate"
  fail=1
else
  n="$(python3 -c "import json;print(len(json.load(open('data/ui-upgrade-ledgers-index-v1.json'))['ledgers']))")"
  echo "OK  all per-app ledgers ($n/$n)"
fi

if ! python3 scripts/ui_upgrade_mandatory_gate_v1.py --surface wtm_tab --assess --json >/dev/null 2>&1; then
  echo "FAIL: gate assess wtm_tab"
  fail=1
else
  echo "OK  gate assess wtm_tab + ledger"
fi

if ! python3 scripts/ui_upgrade_mandatory_gate_v1.py --surface sourcea_landing --assess --json >/dev/null 2>&1; then
  echo "FAIL: gate assess sourcea_landing"
  fail=1
else
  echo "OK  gate assess sourcea_landing"
fi

if ! python3 scripts/ui_upgrade_mandatory_gate_v1.py --surface witnessbc_commercial --assess --json >/dev/null 2>&1; then
  echo "FAIL: gate assess witnessbc_commercial"
  fail=1
else
  echo "OK  gate assess witnessbc_commercial + ledger"
fi

if ! python3 scripts/ui_upgrade_mandatory_gate_v1.py --surface hub_form --assess --json >/dev/null 2>&1; then
  echo "FAIL: gate assess hub_form"
  fail=1
else
  echo "OK  gate assess hub_form + ledger"
fi

if [[ ! -f .cursor/rules/025-ui-upgrade-first-check-live-wire.mdc ]]; then
  echo "FAIL: cursor rule 025 missing"
  fail=1
else
  echo "OK  first-check live wire rule"
fi

if [[ ! -f scripts/ui_upgrade_first_check_v1.py ]]; then
  echo "FAIL: ui_upgrade_first_check_v1.py missing"
  fail=1
else
  echo "OK  first-check script"
fi
if [[ ! -f data/ui-upgrade-ledgers-index-v1.json ]]; then
  echo "FAIL: ledger index missing"
  fail=1
else
  echo "OK  ledger index"
fi

if ! bash scripts/validate-doc-datetime-header-v1.sh brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md >/dev/null 2>&1; then
  echo "FAIL: law doc datetime header"
  fail=1
else
  echo "OK  law doc datetime header"
fi

if [[ "$fail" -ne 0 ]]; then
  echo "FAIL: validate-ui-upgrade-mandatory-v1"
  exit 1
fi

echo "PASS: validate-ui-upgrade-mandatory-v1"
