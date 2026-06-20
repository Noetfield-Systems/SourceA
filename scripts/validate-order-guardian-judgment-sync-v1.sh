#!/usr/bin/env bash
# validate-order-guardian-judgment-sync-v1.sh — sa-0798 judgment/status contract + drift warn
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-order-guardian-judgment-sync-v1 — $*" >&2; exit 1; }

python3 scripts/order_guardian_pendings_crosswalk_v1.py --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('schema')=='order-guardian-pendings-crosswalk-v1', r
assert r.get('judgment_mismatch_count',1)==0, r.get('judgment_mismatches')
drift=r.get('drift_warnings') or []
if drift:
    print('WARN: pendings↔orders cross-SSOT drift (informational):')
    for w in drift:
        print(' ', w)
print(f\"OK: validate-order-guardian-judgment-sync-v1 · orders={r.get('orders_total')} mismatches=0 drift_warn={len(drift)}\")
"
