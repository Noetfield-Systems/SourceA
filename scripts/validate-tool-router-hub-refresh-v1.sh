#!/usr/bin/env bash
# sa-0612 — tool_router capability_catalog hub_refresh entry + execute-step selection
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
from pre_llm.tool_router.capability_catalog import _CATALOG
from pre_llm.tool_router.router_engine import run_tool_router

execute = _CATALOG.get("execute") or []
report = _CATALOG.get("report") or []
exec_hr = [c for c in execute if c.get("capability_id") == "hub_refresh"]
rep_hr = [c for c in report if c.get("capability_id") == "hub_refresh"]
assert exec_hr, "hub_refresh missing from execute catalog"
assert rep_hr, "hub_refresh missing from report catalog"
for row in exec_hr + rep_hr:
    assert row.get("tool_id") == "hub/refresh", row
    assert row.get("permission") == "write", row

live = run_tool_router(text="hub refresh rebuild panel", task_id="validate-hub-refresh", force_refresh=True)
assert live.get("ok"), live
sel = [s for s in (live.get("selection") or []) if s.get("capability_id") == "hub_refresh"]
assert sel, f"hub_refresh not selected: {[s.get('capability_id') for s in live.get('selection') or []]}"
assert sel[0].get("tool_id") == "hub/refresh", sel[0]

print(f"OK: validate-tool-router-hub-refresh-v1 · selected={len(sel)} allowed={sel[0].get('allowed')}")
PY
