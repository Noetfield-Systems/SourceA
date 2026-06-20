#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
from pre_llm.memory_git_bridge.api import memory_git_bridge_v1_payload
from pre_llm.memory_git_bridge.store import BRIDGE_SSOT_PATH

QUERY = "spine execution memory gate shadow git"
live = memory_git_bridge_v1_payload(
    text=QUERY,
    task_id="validate-d6",
    force_refresh=True,
    top_k=8,
)
assert live.get("ok"), live
assert BRIDGE_SSOT_PATH.is_file(), "memory_git_bridge_v1.json missing"
assert live.get("bridge_ready"), "bridge_ready false"
assert live.get("slot_count", 0) >= 1, f"no slots: {live.get('slot_count')}"
hits = live.get("hits") or []
assert len(hits) >= 1, "no bridge hits"
pm = live.get("packet_memory") or {}
assert len(pm.get("slots") or []) >= 1, "packet_memory.slots empty"
assert live.get("read_only") is True, "D6 must be read-only"
assert "retrieval substrate" in (live.get("memory_role") or ""), live.get("memory_role")
sources = live.get("sources") or {}
assert sources.get("execution_memory_lines", 0) >= 0
print(
    "PASS memory git bridge v1",
    "slots",
    live.get("slot_count"),
    "hits",
    len(hits),
    "git",
    live.get("git_available"),
)
PY
