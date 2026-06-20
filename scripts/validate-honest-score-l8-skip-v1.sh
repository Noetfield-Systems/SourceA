#!/usr/bin/env bash
# sa-0077 / sa-0018 / sa-0027 — skip unconditional L8 not_here when hybrid shipped
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
from pathlib import Path

import system_roadmap as sr

_STALE_L8 = (
    "full L8 embeddings later",
    "Embedding index (D5 is token retrieval today)",
    "L8 hybrid scaffold",
)

root = Path(__file__).resolve().parents[1]
embed_path = root / "scripts" / "pre_llm" / "vector_retrieval" / "embedding_provider.py"
index_path = Path.home() / ".sina" / "vector_index_v1.json"
hybrid_shipped = embed_path.is_file() and index_path.is_file()

def assert_no_stale_l8(not_here: list, label: str) -> None:
    for stale in _STALE_L8:
        assert not any(stale in str(line) for line in not_here), (
            f"{label}: stale L8 line {stale!r} in {not_here!r}"
        )

m = sr._build_world_target_map()
nh = (m.get("honest_score") or {}).get("not_here") or []
if hybrid_shipped:
    assert_no_stale_l8(nh, "phase_d complete")

orig_phase_d = sr._phase_d_complete
sr._phase_d_complete = lambda: False
try:
    m_pre = sr._build_world_target_map()
    nh_pre = (m_pre.get("honest_score") or {}).get("not_here") or []
    if hybrid_shipped:
        assert_no_stale_l8(nh_pre, "pre-phase_d")
    else:
        assert any(
            "Embedding index" in str(line) or "full L8 embeddings later" in str(line)
            for line in nh_pre
        ), f"expected L8 gap when hybrid not shipped: {nh_pre!r}"
finally:
    sr._phase_d_complete = orig_phase_d

assert hasattr(sr, "_l8_hybrid_live"), "system_roadmap missing _l8_hybrid_live"
assert sr._l8_hybrid_live() == hybrid_shipped

print(
    f"OK: validate-honest-score-l8-skip-v1 · sa-0077 · hybrid_shipped={hybrid_shipped} · "
    "no unconditional L8 not_here"
)
PY
