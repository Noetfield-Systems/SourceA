#!/usr/bin/env bash
# sa-0614 — D9 blend weights doc vs query_engine / ranker implementation
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
import inspect
import re
from pathlib import Path

ROOT = Path.cwd()
ranker_src = inspect.getsource(__import__("pre_llm.context_ranking.ranker", fromlist=["rank_evidence"]))
hybrid_src = inspect.getsource(__import__("pre_llm.vector_retrieval.embedding_provider", fromlist=["hybrid_score"]))
qe_src = (ROOT / "scripts/pre_llm/vector_retrieval/query_engine.py").read_text(encoding="utf-8")

# D9 context-ranking blend (ranker.py)
d9 = {
    "intent": 0.26,
    "overlap": 0.22,
    "retrieval": 0.28,
    "graph": 0.12,
    "hybrid_sem": 0.12,
}
for w in d9.values():
    assert f"{w}" in ranker_src or f"{w:.2f}" in ranker_src, f"D9 weight {w} missing from ranker.py"
assert abs(sum(d9.values()) - 1.0) < 0.001, d9

# D5 hybrid path used by query_engine → embedding_provider.hybrid_score
assert "hybrid_score" in qe_src, "query_engine must call hybrid_score for hybrid mode"
m = re.search(r"0\.55\s*\*\s*token_score\s*\+\s*0\.45\s*\*\s*sem", hybrid_src)
assert m, "embedding_provider hybrid_score must use 0.55 token + 0.45 semantic"

# WTM synthesis doc mentions D9 blend (inform-only cross-ref)
syn = (ROOT / "brain-os/wtm/SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md").read_text(encoding="utf-8")
assert "D9 blend" in syn, "synthesis doc must mention D9 blend"

print(
    "OK: validate-d9-blend-weights-v1 · D9="
    + "/".join(str(v) for v in d9.values())
    + " D5_hybrid=0.55/0.45"
)
PY
