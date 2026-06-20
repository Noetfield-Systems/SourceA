#!/usr/bin/env bash
# Maintainer: post reply to legacy Live agents API (Worker Hub /legacy/ archive)
set -euo pipefail
API="${SINA_COMMAND_API:-http://127.0.0.1:13020}"
REPLY="${*:-}"
if [[ -z "$REPLY" ]]; then
  echo "Usage: live-agent-cursor-reply.sh \"Your reply to the founder\"" >&2
  exit 1
fi
export REPLY API
python3 <<'PY'
import json, os, sys, urllib.request

reply = os.environ.get("REPLY", "").strip()
if not reply:
    print("error: empty reply", file=sys.stderr)
    sys.exit(1)
sys.path.insert(0, os.path.expanduser("~/Desktop/SourceA/scripts"))
from intelligence_circle import agent_reply_to_maintainer  # noqa: E402

r = agent_reply_to_maintainer(reply)
if not r.get("ok"):
    print(json.dumps(r, indent=2))
    sys.exit(1)
# Sync baked panel JSON so Refresh is not required
try:
    from sina_command_lib import build_payload, write_panel_outputs  # noqa: E402

    payload = build_payload(run_refresh_scripts=False)
    write_panel_outputs(payload)
    r["panel_synced"] = True
except Exception as e:
    r["panel_sync_warning"] = str(e)[:200]
body = json.dumps({"action": "agent_reply", "reply": reply}).encode()
req = urllib.request.Request(
    os.environ["API"] + "/api/intelligence-circle",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        hub = json.loads(resp.read().decode())
        print(json.dumps({"ok": True, "messages": len(r.get("chat_messages") or []), "hub": hub.get("ok")}, indent=2))
except Exception as e:
    print(json.dumps({"ok": True, "messages": len(r.get("chat_messages") or []), "hub_note": str(e)[:120]}, indent=2))
PY
