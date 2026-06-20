#!/usr/bin/env bash
# Tier 4 — product signal + intelligence pipeline files
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MONO="$HOME/Desktop/SinaaiMonoRepo"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

[[ -f "$MONO/n8n/workflows/sinaai-product-signal-webhook.json" || -f "$ROOT/n8n/workflows/sinaai-product-signal-webhook.json" ]] && check true "WF3 product signal" || check false "WF3"
[[ -f "$MONO/n8n/workflows/sinaai-intelligence-pipeline.json" ]] && check true "WF2 intelligence pipeline" || check false "WF2"

export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
out=$(python3 "$ROOT/scripts/n8n_glue_runner_v1.py" signal-ingest --payload '{"source":"mac-health-guard","event":"test_heal","action":"heal"}' 2>/dev/null || echo '{"ok":false}')
ok=$(python3 -c "import json,sys; print('true' if json.load(sys.stdin).get('ok') else 'false')" <<<"$out")
check "$ok" "signal-ingest"

[[ -f "$HOME/.sina/n8n-intelligence/signals.jsonl" ]] && check true "signals.jsonl" || check false "signals.jsonl"

if [[ $fail -eq 0 ]]; then
  python3 -c "import json; from datetime import datetime,timezone; from pathlib import Path; p=Path.home()/'.sina/n8n-receipts/intelligence/tier4-pass.json'; p.write_text(json.dumps({'schema':'tier-gate-v1','tier':4,'at':datetime.now(timezone.utc).isoformat(),'ok':True}, indent=2))"
  echo "validate-n8n-tier4-v1: PASS"
  exit 0
fi
echo "validate-n8n-tier4-v1: FAIL"
exit 1
