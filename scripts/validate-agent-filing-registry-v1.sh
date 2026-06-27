#!/usr/bin/env bash
# Focused proof for registry-first filing routes. Keep this light on Mac.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 - <<'PY'
from scripts.agent_filing_registry_gate_v1 import resolve
from scripts.agentic_conduct_gate_v1 import evaluate

cases = [
    (
        "SAVE_AND_LOCK site intelligence hub",
        "locked_product_spec_doc",
        "docs/SITE_INTELLIGENCE_HUB_LOCKED_v1.md",
    ),
    (
        "mandatory rule and policy machine enforceable for all agents",
        "agent_rule_policy",
        ".cursor/rules/000-cross-lane-edit-forbidden.mdc",
    ),
    (
        "ASF: apply filing registry unification batch",
        "agent_filing_registry_unification_batch",
        "data/agent-filing-registry-unification-batch-v1.json",
    ),
    (
        "ASF: apply filing registry unification batc",
        "agent_filing_registry_unification_batch",
        "data/agent-filing-registry-unification-batch-v1.json",
    ),
]

for intent, route_id, path_suffix in cases:
    row = resolve(intent=intent, agent="cursor")
    assert row.get("ok"), row
    assert row.get("route_id") == route_id, row
    assert str(row.get("path", "")).endswith(path_suffix), row
    assert row.get("next_steps"), row

polluted_cases = [
    "SAVE_AND_LOCK site intelligence hub. No path named, which path should I use?",
    "I can save and lock site intelligence hub, but no path named, which path should I use?",
]
for intent in polluted_cases:
    row = resolve(intent=intent, agent="cursor")
    assert row.get("ok"), row
    assert row.get("route_id") == "locked_product_spec_doc", row
    assert str(row.get("path", "")).endswith("docs/SITE_INTELLIGENCE_HUB_LOCKED_v1.md"), row
    assert "NO_PATH" not in str(row.get("path", "")), row
    assert "WHICH_PATH" not in str(row.get("path", "")), row

blocked = evaluate(
    role="any",
    task_text="SAVE_AND_LOCK site intelligence hub. No path named, which path should I use?",
)
assert not blocked.get("ok"), blocked
assert any("filing_registry_first_required" in v for v in blocked.get("violations") or []), blocked
assert str(blocked.get("filing_registry", {}).get("path", "")).endswith(
    "docs/SITE_INTELLIGENCE_HUB_LOCKED_v1.md"
), blocked

allowed = evaluate(
    role="any",
    task_text=(
        "SAVE_AND_LOCK site intelligence hub resolved route_id=locked_product_spec_doc "
        "path=docs/SITE_INTELLIGENCE_HUB_LOCKED_v1.md"
    ),
)
assert allowed.get("filing_registry", {}).get("ok"), allowed
print("validate-agent-filing-registry-v1: PASS")
PY
