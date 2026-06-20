#!/usr/bin/env bash
# Tier 1 — WF1 v2 + WF8 cooldown ingest + Mac Health E2E
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

[[ -f "$ROOT/n8n/workflows/sinaai-stack-health-ping.json" ]] && check true "WF1 v2 logged" || check false "WF1 v2"
[[ -f "$ROOT/n8n/workflows/wf-mac-health-cooldown-v1.json" ]] && check true "WF8 logged" || check false "WF8"

if ! curl -sf -m 3 http://127.0.0.1:5678/healthz >/dev/null; then
  bash "$ROOT/scripts/founder-start-n8n.sh" >/dev/null 2>&1 || true
  sleep 6
fi

export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
overall=$(python3 -c "from n8n_automation import test_health_ping_dry_run; print(test_health_ping_dry_run().get('overall',''))")
[[ "$overall" == "green" || "$overall" == "yellow" ]] && check true "health_ping $overall" || check false "health_ping ($overall)"

gr_ok=$(python3 -c "
import json, subprocess, sys
p = subprocess.run([sys.executable, '$ROOT/scripts/n8n_glue_runner_v1.py', 'health'], capture_output=True, text=True)
try:
    d = json.loads(p.stdout)
except json.JSONDecodeError:
    d = {}
print('true' if d.get('ok') else 'false')
")
check "$gr_ok" "glue runner health"

cd_ok=$(python3 -c "
import json, subprocess, sys
p = subprocess.run([sys.executable, '$ROOT/scripts/n8n_glue_runner_v1.py', 'cooldown-ingest', '--payload', '{\"cpu_after\":42,\"action\":\"cpu_cool_down\",\"event\":\"test\"}'], capture_output=True, text=True)
try:
    d = json.loads(p.stdout)
except json.JSONDecodeError:
    d = {}
print('true' if d.get('ok') else 'false')
")
check "$cd_ok" "cooldown ingest"

[[ -f "$HOME/.sina/n8n-receipts/mac-health/cooldown.jsonl" ]] && check true "cooldown.jsonl" || check false "cooldown.jsonl"

bash "$ROOT/scripts/validate-mac-health-cooldown-e2e-v1.sh" >/dev/null && check true "mac health E2E" || check false "mac health E2E"

if [[ $fail -eq 0 ]]; then
  python3 -c "import json; from datetime import datetime,timezone; from pathlib import Path; p=Path.home()/'.sina/n8n-receipts/health/tier1-pass.json'; p.write_text(json.dumps({'schema':'tier-gate-v1','tier':1,'at':datetime.now(timezone.utc).isoformat(),'ok':True}, indent=2))"
  echo "validate-n8n-tier1-v1: PASS"
  exit 0
fi
echo "validate-n8n-tier1-v1: FAIL"
exit 1
