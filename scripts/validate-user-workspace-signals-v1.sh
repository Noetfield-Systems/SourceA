#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import json
import urllib.request

from pre_llm.user_signals.store import record_hub_touch, hub_payload
from system_roadmap import system_roadmap_payload

record_hub_touch(hub_tab="system-roadmap", active_repo="SourceA", source="validator")
api = hub_payload()
assert api.get("ok"), api
assert api.get("l0_status") == "done", api
assert api.get("l1_status") in ("done", "partial"), api

sr = system_roadmap_payload()
uws = sr.get("user_workspace_signals") or {}
assert uws.get("ok"), uws

lc = {r["layer"]: r for r in (sr.get("world_target_map") or {}).get("layer_comparison") or []}
assert lc.get("L0", {}).get("your_status") == "done"
assert lc.get("L1", {}).get("your_status") == "done"

with urllib.request.urlopen("http://127.0.0.1:13020/api/user-workspace-signals-v1", timeout=60) as resp:
    live = json.loads(resp.read())
assert live.get("ok"), live
print("OK: validate-user-workspace-signals-v1")
PY
