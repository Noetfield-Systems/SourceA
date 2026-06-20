#!/usr/bin/env bash
# validate-enforcement-demo-v1.sh — enforcement kernel + tamper detection (W2)
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

LATEST="${HOME}/.sina/receipts/enforcement/latest-demo-receipt.json"
TAMPER_TEST=0
[[ "${1:-}" == "--tamper-test" ]] && TAMPER_TEST=1

fail() { echo "FAIL: validate-enforcement-demo-v1 — $*" >&2; exit 1; }

[[ -f scripts/commit_intent_v1.py ]] || fail "commit_intent_v1.py missing"
[[ -f demo/enforcement/intent-allow.json ]] || fail "demo intent-allow missing"
[[ -f demo/enforcement/intent-deny.json ]] || fail "demo intent-deny missing"

# Deny path must block
if python3 scripts/commit_intent_v1.py --intent demo/enforcement/intent-deny.json --json >/tmp/enf-deny.json 2>/dev/null; then
  fail "intent-deny must exit non-zero / blocked"
fi
grep -q '"blocked": true' /tmp/enf-deny.json || fail "intent-deny did not return blocked"

# Allow path must commit
python3 scripts/commit_intent_v1.py --intent demo/enforcement/intent-allow.json --json >/tmp/enf-allow.json \
  || fail "intent-allow commit failed"
grep -q '"outcome": "COMMITTED"' /tmp/enf-allow.json || fail "intent-allow not COMMITTED"

[[ -f "$LATEST" ]] || fail "latest-demo-receipt.json missing after commit"

python3 - <<'PY' || fail "receipt integrity check"
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from commit_intent_v1 import verify_receipt_checksum
from governance_event_spine_v1 import find_by_event_id

latest = Path.home() / ".sina/receipts/enforcement/latest-demo-receipt.json"
rec = json.loads(latest.read_text(encoding="utf-8"))
if rec.get("outcome") != "COMMITTED":
    raise SystemExit("latest receipt outcome not COMMITTED")
if not verify_receipt_checksum(rec):
    raise SystemExit("receipt checksum invalid")
spine_id = rec.get("spine_event_id")
if not spine_id:
    raise SystemExit("COMMITTED receipt missing spine_event_id")
row = find_by_event_id(str(spine_id))
if not row:
    raise SystemExit(f"spine row missing: {spine_id}")
rule = rec.get("rule_id") or ""
law = Path("brain-os/laws/SOURCEA_INVARIANT_GATEKEEPER_BLUEPRINT_LOCKED_v1.md")
if not law.is_file():
    raise SystemExit("rule_id law file missing")
print("OK: receipt checksum + spine bind valid")
PY

if [[ "$TAMPER_TEST" -eq 1 ]]; then
  cp "$LATEST" "${LATEST}.bak"
  python3 - <<'PY' || fail "tamper inject failed"
import json
from pathlib import Path
p = Path.home() / ".sina/receipts/enforcement/latest-demo-receipt.json"
rec = json.loads(p.read_text(encoding="utf-8"))
rec["gate_status"] = "PASS_TAMPERED"
p.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
PY
  if python3 - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from commit_intent_v1 import verify_receipt_checksum
rec = json.loads((Path.home() / ".sina/receipts/enforcement/latest-demo-receipt.json").read_text())
sys.exit(0 if verify_receipt_checksum(rec) else 1)
PY
  then
    mv "${LATEST}.bak" "$LATEST"
    fail "tamper test: checksum should FAIL after hand-edit"
  fi
  mv "${LATEST}.bak" "$LATEST"
  echo "OK: tamper correctly detected"
fi

echo "OK: validate-enforcement-demo-v1 · commit gate · receipt · spine · deny block"
