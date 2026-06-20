#!/usr/bin/env bash
# validate-n8n-tier0-v1.sh — substrate gate (config, receipts, glue runner, mac health)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
fail=0

check() { if [[ "$1" != "true" ]]; then echo "FAIL: $2"; fail=1; else echo "PASS: $2"; fi; }

[[ -f "$SINA/n8n-glue-config-v1.json" ]] && check true "n8n-glue-config" || check false "n8n-glue-config missing"
[[ -d "$SINA/n8n-receipts/health" ]] && check true "receipts/health" || check false "receipts dirs"
[[ -f "$SINA/n8n-workflow-inventory-v2.json" ]] && check true "workflow inventory" || check false "inventory missing"
[[ -f "$SINA/n8n-listener-state-v1.json" ]] && check true "listener state" || check false "listener state missing"

python3 "$ROOT/scripts/n8n_glue_runner_v1.py" --help >/dev/null 2>&1 || python3 "$ROOT/scripts/n8n_glue_runner_v1.py" health >/dev/null
check true "glue runner import"

# Mac Health required; n8n start attempted if down
if ! curl -sf -m 3 http://127.0.0.1:13024/health >/dev/null; then
  echo "FAIL: Mac Health :13024 down"
  fail=1
else
  echo "PASS: Mac Health :13024"
fi

if ! curl -sf -m 3 http://127.0.0.1:5678/healthz >/dev/null; then
  echo "WARN: n8n :5678 down — starting..."
  bash "$ROOT/scripts/founder-start-n8n.sh" >/dev/null 2>&1 || true
  sleep 5
fi
if curl -sf -m 5 http://127.0.0.1:5678/healthz >/dev/null; then
  echo "PASS: n8n :5678"
else
  echo "FAIL: n8n :5678 down after start attempt"
  fail=1
fi

export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
bash "$ROOT/scripts/validate-mac-health-cooldown-e2e-v1.sh" >/dev/null && echo "PASS: mac health E2E" || { echo "FAIL: mac health E2E"; fail=1; }

if [[ $fail -eq 0 ]]; then
  python3 -c "
import json
from datetime import datetime, timezone
from pathlib import Path
p = Path.home() / '.sina/n8n-receipts/health/tier0-pass.json'
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps({'schema':'tier-gate-v1','tier':0,'at':datetime.now(timezone.utc).isoformat(),'ok':True}, indent=2))
print('PASS: tier0-pass.json written')
"
  echo "validate-n8n-tier0-v1: PASS"
  exit 0
fi
echo "validate-n8n-tier0-v1: FAIL"
exit 1
