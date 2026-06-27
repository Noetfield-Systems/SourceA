#!/usr/bin/env bash
# Brain chat — OpenRouter worker + landing config + live reply smoke.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="${ROOT}/SourceA-landing/green-unified/data/sourcea-brain-chat-config-v1.json"
WORKER_URL="${SOURCEA_BRAIN_CHAT_URL:-}"
RECEIPT="${HOME}/.sina/e2e-logs/validate-sourcea-brain-chat-v1.log"
mkdir -p "$(dirname "$RECEIPT")"

if [[ -z "$WORKER_URL" ]]; then
  WORKER_URL="$(python3 -c "import json; print(json.load(open('$CONFIG'))['api_worker_url'])" 2>/dev/null || true)"
fi
[[ -n "$WORKER_URL" ]] || { echo "FAIL: no api_worker_url in $CONFIG"; exit 1; }

echo "=== brain chat config logged ===" | tee "$RECEIPT"
python3 -c "
import json, sys
from pathlib import Path
p = Path('$CONFIG')
row = json.loads(p.read_text())
assert row.get('schema') == 'sourcea-brain-chat-config-v1', row.get('schema')
assert row.get('api_worker_url'), 'missing api_worker_url'
print('OK config', p)
" | tee -a "$RECEIPT"

echo "=== brain chat worker status ===" | tee -a "$RECEIPT"
STATUS_JSON="$(curl -fsS "$WORKER_URL" 2>/dev/null || echo '{}')"
echo "$STATUS_JSON" | python3 -c "
import json, sys
row = json.load(sys.stdin)
ready = row.get('openrouter_ready')
print('openrouter_ready=', ready)
if not ready:
    print('FAIL: OPENROUTER_API_KEY not set on worker — wrangler secret put OPENROUTER_API_KEY')
    sys.exit(1)
print('OK worker status')
" | tee -a "$RECEIPT"

echo "=== brain chat live reply ===" | tee -a "$RECEIPT"
REPLY_JSON="$(curl -fsS -X POST "$WORKER_URL" \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is SourceA in one sentence?"}' 2>/dev/null || echo '{}')"
echo "$REPLY_JSON" | python3 -c "
import json, sys
row = json.load(sys.stdin)
if not row.get('ok'):
    print('FAIL:', row.get('reply') or row.get('error') or row)
    sys.exit(1)
reply = (row.get('reply') or '').strip()
if len(reply) < 20:
    print('FAIL: reply too short:', repr(reply))
    sys.exit(1)
print('OK reply:', reply[:120] + ('…' if len(reply) > 120 else ''))
" | tee -a "$RECEIPT"

echo "=== brain positioning smoke ===" | tee -a "$RECEIPT"
POS_JSON="$(curl -fsS -X POST "$WORKER_URL" \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is SourceA?"}' 2>/dev/null || echo '{}')"
echo "$POS_JSON" | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('ok'), row.get('reply') or row
reply = (row.get('reply') or '').lower()
assert 'forge' in reply, 'missing Forge in what-is answer: ' + reply[:200]
assert 'execution' in reply or 'automate' in reply or 'build' in reply, reply[:200]
assert reply.index('1500') > 80 if '1500' in reply else True, 'price too early in what-is reply'
print('OK positioning what-is')
" | tee -a "$RECEIPT"

IDE_JSON="$(curl -fsS -X POST "$WORKER_URL" \
  -H 'Content-Type: application/json' \
  -d '{"message":"Do you have IDE cloud?"}' 2>/dev/null || echo '{}')"
echo "$IDE_JSON" | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('ok'), row
reply = (row.get('reply') or '').lower()
assert 'forge' in reply, reply[:200]
assert 'forge/terminal' in reply.replace(' ', '') or 'forge terminal' in reply, reply[:200]
print('OK positioning ide cloud')
" | tee -a "$RECEIPT"

REC_JSON="$(curl -fsS -X POST "$WORKER_URL" \
  -H 'Content-Type: application/json' \
  -d '{"message":"You just give me records??"}' 2>/dev/null || echo '{}')"
echo "$REC_JSON" | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('ok'), row
reply = (row.get('reply') or '').lower()
assert 'record' in reply or 'proof' in reply
assert 'forge' in reply or 'run' in reply or 'execution' in reply or 'work' in reply
print('OK positioning records recovery')
" | tee -a "$RECEIPT"

DIST_CFG="${ROOT}/SourceA-landing/green-unified/dist/sourcea/data/sourcea-brain-chat-config-v1.json"
if [[ -f "$DIST_CFG" ]]; then
  echo "=== brain chat config in dist ===" | tee -a "$RECEIPT"
  python3 -c "import json; json.load(open('$DIST_CFG')); print('OK dist config')" | tee -a "$RECEIPT"
fi

echo "validate-sourcea-brain-chat-v1.sh: ALL PASS" | tee -a "$RECEIPT"
