#!/usr/bin/env bash
# sa-0655 — L1 workspace state from hub tab POST signals
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
import json
import urllib.request

from pre_llm.user_signals.store import SCHEMA, WORKSPACE_PATH, load_workspace_state
from system_roadmap import system_roadmap_payload

HUB = "http://127.0.0.1:13020/api/user-workspace-signals-v1"


def post(body: dict) -> dict:
    req = urllib.request.Request(
        HUB,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


touch = post(
    {
        "action": "touch",
        "hub_tab": "validate-l1-workspace",
        "active_repo": "SourceA",
        "active_thread": "sa-0655",
        "source": "validator",
    }
)
assert touch.get("ok") is True, touch
assert touch.get("l1_status") in ("done", "partial"), touch
ws = touch.get("workspace_state") or {}
assert ws.get("hub_tab") == "validate-l1-workspace", ws
assert ws.get("active_repo") == "SourceA", ws

files = post(
    {
        "action": "workspace",
        "open_files": ["scripts/pre_llm/user_signals/api.py"],
        "source": "validator",
    }
)
assert files.get("ok") is True, files
ws2 = files.get("workspace_state") or {}
assert ws2.get("open_files"), ws2

assert WORKSPACE_PATH.is_file(), WORKSPACE_PATH
disk = load_workspace_state()
assert disk.get("schema") == SCHEMA, disk
assert disk.get("hub_tab"), disk

sr = system_roadmap_payload()
lc = {r["layer"]: r for r in (sr.get("world_target_map") or {}).get("layer_comparison") or []}
assert lc.get("L1", {}).get("your_status") == "done", lc.get("L1")

print(
    "OK: validate-l1-workspace-state-hub-post-v1 · "
    f"hub_tab={disk.get('hub_tab')} l1={touch.get('l1_status')}"
)
PY
