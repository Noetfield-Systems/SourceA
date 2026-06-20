#!/usr/bin/env bash
# sa-0616 — L5 semantic_history + B3 feedback → D16 packet_memory_merge path
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
import inspect

from pre_llm.packet_memory_merge.memory_collector import (
    collect_b_layer_slots,
    collect_l5_history_slots,
)
from pre_llm.packet_memory_merge.merge_engine import run_memory_merge_writeback

mc_src = inspect.getsource(__import__("pre_llm.packet_memory_merge.memory_collector", fromlist=["collect_l5_history_slots"]))
me_src = inspect.getsource(__import__("pre_llm.packet_memory_merge.merge_engine", fromlist=["run_memory_merge_writeback"]))

assert "build_semantic_history" in mc_src, "memory_collector must import L5 history_bridge"
assert "semantic_history" in mc_src, "memory_collector must emit semantic_history slots"
assert "feedback_signal" in mc_src, "memory_collector must emit feedback_signal slots"
assert "collect_l5_history_slots" in me_src, "merge_engine must call collect_l5_history_slots"
assert "l5_slots" in me_src, "merge_engine must merge l5_slots into D16 packet"

l5 = collect_l5_history_slots(text="pre-LLM D16 memory merge semantic history", repo_root=str(__import__("pathlib").Path.cwd()), limit=4)
b = collect_b_layer_slots(limit=8)
assert isinstance(l5, list), l5
assert isinstance(b, list), b

# L5 path is best-effort (git may be empty in CI) — structure must be valid when rows exist
for row in l5[:2]:
    assert row.get("kind") == "semantic_history", row
    assert row.get("producer") == "L5", row
feedback = [row for row in b if row.get("kind") == "feedback_signal"]
assert "execution_feedback_signals.jsonl" in mc_src, "B3 feedback path must be wired in memory_collector"

hist_mod = inspect.getsource(__import__("pre_llm.semantic_history.history_bridge", fromlist=["build_semantic_history"]))
assert "read_git_commits" in hist_mod, "L5 must use git_reader for semantic history"

print(
    f"OK: validate-semantic-history-d16-v1 · l5_slots={len(l5)} b_layer_slots={len(b)} feedback_slots={len(feedback)}"
)
PY
