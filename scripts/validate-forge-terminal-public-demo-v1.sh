#!/usr/bin/env bash
# Forge Terminal public demo — disk + worker smoke (no Playwright).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GREEN="${ROOT}/SourceA-landing/green-unified"
CONFIG="${GREEN}/data/sourcea-brain-chat-config-v1.json"
RECEIPT="${HOME}/.sina/e2e-logs/validate-forge-terminal-public-demo-v1.log"
BASE="${SOURCEA_E2E_BASE:-https://sourcea.app}"
mkdir -p "$(dirname "$RECEIPT")"

echo "=== forge terminal public demo disk ===" | tee "$RECEIPT"

for f in \
  "${GREEN}/forge/terminal.html" \
  "${GREEN}/sourcea-forge-terminal-demo.js" \
  "${GREEN}/sourcea-forge-terminal-demo.css" \
  "${CONFIG}"; do
  [[ -f "$f" ]] || { echo "FAIL missing $f"; exit 1; }
  echo "OK file $f" | tee -a "$RECEIPT"
done

python3 -c "
from pathlib import Path
html = Path('${GREEN}/forge/terminal.html').read_text(encoding='utf-8')
js = Path('${GREEN}/sourcea-forge-terminal-demo.js').read_text(encoding='utf-8')
checks = [
    ('html sa-ft-status', 'id=\"sa-ft-status\"' in html),
    ('html sa-ft-send', 'id=\"sa-ft-send\"' in html),
    ('html demo js v1.4', 'sourcea-forge-terminal-demo.js?v=1.4.1' in html),
    ('html preconnect worker', 'sourcea-brain-chat-v1' in html),
    ('html forge hub link', 'href=\"/sourcea/forge/\"' in html),
    ('js product forge_terminal', 'PRODUCT = \"forge_terminal\"' in js),
    ('js prompt forge', 'function forgeMission' in js),
    ('js demo version', 'DEMO_VERSION = \"1.4.1\"' in js),
]
for name, ok in checks:
    assert ok, name
    print('OK', name)
" | tee -a "$RECEIPT"

echo "=== brain chat worker forge_terminal product ===" | tee -a "$RECEIPT"
WORKER_URL="$(python3 -c "import json; print(json.load(open('${CONFIG}'))['api_worker_url'])")"
curl -fsS -X POST "$WORKER_URL" \
  -H 'Content-Type: application/json' \
  -d '{"action":"status","product":"forge_terminal"}' | python3 -c "
import json, sys
row = json.load(sys.stdin)
ready = row.get('ai_model_ready', row.get('openrouter_ready'))
assert ready, row
provider = row.get('provider') or ('openrouter' if row.get('openrouter_ready') else 'unknown')
print(f'OK worker status ai_model_ready provider={provider}')
" | tee -a "$RECEIPT"

curl -fsS -X POST "$WORKER_URL" \
  -H 'Content-Type: application/json' \
  -d '{"action":"chat","product":"forge_terminal","message":"GOAL: test public demo\n\nFounder input: What is Forge Terminal in one sentence?"}' | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('ok'), row.get('reply') or row
reply = (row.get('reply') or '').strip()
assert len(reply) > 30, reply
low = reply.lower()
assert 'openrouter' not in low
print('OK forge_terminal reply:', reply[:100] + ('…' if len(reply) > 100 else ''))
" | tee -a "$RECEIPT"

echo "=== public URLs (${BASE}) ===" | tee -a "$RECEIPT"
for url in \
  "${BASE}/sourcea/forge/terminal" \
  "${BASE}/forge/terminal" \
  "${BASE}/sourcea/sourcea-forge-terminal-demo.js?v=1.4.1" \
  "${BASE}/sourcea/data/sourcea-brain-chat-config-v1.json"; do
  code="$(curl -sS -o /dev/null -w '%{http_code}' "$url" || echo 000)"
  [[ "$code" == "200" || "$code" == "302" ]] || { echo "FAIL $url -> $code"; exit 1; }
  echo "OK $code $url" | tee -a "$RECEIPT"
done

echo "validate-forge-terminal-public-demo-v1.sh: ALL PASS" | tee -a "$RECEIPT"
python3 -c "
import json, time
from pathlib import Path
p = Path.home() / '.sina' / 'forge-terminal-public-demo-e2e-v1.json'
p.write_text(json.dumps({
  'schema': 'forge-terminal-public-demo-e2e-v1',
  'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
  'base': '${BASE}',
  'demo_version': '1.4.1',
  'ok': True,
}, indent=2) + '\n', encoding='utf-8')
print('OK receipt', p)
" | tee -a "$RECEIPT"
