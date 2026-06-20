#!/usr/bin/env bash
# sa-0139 — l8-hybrid grounding cites embedding_provider.py + query_engine
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from eval_packet_v1b.grounding import (
    L8_EMBEDDING_PROVIDER_PY,
    L8_HYBRID_PATHS,
    build_task_grounding,
    cross_check_l8_hybrid_grounding,
)

errs = cross_check_l8_hybrid_grounding()
if errs:
    for e in errs:
        print(f"FAIL: {e}")
    raise SystemExit(1)

g = build_task_grounding(
    task_id="l8-hybrid",
    prompt="How does L8 hybrid embedding retrieval extend D5 token index?",
    keywords=["embedding", "vector", "hybrid", "retrieval"],
)
paths = list(g.get("expected_paths") or [])
assert paths == list(L8_HYBRID_PATHS), paths
assert L8_EMBEDDING_PROVIDER_PY in paths, paths

print(
    "OK: validate-eval-packet-v1b-l8-hybrid-grounding-v1 · "
    "embedding_provider.py + query_engine (sa-0139)"
)
PY
