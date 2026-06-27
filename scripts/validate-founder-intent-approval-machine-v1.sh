#!/usr/bin/env bash
# Validate Founder Intent Approval Machine — schema + canonical intent/critic cases.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== founder intent approval machine ==="

SOURCEA_ROOT="$ROOT" python3 - <<'PY'
import importlib.util
import json
import os
from pathlib import Path

root = Path(os.environ["SOURCEA_ROOT"])
spec_path = root / "data/founder-intent-approval-machine-v1.json"
script_path = root / "scripts/founder_intent_approval_machine_v1.py"

spec = json.loads(spec_path.read_text(encoding="utf-8"))
assert spec["schema"] == "founder-intent-approval-machine-v1", spec.get("schema")
assert len(spec["stages"]) == 9, len(spec["stages"])
assert len(spec["canonical_cases"]) >= 8, len(spec["canonical_cases"])
assert {"APPROVED", "APPROVED_SPEC", "RETURN_TO_AGENT", "FIX_DISK", "FIX_MACHINES", "ASK_FOUNDER"} <= set(spec["verdicts"])

module_spec = importlib.util.spec_from_file_location("fiamm", script_path)
mod = importlib.util.module_from_spec(module_spec)
assert module_spec and module_spec.loader
module_spec.loader.exec_module(mod)

for case in spec["canonical_cases"]:
    row = mod.run_machine(case["message"], surface="validator", write=False)
    assert row["intent_class"] == case["expected_intent"], (case["id"], row["intent_class"])
    for route in case.get("must_route_to", []):
        assert route in row["route"], (case["id"], route, row["route"])
    assert row["verdict"] in {"APPROVED", "APPROVED_SPEC", "ASK_FOUNDER"}, (case["id"], row["verdict"])

literal = mod.run_machine(
    "Brain should be highest confidence.",
    surface="validator",
    candidate_output="You are the highest-confidence public guide for SourceA.",
    write=False,
)
assert literal["verdict"] == "RETURN_TO_AGENT", literal
assert any(f["id"] == "literal_copy" for f in literal["critic_findings"]), literal["critic_findings"]

hardcoded = mod.run_machine(
    "Farsi and Spanish are examples. Brain should translate generally.",
    surface="validator",
    candidate_output="if farsi then return Persian paragraph; if spanish then return Spanish paragraph",
    write=False,
)
assert hardcoded["verdict"] == "RETURN_TO_AGENT", hardcoded
assert any(f["id"] == "hardcoded_example" for f in hardcoded["critic_findings"]), hardcoded["critic_findings"]

ambiguous = mod.run_machine("Make it better.", surface="validator", write=False)
assert ambiguous["intent_class"] == "ambiguous", ambiguous
assert ambiguous["verdict"] == "ASK_FOUNDER", ambiguous

print("OK schema", spec["version"])
print("OK canonical_cases", len(spec["canonical_cases"]))
print("OK blocker_cases literal_copy hardcoded_example")
print("OK ambiguous asks founder")
PY

echo "validate-founder-intent-approval-machine-v1.sh: ALL PASS"
