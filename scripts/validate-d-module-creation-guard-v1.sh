#!/usr/bin/env bash
# sa-0615 — reject new pre_llm D-module dirs unless plan authorizes (frozen D1–D16 allowlist)
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
from pathlib import Path

ROOT = Path.cwd()
PRE_LLM = ROOT / "scripts" / "pre_llm"

# Frozen at phase_d_complete — no new D-modules without plan + ASF (SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2)
AUTHORIZED = frozenset({
    "code_intelligence",      # D1
    "graph_fusion",           # D2
    "dependency_graph",       # D3
    "intent_engine",          # D4
    "vector_retrieval",       # D5
    "memory_git_bridge",      # D6
    "query_expansion",        # D7
    "graph_reasoning",        # D8
    "context_ranking",        # D9
    "planning_engine",        # D10
    "tool_router",            # D11
    "validation_layer",       # D12
    "diff_intelligence",      # D13
    "context_compression",    # D14
    "context_assembly",       # D15
    "packet_memory_merge",    # D16
    "context_packet",         # schema spine
    "packet_readiness",       # D15.2
    "user_signals",           # L0 bridge
    "semantic_history",       # history bridge
})

on_disk = {
    p.name
    for p in PRE_LLM.iterdir()
    if p.is_dir() and not p.name.startswith("__")
}
extra = sorted(on_disk - AUTHORIZED)
missing = sorted(AUTHORIZED - on_disk)
assert not extra, f"unauthorized pre_llm modules: {extra}"
assert not missing, f"authorized module missing locally: {missing}"

syn = (ROOT / "brain-os/wtm/SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md").read_text(encoding="utf-8")
assert "D1–D16" in syn or "D1-D16" in syn, "synthesis must document D1-D16 stack"

print(f"OK: validate-d-module-creation-guard-v1 · modules={len(on_disk)} authorized={len(AUTHORIZED)}")
PY
