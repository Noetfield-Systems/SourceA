#!/usr/bin/env bash
# Pre-sleep monitor — one screen. Run anytime while verifying Phase 1.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     PRE-SLEEP TRANSITION — ASF monitors, Claude proves  ║"
echo "║     Law: PRE_SLEEP_TRANSITION_LOCKED_v1.md              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "GOVERNANCE: ASF in charge → [PRE-SLEEP you are here] → Claude team (sleep)"
echo "  Pre-sleep: Worker MAY run + CLI+API+OpenRouter PROVE alive"
echo "  Sleep:     Claude team (CLI+API+Pro) owns boss queue — Worker OFF"
echo ""

python3 scripts/brain_read_state_v1.py --caller pre_sleep_monitor 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
hb=d.get('heartbeat') or {}
print('ALIGNMENT     ', '✅ GREEN' if d.get('aligned') else '❌ RED')
print('Worker turn   ', hb.get('sa_id'), (d.get('inbox') or {}).get('role'), 'pos', hb.get('queue_pos'), '/', hb.get('queue_total'))
print('INBOX pending ', (d.get('inbox') or {}).get('pending'))
print('Orchestrator  ', (d.get('orchestrator') or {}).get('status'))
print('Report block  ', d.get('report_blocks_advance'))
"

python3 scripts/goal-progress-v1.py --json 2>/dev/null | python3 -c "
import json,sys
g=json.load(sys.stdin).get('goal_1') or {}
print('Registry      ', f\"{g.get('done')}/{g.get('total')} ({g.get('pct')}%)\")
"

echo ""
echo "── Lanes ──"
wp="$HOME/.sina/sidecar-engines-watch-v1.pid"
if [[ -f "$wp" ]] && kill -0 "$(cat "$wp")" 2>/dev/null; then
  echo "API+CLI watch ✅ ALIVE pid=$(cat "$wp")"
else
  echo "API+CLI watch ❌ DEAD"
fi
op="$HOME/.sina/overnight-3engine-v1.pid"
if [[ -f "$op" ]] && kill -0 "$(cat "$op")" 2>/dev/null; then
  echo "Overnight disp  ⚠️  RUNNING (should be OFF in Phase 1)"
else
  echo "Overnight disp  ✅ OFF (correct Phase 1)"
fi
[[ -f "$HOME/.sina/auto-run-disabled-v1.flag" ]] && echo "Autorun flag    ✅ ON (Worker lane only)" || echo "Autorun flag    ⚠️  absent"

echo ""
echo "── Sidecar outputs (latest) ──"
ls -t "$HOME/.sina/sidecar/api-scout/" 2>/dev/null | head -1 | xargs -I{} echo "API scout       {}" || echo "API scout       (none)"
ls -t "$HOME/.sina/sidecar/cli-prep/" 2>/dev/null | head -1 | xargs -I{} echo "CLI prep        {}" || echo "CLI prep        (none)"

echo ""
python3 scripts/gatekeeper_v1.py 2>/dev/null | head -1 | sed 's/^/Gatekeeper      /'

echo ""
echo "── Four-engine probe ──"
bash "$ROOT/scripts/pre-sleep-engine-probe-v1.sh" 2>/dev/null || true

echo ""
echo "── Approve sleep when ALL true ──"
echo "  • 3+ Worker turns advanced without sa_mismatch"
echo "  • sidecar watch ALIVE + new scout/prep after each advance"
echo "  • gatekeeper PASS after each ACTIVE_NOW sync"
echo "  • YOU say: arm sleep"
echo ""
echo "Monitor (live UI): http://127.0.0.1:13021/monitor"
echo "  Hub Actions → Open Pre-Sleep Monitor  (or Connected Apps → SourceA Monitor)"
echo ""
