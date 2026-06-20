#!/usr/bin/env bash
# sa-0620 / sa-0645 — OpenRouter/cloud embeddings deferred to phase-s9-research-models (doc-only)
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
import json
from pathlib import Path

wtm = Path("brain-os/wtm/SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md").read_text(encoding="utf-8")
registry = json.loads(Path("brain-os/plan-registry/sourcea-1000/REGISTRY.json").read_text(encoding="utf-8"))
phases = {p.get("id") for p in (registry.get("phases") or [])}

assert "phase-s9-research-models" in phases, "REGISTRY must define phase-s9-research-models"
assert "sa-0620" in wtm or "Embedding API deferral" in wtm, wtm
assert "phase-s9-research-models" in wtm, "WTM must cite phase-s9-research-models deferral"
assert "phase-s6-wtm-pre-llm" in wtm, "WTM must scope deferral away from phase-s6"
assert Path("scripts/pre_llm/vector_retrieval/embedding_provider.py").is_file()

print("OK: validate-openrouter-embeddings-deferred-s9-v1 · deferral doc present")
PY
