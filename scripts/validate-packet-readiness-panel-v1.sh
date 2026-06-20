#!/usr/bin/env bash
# sa-0618 / sa-0643 — hub ui_contract renderPacketReadinessPanel + D15.2 packet_readiness surface
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
from pathlib import Path

import system_roadmap as sr
from pre_llm.packet_readiness.hub_surface import packet_readiness_hub_payload

ROOT = Path.cwd()
app_js = (ROOT / "agent-control-panel/assets/app.js").read_text(encoding="utf-8")
audit_src = (ROOT / "scripts/audit_hub_source_alignment.py").read_text(encoding="utf-8")

for needle in (
    "function renderPacketReadinessPanel",
    "renderPacketReadinessPanel(",
    "sc-packet-ready",
    "packet-readiness-panel",
    "readiness_pct",
    "section_rows",
    "gate_eligible",
):
    assert needle in app_js, f"app.js missing packet readiness UI hook: {needle}"

assert "renderPacketReadinessPanel" in audit_src, "audit_hub_source_alignment must require renderPacketReadinessPanel"

api = packet_readiness_hub_payload(task_id="validate-d15-2-panel")
assert api.get("ok"), api
assert api.get("producer") == "D15.2"
assert api.get("readiness_pct") is not None
assert len(api.get("section_rows") or []) >= 9

payload = sr.system_roadmap_payload()
pr = payload.get("packet_readiness") or {}
assert pr.get("ok"), "system_roadmap.packet_readiness missing"
assert pr.get("readiness_pct") is not None
assert pr.get("section_rows"), "packet_readiness.section_rows empty"

ui = payload.get("ui_contract") or {}
assert ui.get("packet_readiness_api") == "/api/packet-readiness-v1" or api.get("api") == "/api/packet-readiness-v1"

print(
    f"OK: validate-packet-readiness-panel-v1 · pct={pr.get('readiness_pct')} "
    f"rows={len(pr.get('section_rows') or [])} eligible={pr.get('gate_eligible')}"
)
PY
