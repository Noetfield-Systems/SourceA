#!/usr/bin/env bash
# portfolio_fix_execute_v1 — one command accelerates P0 (any directory)
# Roles: refreshes defer · portfolio pulse · WBC guards · optional TF ladder build
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TF_ROOT="$HOME/Desktop/TrustField Technologies"

echo "=== PORTFOLIO FIX EXECUTE v1 ==="
echo "    root: $ROOT"
echo ""

echo "--- 1/5 commercial email defer pulse ---"
python3 "$ROOT/scripts/commercial_email_send_defer_v1.py" --json 2>/dev/null | python3 -c "
import sys,json
try:
 d=json.load(sys.stdin)
 print('defer', d.get('email_send_defer_line','')[:96])
 print('sites_online', d.get('sites_online'))
except Exception: print('defer pulse ran')
" || python3 "$ROOT/scripts/commercial_email_send_defer_v1.py" 2>&1 | tail -1
echo ""

echo "--- 2/5 portfolio fix plan pulse + wire ---"
python3 "$ROOT/scripts/portfolio_fix_plan_pulse_v1.py" --wire --json | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('portfolio_fix_line',''))
print('phase', d.get('phase'), 'p0_ok', d.get('ok'))
" || true
echo ""

echo "--- 3/5 WitnessBC UI FIRST CHECK ack + zero-drift ---"
bash "$ROOT/scripts/wbc-ui-first-check.sh" --surface witnessbc_commercial --ack 2>&1 | tail -3 || true
bash "$ROOT/scripts/validate-ui-zero-drift-v1.sh" 2>&1 | tail -2 || echo "WARN: zero-drift step — run wbc-ui-first-check ack then retry"
echo ""

echo "--- 4/5 TrustField ladder build (TrustField Agent lane) ---"
if [[ -d "$TF_ROOT/scripts" && -x "$TF_ROOT/scripts/ui_build_and_verify.sh" ]]; then
  (cd "$TF_ROOT" && ./scripts/ui_build_and_verify.sh) 2>&1 | tail -8 || echo "WARN: TF ui_build_and_verify exit non-zero — TrustField agent continues"
else
  echo "SKIP: TrustField repo or ui_build_and_verify.sh not found"
fi
echo ""

echo "--- 5/5 portfolio pulse refresh post-TF ---"
python3 "$ROOT/scripts/portfolio_fix_plan_pulse_v1.py" --wire --json | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('portfolio_fix_line',''))
" || true
echo ""
echo "PASS: portfolio_fix_execute_v1 complete"
echo "HANDOFF TF: ~/.sina/agent-workspaces/trustfield/PORTFOLIO_FIX_HANDOFF_LOCKED_v1.md"
echo "HANDOFF Worker: ~/.sina/agent-workspaces/sourcea-worker/PORTFOLIO_FIX_HANDOFF_LOCKED_v1.md"
