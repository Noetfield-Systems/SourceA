#!/usr/bin/env bash
# validate-n8n-chat-unify-wire-v1.sh — n8n ↔ Chat Unify ↔ Cursor glue gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

[[ -f "$ROOT/scripts/n8n_chat_unify_wire_v1.py" ]] && check true "wire script" || check false "wire script"
grep -q 'chat_unify_merge' "$ROOT/scripts/n8n_glue_config_v1.py" && check true "glue config webhook" || check false "glue config"

python3 "$ROOT/scripts/n8n_chat_unify_wire_v1.py" --wire --json >/dev/null
[[ -f "$SINA/n8n-chat-unify-wire-v1.json" ]] && check true "wire receipt" || check false "wire receipt"

python3 - <<'PY' || { echo "FAIL: wire status"; fail=1; }
import json
from pathlib import Path
r = json.loads((Path.home()/".sina/n8n-chat-unify-wire-v1.json").read_text())
st = r.get("status") or {}
assert st.get("chat_unify_up"), st
assert st.get("n8n_up"), st
assert st.get("merge_workflow_active"), st
assert st.get("wired"), st
print("PASS: wired status")
PY

python3 - <<'PY' || { echo "FAIL: direct glue ingest"; fail=1; }
import json, subprocess
from pathlib import Path
proc = subprocess.run(
    ["python3", str(Path.home()/ "Desktop/SourceA/scripts/n8n_glue_runner_v1.py"), "chat-unify-merge", "--payload", json.dumps({"event":"validator","extract_count":0})],
    capture_output=True, text=True, timeout=60,
)
body = json.loads(proc.stdout or "{}")
assert body.get("ok"), body
print("PASS: chat-unify-merge glue command")
PY

curl -sf http://127.0.0.1:13023/health >/dev/null && check true "chat unify health" || check false "chat unify health"
curl -sf http://127.0.0.1:13026/health >/dev/null && check true "n8n integration health" || check false "n8n integration"

python3 - <<'PY' || { echo "FAIL: chat unify n8n_wire in report"; fail=1; }
import json, urllib.request
req = urllib.request.Request(
    "http://127.0.0.1:13023/api/chat-unify",
    data=json.dumps({"action": "report"}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=15) as resp:
    d = json.loads(resp.read().decode())
assert d.get("ok"), d
assert "n8n_wire" in d, d.keys()
print("PASS: chat unify report n8n_wire")
PY

python3 - <<'PY' || { echo "FAIL: integration wire action"; fail=1; }
import json, urllib.request
req = urllib.request.Request(
    "http://127.0.0.1:13026/api/n8n-integration",
    data=json.dumps({"action": "report"}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=15) as resp:
    d = json.loads(resp.read().decode())
assert d.get("ok"), d
assert d.get("version") == "1.6.0", d.get("version")
assert "chat_unify_wire" in d, d.keys()
print("PASS: integration report chat_unify_wire")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-n8n-chat-unify-wire-v1"
  exit 0
fi
echo "FAIL: validate-n8n-chat-unify-wire-v1"
exit 1
