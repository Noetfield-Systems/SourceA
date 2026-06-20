#!/usr/bin/env bash
# validate-demo-enforcement-v1.sh — Copilot P-001 demo (BLOCK / ALLOW / tamper)
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

LATEST="${HOME}/.sina/demo-enforcement/receipts/latest-demo-receipt.json"
TAMPER_TEST=0
[[ "${1:-}" == "--tamper-test" ]] && TAMPER_TEST=1

fail() { echo "FAIL: validate-demo-enforcement-v1 — $*" >&2; exit 1; }

[[ -f brain-os/demo/governance_demo_policy_v1.json ]] || fail "policy missing"
[[ -f scripts/governance_demo_gate_v1.py ]] || fail "demo gate missing"
[[ -f scripts/commit_intent_v1.py ]] || fail "commit_intent_v1.py missing"

if python3 scripts/commit_intent_v1.py --demo-enforcement --case block --json >/tmp/copilot-block.json 2>/dev/null; then
  fail "block case must exit non-zero"
fi
grep -q '"blocked": true' /tmp/copilot-block.json || fail "block case did not return blocked"

python3 scripts/commit_intent_v1.py --demo-enforcement --case allow --json >/tmp/copilot-allow.json \
  || fail "allow case failed"
grep -q '"outcome": "COMMITTED"' /tmp/copilot-allow.json || fail "allow not COMMITTED"
grep -q '"status": "DONE"' /tmp/copilot-allow.json || fail "allow missing DONE status"

[[ -f "$LATEST" ]] || fail "latest copilot receipt missing"

python3 - <<'PY' || fail "receipt integrity"
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from commit_intent_v1 import verify_receipt_checksum
from governance_event_spine_v1 import find_by_event_id

latest = Path.home() / ".sina/demo-enforcement/receipts/latest-demo-receipt.json"
rec = json.loads(latest.read_text(encoding="utf-8"))
if rec.get("outcome") != "COMMITTED":
    raise SystemExit("outcome not COMMITTED")
if rec.get("rule_id") != "P-001":
    raise SystemExit("rule_id not P-001")
if not verify_receipt_checksum(rec):
    raise SystemExit("checksum invalid")
spine_id = rec.get("spine_event_id")
if not spine_id:
    raise SystemExit("missing spine_event_id")
if not find_by_event_id(str(spine_id)):
    raise SystemExit(f"spine row missing: {spine_id}")
print("OK: copilot receipt + spine + P-001")
PY

if [[ "$TAMPER_TEST" -eq 1 ]]; then
  cp "$LATEST" "${LATEST}.bak"
  python3 - <<'PY' || fail "tamper inject"
import json
from pathlib import Path
p = Path.home() / ".sina/demo-enforcement/receipts/latest-demo-receipt.json"
rec = json.loads(p.read_text(encoding="utf-8"))
rec["gate_status"] = "PASS_TAMPERED"
p.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
PY
  if python3 - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from commit_intent_v1 import verify_receipt_checksum
rec = json.loads((Path.home() / ".sina/demo-enforcement/receipts/latest-demo-receipt.json").read_text())
sys.exit(0 if verify_receipt_checksum(rec) else 1)
PY
  then
    mv "${LATEST}.bak" "$LATEST"
    fail "tamper should FAIL checksum"
  fi
  mv "${LATEST}.bak" "$LATEST"
  echo "OK: tamper detected"
fi

echo "OK: validate-demo-enforcement-v1 · Copilot BLOCK/ALLOW · receipt · spine"
