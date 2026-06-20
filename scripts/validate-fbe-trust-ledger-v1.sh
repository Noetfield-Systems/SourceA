#!/usr/bin/env bash
# validate-fbe-trust-ledger-v1.sh — FBE trust ledger event chain
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== Ledger schema ==="
[[ -f data/fbe_trust_ledger_schema_v1.json ]] || { echo "FAIL: missing schema"; fail=1; }
[[ -f scripts/fbe/lib/trust_ledger_v1.py ]] || { echo "FAIL: missing module"; fail=1; }

echo "=== Ledger append + query ==="
python3 - <<'PY' || fail=1
import sys
sys.path.insert(0, "scripts")
from fbe.lib.trust_ledger_v1 import append_event, events_for_job, ledger_payload

jid = "job-validate-ledger-v1"
for et in ("JOB_QUEUED", "POLICY_CHECKED", "KERNEL_STARTED", "JOB_COMPLETED", "LEDGER_SIGNED"):
    r = append_event(
        event_type=et,
        job_id=jid,
        factory_id="exchange-factory-v1",
        policy_pack="fintrac_kyb_v1",
        kernel_hash="abc123",
        payload={"test": True},
        bridge_spine=(et == "LEDGER_SIGNED"),
    )
    assert r.get("ok"), r
events = events_for_job(jid)
assert len(events) >= 5, len(events)
payload = ledger_payload(job_id=jid)
assert payload.get("event_count", 0) >= 5, payload
print("OK: ledger events", len(events))
PY

echo "=== Hub ledger route ==="
grep -q '/api/fbe/ledger/v1' scripts/sina-command-server.py || { echo "FAIL: hub route"; fail=1; }

echo "=== Spine FBE_JOB_SIGNED ==="
grep -q 'FBE_JOB_SIGNED' scripts/governance_event_spine_v1.py || { echo "FAIL: spine event"; fail=1; }

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-trust-ledger-v1"
  exit 0
fi
echo "FAIL: validate-fbe-trust-ledger-v1"
exit 1
