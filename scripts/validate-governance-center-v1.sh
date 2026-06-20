#!/usr/bin/env bash
# validate-governance-center-v1.sh — Governance Center receipt + rooms wired
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -f "$ROOT/SOURCEA_GOVERNANCE_CENTER_SELF_GOVERN_LOCKED_v1.md" ]] || fail "missing law"
[[ -f "$ROOT/SOURCEA_GOV_META_AUDIT_LOCKED_v1.md" ]] || fail "missing gov meta-audit law"
[[ -f "$ROOT/scripts/governance_center_run_v1.py" ]] || fail "missing orchestrator"
[[ -f "$ROOT/scripts/governance_meta_audit_v1.py" ]] || fail "missing governance_meta_audit_v1.py"

python3 "$ROOT/scripts/governance_meta_audit_v1.py" --tier fast --json >/dev/null \
  || echo "WARN: governance meta-audit ok=false — center receipt must be ok=false" >&2

python3 "$ROOT/scripts/governance_center_run_v1.py" --tier fast --skip-judge --skip-thread --json >/dev/null \
  || fail "governance_center_run fast"

R="$HOME/.sina/governance-center-receipt-v1.json"
[[ -f "$R" ]] || fail "missing governance-center receipt"
python3 - <<'PY' "$R"
import json, sys
r = json.load(open(sys.argv[1]))
assert r.get("schema") == "governance-center-receipt-v1"
assert r.get("ok") is True, r.get("steps")
print("OK: governance-center receipt ok=true")
PY

bash "$ROOT/scripts/validate-judge-center-v1.sh" 2>/dev/null || fail "judge center"
bash "$ROOT/scripts/validate-thread-room-v1.sh" 2>/dev/null || fail "thread room"

echo "OK: validate-governance-center-v1"
