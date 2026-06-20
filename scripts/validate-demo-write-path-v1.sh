#!/usr/bin/env bash
# validate-demo-write-path-v1.sh — W2 demo write path (commit → receipt → spine → tamper FAIL)
# TRACE: ENF-04 · enf-0002 · ENFORCEMENT_6MO W2
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

fail() { echo "FAIL: validate-demo-write-path-v1 — $*" >&2; exit 1; }

[[ -f scripts/commit_intent_v1.py ]] || fail "commit_intent_v1.py missing"
[[ -f scripts/governance_event_spine_v1.py ]] || fail "governance_event_spine_v1.py missing"
[[ -f scripts/governance_demo_gate_v1.py ]] || fail "governance_demo_gate_v1.py missing"
[[ -f brain-os/demo/governance_demo_policy_v1.json ]] || fail "demo policy missing"

RECEIPT_DIR="${HOME}/.sina/demo-enforcement/receipts"
[[ -d "$RECEIPT_DIR" ]] || fail "demo receipt dir missing — run allow path first"

bash scripts/validate-demo-enforcement-v1.sh --tamper-test || fail "demo enforcement chain"

python3 - <<'PY' || fail "write-path contract"
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from commit_intent_v1 import verify_receipt_checksum
from governance_event_spine_v1 import find_by_event_id

latest = Path.home() / ".sina/demo-enforcement/receipts/latest-demo-receipt.json"
rec = json.loads(latest.read_text(encoding="utf-8"))
required = ("outcome", "rule_id", "spine_event_id", "receipt_checksum", "gate_status", "receipt_id")
for k in required:
    if k not in rec:
        raise SystemExit(f"receipt missing field: {k}")
if rec.get("outcome") != "COMMITTED":
    raise SystemExit("latest receipt not COMMITTED")
if not verify_receipt_checksum(rec):
    raise SystemExit("checksum invalid on latest receipt")
if not find_by_event_id(str(rec.get("spine_event_id"))):
    raise SystemExit("spine row missing for latest receipt")

# Write path = single commit gate module
ci = Path("scripts/commit_intent_v1.py").read_text(encoding="utf-8")
if "--demo-enforcement" not in ci:
    raise SystemExit("commit_intent missing --demo-enforcement entry")
print("OK: W2 write-path · commit_intent → receipt → spine bound")
PY

echo "OK: validate-demo-write-path-v1 · W2 kernel · tamper FAIL · ENF-04"
