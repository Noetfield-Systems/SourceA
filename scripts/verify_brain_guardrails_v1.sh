#!/usr/bin/env bash
# Brain guardrails — positioning verify + live chat smoke.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== verify_brain_guardrails_v1 ==="
bash "$ROOT/scripts/validate-sourcea-brain-chat-v1.sh"

CONFIG="${ROOT}/SourceA-landing/green-unified/data/sourcea-brain-chat-config-v1.json"
WORKER_URL="$(python3 -c "import json; print(json.load(open('$CONFIG'))['api_worker_url'])")"
REPLY_JSON="$(curl -fsS -X POST "$WORKER_URL" \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is SourceA?","page_path":"/"}' 2>/dev/null || echo '{}')"

echo "$REPLY_JSON" | python3 -c "
import json, sys, subprocess
row = json.load(sys.stdin)
msg = row.get('message') or 'What is SourceA?'
proc = subprocess.run(
    [sys.executable, '$ROOT/scripts/verify_brain_reply_positioning_v1.py',
     '--reply', row.get('reply') or '', '--message', msg,
     '--intent', (row.get('retrieval') or {}).get('intent') or 'core', '--json'],
    capture_output=True, text=True,
)
print(proc.stdout or proc.stderr)
sys.exit(0 if json.loads(proc.stdout or '{}').get('ok') else 1)
"
echo "verify_brain_guardrails_v1.sh: ALL PASS"
