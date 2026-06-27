#!/usr/bin/env bash
# Production Brain live smoke — sourcea.app CDN assets + worker GET + stranger API prompts.
# Part A only (docs/SOURCEA_UI_STANDARD_RUBRIC_LOCKED_v1.md Phase 2). Not taste / desire grading.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${SOURCEA_E2E_BASE:-https://sourcea.app}"
RECEIPT_LOG="${HOME}/.sina/e2e-logs/validate-sourcea-brain-live-v1.log"
RECEIPT_JSON="${HOME}/.sina/enforcement/sourcea-brain-live-gate-receipt-v1.json"
mkdir -p "$(dirname "$RECEIPT_LOG")" "$(dirname "$RECEIPT_JSON")"

echo "=== brain live production smoke (${BASE}) ===" | tee "$RECEIPT_LOG"

echo "=== production assets HTTP ===" | tee -a "$RECEIPT_LOG"
for url in \
  "${BASE}/sourcea/forge/" \
  "${BASE}/sourcea/sourcea-chatbot.js" \
  "${BASE}/sourcea/sourcea.css" \
  "${BASE}/sourcea/data/sourcea-brain-chat-config-v1.json" \
  "${BASE}/sourcea/data/sourcea-positioning-v1.json"; do
  code="$(curl -sS -o /dev/null -w '%{http_code}' "$url" || echo 000)"
  [[ "$code" == "200" || "$code" == "302" ]] || { echo "FAIL $url -> $code" | tee -a "$RECEIPT_LOG"; exit 1; }
  echo "OK $code $url" | tee -a "$RECEIPT_LOG"
done

echo "=== production brain config ===" | tee -a "$RECEIPT_LOG"
CONFIG_JSON="$(curl -fsS "${BASE}/sourcea/data/sourcea-brain-chat-config-v1.json")"
WORKER_URL="$(echo "$CONFIG_JSON" | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('schema') == 'sourcea-brain-chat-config-v1', row.get('schema')
url = row.get('api_worker_url') or ''
assert url.startswith('https://'), url
print(url)
")"
echo "OK worker_url $WORKER_URL" | tee -a "$RECEIPT_LOG"

echo "=== production chatbot.js invariants ===" | tee -a "$RECEIPT_LOG"
CHATBOT_JS="$(curl -fsS "${BASE}/sourcea/sourcea-chatbot.js")"
export CHATBOT_JS
python3 - <<'PY' | tee -a "$RECEIPT_LOG"
import os, sys
js = os.environ["CHATBOT_JS"]
checks = [
    ("execution_greet", "AI execution platform powered by Forge" in js),
    ("forge_chip_in_chat", "What is Forge Terminal and how do I try it" in js),
    ("pricing_chip_in_chat", "How does SourceA pricing work" in js),
    ("no_old_subtitle", "Your SourceA guide — proof, pricing" not in js),
    ("no_old_placeholder", "Ask about proof, pricing, Forge Terminal" not in js),
    ("no_forge_chip_nav", 'Try Forge Terminal", accent: true, action: () => (window.location.href = "/sourcea/forge/terminal")' not in js),
    ("offline_a11y", "syncOfflineBanner" in js and "aria-hidden" in js),
    ("head_main_layout", "sa-brain-head-main" in js),
]
for name, ok in checks:
    assert ok, name
    print("OK", name)
PY

echo "=== production worker GET ===" | tee -a "$RECEIPT_LOG"
STATUS_JSON="$(curl -fsS "$WORKER_URL")"
echo "$STATUS_JSON" | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('openrouter_ready'), row
hint = (row.get('hint') or '').lower()
assert 'site assistant' not in hint or 'execution' in hint, row.get('hint')
print('OK openrouter_ready hint=', row.get('hint', '')[:80])
" | tee -a "$RECEIPT_LOG"

echo "=== production CORS preflight ===" | tee -a "$RECEIPT_LOG"
CORS_CODE="$(curl -sS -o /dev/null -w '%{http_code}' -X OPTIONS "$WORKER_URL" \
  -H "Origin: ${BASE}" \
  -H "Access-Control-Request-Method: POST" || echo 000)"
[[ "$CORS_CODE" == "204" || "$CORS_CODE" == "200" ]] || { echo "FAIL CORS OPTIONS $CORS_CODE"; exit 1; }
echo "OK CORS OPTIONS $CORS_CODE" | tee -a "$RECEIPT_LOG"

echo "=== stranger prompts (production worker) ===" | tee -a "$RECEIPT_LOG"

post_brain() {
  local label="$1"
  local msg="$2"
  local py="$3"
  local json
  json="$(curl -fsS -X POST "$WORKER_URL" \
    -H 'Content-Type: application/json' \
    -d "$(python3 -c "import json; print(json.dumps({'message': '''$msg'''}))")")" || echo '{}'
  echo "$json" | python3 -c "$py" | tee -a "$RECEIPT_LOG"
}

post_brain "what-is" "What is SourceA?" 'import json,sys
row=json.load(sys.stdin)
assert row.get("ok"), row.get("reply") or row
reply=(row.get("reply") or "").lower()
assert "forge" in reply, reply[:200]
assert "execution" in reply or "automate" in reply or "build" in reply, reply[:200]
print("OK what-is:", (row.get("reply") or "")[:100])'

post_brain "ide-cloud" "Do you have IDE cloud?" 'import json,sys
row=json.load(sys.stdin)
assert row.get("ok"), row
reply=(row.get("reply") or "").lower()
assert "forge" in reply, reply[:200]
assert "forge/terminal" in reply.replace(" ", "") or "forge terminal" in reply, reply[:200]
print("OK ide-cloud")'

post_brain "records-recovery" "You just give me records??" 'import json,sys
row=json.load(sys.stdin)
assert row.get("ok"), row
reply=(row.get("reply") or "").lower()
assert "record" in reply
assert any(w in reply for w in ("forge", "run", "execution", "work")), reply[:200]
print("OK records-recovery")'

python3 - <<PY | tee -a "$RECEIPT_LOG"
import json, time
from pathlib import Path
row = {
    "schema": "sourcea-brain-live-gate-receipt-v1",
    "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "ok": True,
    "verdict": "PASS",
    "base": "${BASE}",
    "worker_url": "${WORKER_URL}",
    "checks": ["assets_200", "chatbot_invariants", "worker_get", "cors", "stranger_what_is", "stranger_ide", "stranger_records"],
    "law_ref": "docs/SOURCEA_UI_STANDARD_RUBRIC_LOCKED_v1.md",
}
Path("${RECEIPT_JSON}").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
print("OK receipt", "${RECEIPT_JSON}")
PY

echo "validate-sourcea-brain-live-v1.sh: ALL PASS" | tee -a "$RECEIPT_LOG"
