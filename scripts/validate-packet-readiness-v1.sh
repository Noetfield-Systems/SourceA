#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import json
import urllib.request

from pre_llm.packet_readiness.hub_surface import packet_readiness_hub_payload
from system_roadmap import system_roadmap_payload

api = packet_readiness_hub_payload(task_id="validate-d15-2")
assert api.get("ok"), api
assert api.get("producer") == "D15.2"
assert api.get("schema") == "packet-readiness-hub-v1"
assert "readiness_pct" in api
assert "gate_eligible" in api
assert "section_rows" in api and len(api["section_rows"]) >= 9
assert api.get("api") == "/api/packet-readiness-v1"

sr = system_roadmap_payload()
pr = sr.get("packet_readiness") or {}
assert pr.get("ok"), "system_roadmap.packet_readiness missing"
assert pr.get("readiness_pct") is not None

with urllib.request.urlopen("http://127.0.0.1:13020/api/packet-readiness-v1", timeout=60) as resp:
    live = json.loads(resp.read())
assert live.get("ok"), live
assert live.get("producer") == "D15.2"

print(
    "PASS packet readiness v1",
    "pct",
    api.get("readiness_pct"),
    "eligible",
    api.get("gate_eligible"),
    "mode",
    api.get("gate_mode"),
)
PY
