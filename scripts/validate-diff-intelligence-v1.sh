#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import inspect

from pre_llm.diff_intelligence.api import diff_intelligence_v1_payload
from pre_llm.diff_intelligence.diff_engine import run_diff_intelligence
from pre_llm.diff_intelligence.store import DIFF_SSOT_PATH, SCHEMA

import pre_llm.diff_intelligence.diff_engine as de
src = inspect.getsource(de)
for forbidden in ("openai", "openrouter", "anthropic", "requests.post"):
    assert forbidden not in src.lower(), f"forbidden in D13: {forbidden}"

QUERY = "ship D13 diff intelligence semantic change impact git dependency pre-LLM"
live = run_diff_intelligence(text=QUERY, task_id="validate-d13", force_refresh=True)
assert live.get("ok"), live
assert live.get("schema") == SCHEMA
assert DIFF_SSOT_PATH.is_file(), "diff_intelligence_v1.json missing"
assert live.get("diff_ready"), live
assert live.get("change_count", 0) >= 1, live

changes = live.get("changes") or []
assert changes, "expected at least one change"
assert all(c.get("path") and c.get("kind") for c in changes)
assert all((c.get("impact") or {}).get("severity") in ("none", "low", "medium", "high") for c in changes)

impact = live.get("impact_map") or {}
assert impact.get("files_changed", 0) >= 1

api = diff_intelligence_v1_payload(text=QUERY, task_id="validate-d13-api")
assert api.get("ok"), api
pd = api.get("packet_diff") or {}
assert len(pd.get("changes") or []) >= 1
assert pd.get("producer") == "D13"
assert pd.get("diff_ready") is True

print(
    "PASS diff intelligence v1",
    "changes",
    live.get("change_count"),
    "high_impact",
    len(impact.get("high_impact_paths") or []),
    "scope",
    live.get("git_scope"),
)
PY
