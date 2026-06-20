#!/usr/bin/env bash
# sa-0619 / sa-0644 — packet_memory_merge collect_d6_slots via memory_git_bridge
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
import inspect
from pathlib import Path

from pre_llm.packet_memory_merge.memory_collector import collect_d6_slots
from pre_llm.packet_memory_merge.merge_engine import run_memory_merge_writeback

mc_src = inspect.getsource(__import__("pre_llm.packet_memory_merge.memory_collector", fromlist=["collect_d6_slots"]))
me_src = inspect.getsource(__import__("pre_llm.packet_memory_merge.merge_engine", fromlist=["run_memory_merge_writeback"]))

assert "run_bridge" in mc_src, "collect_d6_slots must call memory_git_bridge run_bridge"
assert "filter_slots" in mc_src, "collect_d6_slots must filter D6 slots"
assert 'source_plane", "D6"' in mc_src or "source_plane', 'D6'" in mc_src
assert "collect_d6_slots" in me_src, "merge_engine must call collect_d6_slots"
assert "d6_slots" in me_src, "merge_engine must merge d6_slots"

root = str(Path.cwd())
slots = collect_d6_slots(
    text="D6 memory git bridge packet merge execution",
    repo_root=root,
    task_id="validate-d6-collector",
    force_refresh=True,
)
assert isinstance(slots, list), slots
for row in slots[:3]:
    assert row.get("source_plane") == "D6", row

print(f"OK: validate-packet-memory-merge-d6-collector-v1 · d6_slots={len(slots)}")
PY
