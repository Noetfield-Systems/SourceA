#!/usr/bin/env bash
# Tier 2 — queue sweep, disk wire, cpu pause
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

for wf in wf-factory-queue-sweeper-v1 wf-disk-live-wire-watchdog-v1 wf-n8n-self-pause-cpu-v1; do
  [[ -f "$ROOT/n8n/workflows/${wf}.json" ]] && check true "$wf.json" || check false "$wf.json"
done

export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
for cmd in queue-sweep disk-wire cpu-pause-check; do
  out=$(python3 "$ROOT/scripts/n8n_glue_runner_v1.py" "$cmd" 2>/dev/null || echo '{"ok":false}')
  ok=$(python3 -c "import json,sys; print('true' if json.load(sys.stdin).get('ok') else 'false')" <<<"$out")
  check "$ok" "glue $cmd"
done

if [[ $fail -eq 0 ]]; then
  python3 -c "import json; from datetime import datetime,timezone; from pathlib import Path; p=Path.home()/'.sina/n8n-receipts/health/tier2-pass.json'; p.write_text(json.dumps({'schema':'tier-gate-v1','tier':2,'at':datetime.now(timezone.utc).isoformat(),'ok':True}, indent=2))"
  echo "validate-n8n-tier2-v1: PASS"
  exit 0
fi
echo "validate-n8n-tier2-v1: FAIL"
exit 1
