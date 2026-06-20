#!/usr/bin/env bash
# Full manifest — 18 glue workflows + deferred telegram
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
fail=0

python3 -c "
import json
from pathlib import Path
m = json.loads((Path('$ROOT')/'scripts/fixtures/n8n/workflow_manifest.json').read_text())
ids = [w['id'] for w in m.get('workflows', []) if not w.get('deferred')]
assert len(ids) >= 18, f'expected 18+ workflows got {len(ids)}'
deferred = m.get('deferred') or []
print('PASS: manifest', len(ids), 'workflows', len(deferred), 'deferred')
" || fail=1

for wf in wf-agent-scoreboard-sync-v1 wf-founder-request-registrar-v1 wf-semej-session-bookend-v1 wf-backup-receipt-archiver-v1 wf-chat-unify-merge-receipt-v1; do
  [[ -f "$ROOT/n8n/workflows/${wf}.json" ]] && echo "PASS: $wf" || { echo "FAIL: $wf"; fail=1; }
done

export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
python3 "$ROOT/scripts/n8n_glue_runner_v1.py" scoreboard-sync >/dev/null && echo "PASS: scoreboard-sync" || { echo "FAIL: scoreboard-sync"; fail=1; }

if [[ $fail -eq 0 ]]; then
  python3 -c "
import json
from datetime import datetime, timezone
from pathlib import Path
p = Path.home() / '.sina/n8n-receipts/FINAL_AUTOMATION_PASS_v2.json'
p.write_text(json.dumps({
  'schema': 'final-automation-pass-v2',
  'at': datetime.now(timezone.utc).isoformat(),
  'ok': True,
  'tiers': [0,1,2,3,4,5,6],
  'hub_mode': json.loads((Path.home()/'.sina/n8n-glue-config-v1.json').read_text()).get('hub_mode'),
}, indent=2))
print('PASS: FINAL_AUTOMATION_PASS_v2.json')
"
  echo "validate-n8n-full-manifest-v1: PASS"
  exit 0
fi
echo "validate-n8n-full-manifest-v1: FAIL"
exit 1
