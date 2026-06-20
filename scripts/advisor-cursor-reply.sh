#!/usr/bin/env bash
# Cursor Advisor chat: send your reply back to Sina Command app.
set -euo pipefail
API="${SINA_COMMAND_API:-http://127.0.0.1:13020}"
REPLY="${*:-}"
if [[ -z "$REPLY" ]]; then
  echo "Usage: advisor-cursor-reply.sh \"Your advisor reply text\"" >&2
  exit 1
fi
export REPLY API
python3 <<'PY'
import json, os, urllib.request
body = json.dumps({"action": "founder_reply", "reply": os.environ["REPLY"]}).encode()
req = urllib.request.Request(
    os.environ["API"] + "/api/advisor/chat",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=30) as r:
    print(r.read().decode())
PY
