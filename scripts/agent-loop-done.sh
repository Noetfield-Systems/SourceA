#!/usr/bin/env bash
# Cursor executing agent: submit loop answer to Sina Command (ends round, triggers next).
set -euo pipefail
API="${SINA_COMMAND_API:-http://127.0.0.1:13020}"
SUMMARY="${1:-done}"
shift || true
RESPONSE="${*:-}"
if [[ -z "$RESPONSE" ]]; then
  RESPONSE="$SUMMARY"
fi
export SUMMARY RESPONSE API
python3 <<'PY'
import json, os, urllib.request
body = json.dumps({
    "action": "response",
    "summary": os.environ["SUMMARY"],
    "response": os.environ["RESPONSE"],
}).encode()
req = urllib.request.Request(
    os.environ["API"] + "/api/agent-loop",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode())
PY
