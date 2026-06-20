#!/usr/bin/env bash
# Paste the current AI's answer from Chrome into the SEMEJ loop (self-heal / manual path).
set -euo pipefail
API="${SINA_COMMAND_API:-http://127.0.0.1:13020}"
ANSWER="${*:-}"
if [[ -z "$ANSWER" ]]; then
  echo "Usage: semej-inject-answer.sh \"Full answer text from Gemini/ChatGPT/...\"" >&2
  exit 1
fi
export ANSWER API
python3 <<'PY'
import json, os, urllib.request
body = json.dumps({"action": "response", "response": os.environ["ANSWER"]}).encode()
req = urllib.request.Request(
    os.environ["API"] + "/api/semej",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode())
PY
