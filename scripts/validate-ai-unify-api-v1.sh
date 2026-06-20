#!/usr/bin/env bash
# validate-ai-unify-api-v1.sh — OpenRouter + Gemini + Chat Unify API wire gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

[[ -f "$ROOT/scripts/ai_unify_api_v1.py" ]] && check true "ai_unify_api script" || check false "ai_unify_api script"
grep -q 'ai_polish' "$ROOT/scripts/chat_unify_merge.py" && check true "chat_unify ai actions" || check false "chat_unify ai actions"
grep -q 'ai_chat' "$ROOT/scripts/n8n_integration_core.py" && check true "n8n integration ai actions" || check false "n8n integration ai actions"
grep -q '/api/ai-unify' "$ROOT/scripts/chat-unify-server.py" && check true "ai-unify HTTP route" || check false "ai-unify HTTP route"

python3 "$ROOT/scripts/ai_unify_api_v1.py" --action status --json >/dev/null
check true "ai status CLI"

python3 - <<'PY' || { echo "FAIL: status schema"; fail=1; }
import json, sys
sys.path.insert(0, "/Users/sinakazemnezhad/Desktop/SourceA/scripts")
from ai_unify_api_v1 import status_payload, pick_provider, handle_action
s = status_payload()
assert s.get("schema") == "ai-unify-api-v1"
assert "openrouter_ready" in s and "gemini_direct_ready" in s
assert pick_provider("auto") in ("openrouter", "gemini_direct", "none")
chat = handle_action({"action": "chat", "user": ""})
assert chat.get("error") == "empty_brief" or not chat.get("ok")
print("PASS: ai_unify_api module")
PY

bash "$ROOT/scripts/serve-chat-unify.sh" status >/dev/null 2>&1 || bash "$ROOT/scripts/serve-chat-unify.sh" start >/dev/null 2>&1 || true
sleep 1

python3 - <<'PY' || { echo "FAIL: chat-unify ai_status HTTP"; fail=1; }
import json, urllib.request
req = urllib.request.Request(
    "http://127.0.0.1:13023/api/chat-unify",
    data=json.dumps({"action": "ai_status"}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=15) as r:
    d = json.loads(r.read().decode())
assert d.get("schema") == "ai-unify-api-v1", d
print("PASS: chat-unify ai_status HTTP")
PY

python3 - <<'PY' || { echo "FAIL: ai-unify direct route"; fail=1; }
import json, urllib.request
with urllib.request.urlopen("http://127.0.0.1:13023/api/ai-unify", timeout=15) as r:
    d = json.loads(r.read().decode())
assert d.get("ok") and d.get("schema") == "ai-unify-api-v1"
print("PASS: GET /api/ai-unify")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-ai-unify-api-v1"
  exit 0
fi
echo "FAIL: validate-ai-unify-api-v1"
exit 1
