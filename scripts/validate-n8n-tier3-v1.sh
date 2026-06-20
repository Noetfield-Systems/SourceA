#!/usr/bin/env bash
# Tier 3 — governance fast, poison track, factory stuck (notify only)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

for wf in wf-governance-fast-15m-v1 wf-poison-track-reminder-v1 wf-run-inbox-reminder-v1; do
  [[ -f "$ROOT/n8n/workflows/${wf}.json" ]] && check true "$wf.json" || check false "$wf.json"
done

export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
for cmd in poison-track factory-stuck; do
  out=$(python3 "$ROOT/scripts/n8n_glue_runner_v1.py" "$cmd" 2>/dev/null || echo '{"ok":false}')
  ok=$(python3 -c "import json,sys; print('true' if json.load(sys.stdin).get('ok') else 'false')" <<<"$out")
  check "$ok" "glue $cmd"
done

# governance-fast may take time — check receipt file grows
before=$(wc -l < "$HOME/.sina/n8n-receipts/governance/wf-governance-fast-15m.jsonl" 2>/dev/null || echo 0)
python3 "$ROOT/scripts/n8n_glue_runner_v1.py" governance-fast >/dev/null 2>&1 || true
after=$(wc -l < "$HOME/.sina/n8n-receipts/governance/wf-governance-fast-15m.jsonl" 2>/dev/null || echo 0)
[[ "$after" -gt "$before" ]] && check true "glue governance-fast receipt" || check false "glue governance-fast receipt"

grep -q 'factory-stuck' "$ROOT/scripts/n8n_glue_runner_v1.py" && check true "factory-stuck wired" || check false "factory-stuck"
! grep -q 'auto.run\|inject_cursor' "$ROOT/n8n/workflows/wf-run-inbox-reminder-v1.json" && check true "no auto-run in WF10" || check false "auto-run leak"

if [[ $fail -eq 0 ]]; then
  python3 -c "import json; from datetime import datetime,timezone; from pathlib import Path; p=Path.home()/'.sina/n8n-receipts/governance/tier3-pass.json'; p.write_text(json.dumps({'schema':'tier-gate-v1','tier':3,'at':datetime.now(timezone.utc).isoformat(),'ok':True}, indent=2))"
  echo "validate-n8n-tier3-v1: PASS"
  exit 0
fi
echo "validate-n8n-tier3-v1: FAIL"
exit 1
