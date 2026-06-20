#!/usr/bin/env bash
# validate-platform-neutral-world-model-v1.sh — platform-neutral policy + WTM plan loop
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/platform-neutral-world-model-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/world_model_plan_check_v1.py || { echo "FAIL missing script"; exit 1; }
test -f .cursor/rules/platform-neutral-world-model.mdc || { echo "FAIL missing cursor rule"; exit 1; }

grep -q 'platform_neutral_world_model' scripts/plans_unified_upgrade_v1.py || { echo "FAIL plans_unified not wired"; exit 1; }
grep -q 'world_model_plan_check' scripts/plans_unified_upgrade_v1.py || { echo "FAIL WTM loop not wired"; exit 1; }
grep -q '/api/world-model-plan-check/tick/v1' scripts/sina-command-server.py || { echo "FAIL hub API missing"; exit 1; }
grep -q 'world_model_plan_check_v1' scripts/sina-command-server.py || { echo "FAIL loop chain missing WTM"; exit 1; }
grep -q 'world_model_plan_check_v1' data/commercial/stack-map-routing-v1.json || { echo "FAIL stack-map missing WTM"; exit 1; }

python3 - <<'PY' || { echo "FAIL SSOT schema"; exit 1; }
import json
from pathlib import Path
j = json.loads(Path("data/platform-neutral-world-model-v1.json").read_text())
assert j.get("schema") == "platform-neutral-world-model-v1"
assert j.get("platform_neutral_policy", {}).get("surfaces")
assert "mac only" in j["platform_neutral_policy"]["forbidden_public_framing"]
billing = j["platform_neutral_policy"].get("stripe_billing") or {}
assert billing.get("statement_descriptor") == "NOETFIELD SYSTEMS"
assert billing.get("statement_descriptor_short") == "NFS"
assert any(r["lane"] == "noetfield" for r in j.get("product_routes", []))
print("OK: SSOT platform-neutral-world-model-v1")
PY

python3 scripts/world_model_plan_check_v1.py --json >/dev/null
test -f "${SINA}/world-model-plan-check-receipt-v1.json" || { echo "FAIL missing receipt"; exit 1; }

echo "PASS: validate-platform-neutral-world-model-v1"
