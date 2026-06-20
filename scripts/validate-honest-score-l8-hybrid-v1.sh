#!/usr/bin/env bash
# sa-0043 / sa-0093 / sa-0018 — reject unconditional L8 not_here when hybrid shipped
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

bash validate-honest-score-l8-skip-v1.sh
bash validate-honest-score-not-here-drift-v1.sh

python3 - <<'PY'
from pathlib import Path

import system_roadmap as sr

scripts = Path(__file__).resolve().parent
assert hasattr(sr, "_l8_hybrid_live"), "system_roadmap missing _l8_hybrid_live (sa-0043)"
audit = (scripts / "audit_hub_source_alignment.py").read_text(encoding="utf-8")
assert "_check_honest_score_not_here_regression" in audit, "audit missing L8 regression (sa-0043)"

root = scripts.parent
embed = root / "scripts" / "pre_llm" / "vector_retrieval" / "embedding_provider.py"
index = Path.home() / ".sina" / "vector_index_v1.json"
hybrid = embed.is_file() and index.is_file()
assert sr._l8_hybrid_live() == hybrid, f"_l8_hybrid_live drift (sa-0043)"

stale = (
    "full L8 embeddings later",
    "Embedding index (D5 is token retrieval today)",
    "L8 hybrid scaffold",
)
if hybrid:
    nh = (sr._build_world_target_map().get("honest_score") or {}).get("not_here") or []
    for s in stale:
        assert not any(s in str(line) for line in nh), f"stale L8 not_here {s!r} (sa-0043)"

print(f"OK: validate-honest-score-l8-hybrid-v1 · hybrid_shipped={hybrid} · no unconditional L8 not_here")
PY
