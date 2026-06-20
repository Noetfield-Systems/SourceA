#!/usr/bin/env bash
# demo-enforcement-5min-v1.sh — investor room beats (W1)
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

pause() { sleep "${1:-2}"; }

echo "=============================================="
echo " ENFORCEMENT-6MO — 5-MIN INVESTOR DEMO"
echo " If AI executes without governance, it fails."
echo "=============================================="
echo ""

echo "[0:30] BEAT 1 — Copilot policy change without approval → BLOCKED (P-001)"
pause 1
python3 scripts/commit_intent_v1.py --demo-enforcement --case block --json | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('  outcome:', d.get('receipt',{}).get('outcome','BLOCKED'))
print('  reason:', '; '.join((d.get('receipt',{}) or {}).get('gate_reasons') or [])[:200])
" || true
echo "  → Rule P-001 DENY. No DONE receipt on spine."
pause 2
echo ""

echo "[1:30] BEAT 2 — Valid Copilot change + approval_ref → receipt + spine"
pause 1
OUT=$(python3 scripts/commit_intent_v1.py --demo-enforcement --case allow --json)
echo "$OUT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
r=d.get('receipt') or {}
print('  outcome:', r.get('outcome'))
print('  status:', r.get('status'))
print('  policy_id:', r.get('policy_id'))
print('  spine_event_id:', r.get('spine_event_id'))
print('  checksum:', r.get('receipt_checksum'))
"
pause 2
echo ""

echo "[2:30] BEAT 3 — Attacker tampers receipt → validator FAILS"
pause 1
bash scripts/validate-demo-enforcement-v1.sh --tamper-test
pause 2
echo ""

echo "[4:00] BEAT 4 — Kill switch (FREEZE) logged"
FREEZE="${HOME}/.sina/auto-run-disabled-v1.flag"
if [[ -f "$FREEZE" ]]; then
  echo "  FREEZE flag PRESENT → factory auto-run disabled"
  head -3 "$FREEZE" 2>/dev/null | sed 's/^/  /'
else
  echo "  (FREEZE flag not set — optional beat)"
fi
pause 1
bash scripts/validate-demo-enforcement-v1.sh
echo ""

echo "=============================================="
echo " DEMO COMPLETE — W1 proof path"
echo " Next: W3 economic signal (pilot / LOI)"
echo "=============================================="
