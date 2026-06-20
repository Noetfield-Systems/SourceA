#!/usr/bin/env bash
# sa-0654 — L0 MVP user_signals_v1.json artifact when hub touched
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
from pre_llm.user_signals.store import SCHEMA, SIGNALS_PATH, hub_payload, load_signals
from system_roadmap import _artifact_exists, system_roadmap_payload

assert SIGNALS_PATH.is_file(), f"missing L0 artifact: {SIGNALS_PATH}"
assert _artifact_exists("user_signals_v1.json"), "system_roadmap must see user_signals_v1.json"

sig = load_signals()
assert sig.get("schema") == SCHEMA, sig.get("schema")
assert sig.get("signals"), "user_signals_v1.json must have hub touch rows"
assert sig.get("last_refresh_at") or sig.get("last_hub_tab"), sig

api = hub_payload()
assert api.get("ok") is True, api
assert api.get("l0_status") == "done", api
assert int(api.get("signal_count") or 0) > 0, api

sr = system_roadmap_payload()
uws = sr.get("user_workspace_signals") or {}
assert uws.get("ok") is True, uws
lc = {r["layer"]: r for r in (sr.get("world_target_map") or {}).get("layer_comparison") or []}
assert lc.get("L0", {}).get("your_status") == "done", lc.get("L0")

print(
    "OK: validate-user-signals-v1-artifact-v1 · "
    f"path={SIGNALS_PATH.name} signals={api.get('signal_count')} l0={api.get('l0_status')}"
)
PY
