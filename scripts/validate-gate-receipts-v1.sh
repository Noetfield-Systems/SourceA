#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import json
import urllib.request

from gate_receipts_hub import gate_receipts_hub_payload
from system_roadmap import system_roadmap_payload

api = gate_receipts_hub_payload()
assert api.get("ok"), api
assert api.get("current_mode") in ("enforce", "shadow", "off")

sr = system_roadmap_payload()
gr = sr.get("gate_receipts") or {}
assert gr.get("ok"), gr
md = gr.get("model_dispatch") or {}
assert md.get("ok"), md
assert md.get("producer") == "model_dispatch.py", md
assert md.get("current_mode") in ("enforce", "shadow", "off"), md

with urllib.request.urlopen("http://127.0.0.1:13020/api/gate-receipts-v1", timeout=60) as resp:
    live = json.loads(resp.read())
assert live.get("ok"), live
live_md = live.get("model_dispatch") or {}
assert live_md.get("ok"), live_md
assert "model_dispatch" in (live.get("coverage_note") or ""), live.get("coverage_note")
print("OK: validate-gate-receipts-v1 · model_dispatch integrated")
PY
