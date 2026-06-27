#!/usr/bin/env bash
# demo-asset-b-policy-v1.sh — Asset B screen-share (block → allow → tamper)
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

POLICY="${1:-outreach}"
if [[ "${1:-}" == "--policy" ]]; then
  POLICY="${2:-outreach}"
fi

case "$POLICY" in
  outreach|ops|creative) ;;
  *)
    echo "usage: $0 [--policy] outreach|ops|creative" >&2
    exit 1
    ;;
esac

pause() { sleep "${1:-2}"; }

echo "=============================================="
echo " ASSET B — POLICY DEMO ($POLICY)"
echo " Block → allow → receipt → tamper fail"
echo "=============================================="
echo ""

echo "[0:30] BEAT 1 — Policy BLOCK"
pause 1
python3 scripts/commit_intent_v1.py --asset-b-policy "$POLICY" --case block --json | python3 -c "
import json,sys
d=json.load(sys.stdin)
r=d.get('receipt') or {}
print('  outcome:', r.get('outcome','BLOCKED'))
print('  reason:', '; '.join(r.get('gate_reasons') or [])[:200])
" || true
pause 2
echo ""

echo "[1:30] BEAT 2 — Policy ALLOW → signed receipt"
pause 1
python3 scripts/commit_intent_v1.py --asset-b-policy "$POLICY" --case allow --json | python3 -c "
import json,sys
d=json.load(sys.stdin)
r=d.get('receipt') or {}
print('  outcome:', r.get('outcome'))
print('  policy_id:', r.get('policy_id'))
print('  receipt_checksum:', r.get('receipt_checksum'))
print('  spine_event_id:', r.get('spine_event_id'))
"
pause 2
echo ""

echo "[2:30] BEAT 3 — Tamper receipt → validator FAIL"
pause 1
bash scripts/validate-demo-enforcement-v1.sh --tamper-test
pause 2
echo ""

echo "=============================================="
echo " ASSET B DEMO COMPLETE — attach policy JSON on outreach"
echo " SOW: docs/asset-b-policy-pack/SOW_MAPPING_LOCKED_v1.md"
echo "=============================================="
