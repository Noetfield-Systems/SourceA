#!/usr/bin/env bash
# validate-ui-upgrade-no-downgrade-v1.sh — controlled landing UI must match baseline SSOT
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== validate-ui-upgrade-no-downgrade-v1 ==="
python3 scripts/ui_upgrade_baseline_guard_v1.py verify-all || exit 1

# E2E receipt — zero-tolerance flag requires pass (no WARN)
RECEIPT="${HOME}/.sina/sourcea-landing-run-receipt-v1.json"
ZERO_FLAG="${HOME}/.sina/founder-zero-ui-drift-v1.flag"
if [[ -f "$RECEIPT" ]]; then
  python3 - <<PY
import json, sys
from pathlib import Path
p = Path("${RECEIPT}")
zero = Path("${ZERO_FLAG}").is_file()
row = json.loads(p.read_text())
e2e = row.get("e2e")
if e2e == "pass":
    print("OK: landing run receipt e2e=pass")
elif zero:
    print(f"FAIL: zero UI drift — landing e2e={e2e!r} (pass required)", file=sys.stderr)
    sys.exit(1)
elif e2e == "skipped":
    print("WARN: landing run receipt e2e=skipped — run run-recipe.sh --e2e after UI changes")
else:
    print(f"WARN: landing run receipt e2e={e2e!r}")
PY
else
  if [[ -f "$ZERO_FLAG" ]]; then
    echo "FAIL: zero UI drift — missing landing run receipt" >&2
    exit 1
  fi
  echo "WARN: no landing run receipt — bash SourceA-landing/green-unified/scripts/run-recipe.sh --e2e"
fi

echo "validate-ui-upgrade-no-downgrade-v1.sh: ALL PASS"
