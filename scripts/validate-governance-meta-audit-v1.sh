#!/usr/bin/env bash
# validate-governance-meta-audit-v1.sh — meta-audit script + receipt shape
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-governance-meta-audit-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/SOURCEA_GOV_META_AUDIT_LOCKED_v1.md" ]] || fail "missing law"
[[ -f "$ROOT/scripts/governance_meta_audit_v1.py" ]] || fail "missing governance_meta_audit_v1.py"

python3 "$ROOT/scripts/governance_meta_audit_v1.py" --tier fast --json >/dev/null \
  || fail "governance_meta_audit_v1 fast run"

R="$HOME/.sina/governance-meta-audit-receipt-v1.json"
[[ -f "$R" ]] || fail "missing governance-meta-audit-receipt-v1.json"

python3 - <<'PY' "$R"
import json
import sys

r = json.load(open(sys.argv[1]))
assert r.get("schema") == "governance-meta-audit-receipt-v1", r.get("schema")
assert "checks" in r and isinstance(r["checks"], list), "checks missing"
assert "governance_may_claim_fixed" in r, "governance_may_claim_fixed missing"
if not r.get("ok"):
    fails = r.get("failures") or []
    print(f"WARN: meta-audit ok=false failures={len(fails)} (validator shape OK)")
    for f in fails[:5]:
        print(f"  - {f.get('id')}: {f.get('detail','')[:120]}")
    raise SystemExit(0)
print("OK: governance-meta-audit receipt ok=true")
PY

echo "OK: validate-governance-meta-audit-v1"
