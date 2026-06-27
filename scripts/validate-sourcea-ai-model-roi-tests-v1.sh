#!/usr/bin/env bash
# Validate SourceA model ROI matrix, evals, runner dry-run, and router policy.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== sourcea ai model roi tests ==="

SOURCEA_ROOT="$ROOT" python3 - <<'PY'
import importlib.util
import json
import os
from pathlib import Path

root = Path(os.environ["SOURCEA_ROOT"])
matrix_path = root / "data/sourcea-ai-model-roi-test-matrix-v1.json"
eval_path = root / "data/sourcea-ai-model-roi-eval-cases-v1.json"
policy_path = root / "data/sourcea-ai-model-router-policy-v1.json"
runner_path = root / "scripts/sourcea_ai_model_roi_test_runner_v1.py"
model_dispatch_path = root / "scripts/model_dispatch.py"

matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
evals = json.loads(eval_path.read_text(encoding="utf-8"))
policy = json.loads(policy_path.read_text(encoding="utf-8"))

assert matrix["schema"] == "sourcea-ai-model-roi-test-matrix-v1"
assert evals["schema"] == "sourcea-ai-model-roi-eval-cases-v1"
assert policy["schema"] == "sourcea-ai-model-router-policy-v1"
models = matrix["models"]
assert len(models) >= 16, len(models)

surfaces = {"brain_chat", "forge_terminal", "chat_unify"}
coverage = {s: 0 for s in surfaces}
ids = set()
for model in models:
    mid = model["id"]
    assert mid not in ids, mid
    ids.add(mid)
    assert model.get("provider"), mid
    assert model.get("api_model"), mid
    assert model.get("cost_band"), mid
    assert model.get("roles"), mid
    for surface in model.get("surfaces") or []:
        assert surface in surfaces, (mid, surface)
        coverage[surface] += 1

for surface, minimum in matrix["minimum_surface_coverage"].items():
    assert coverage[surface] >= minimum, (surface, coverage[surface], minimum)

for future in matrix["future_candidates"]:
    assert future["status"] == "candidate_future", future
    assert future.get("api_model") is None, future

required = set(evals["required_buckets"])
present = {case["bucket"] for case in evals["cases"]}
assert required <= present, sorted(required - present)
assert len(evals["cases"]) >= 12, len(evals["cases"])
assert any(case.get("must_preserve_model_lock") for case in evals["cases"])

module_spec = importlib.util.spec_from_file_location("model_roi_runner", runner_path)
runner = importlib.util.module_from_spec(module_spec)
assert module_spec and module_spec.loader
module_spec.loader.exec_module(runner)
receipt = runner.run(live=False, surface="chat_unify", limit_models=2, limit_cases=3)
assert receipt["schema"] == "sourcea-ai-model-roi-test-receipt-v1"
assert receipt["live"] is False
assert receipt["model_count"] == 2
assert Path(receipt["receipt_path"]).is_file()
for row in receipt["results"]:
    assert row["approval_status"] == "CANDIDATE_ONLY"
    for case in row["cases"]:
        assert case["status"] == "NOT_EXECUTED"

dispatch_spec = importlib.util.spec_from_file_location("model_dispatch", model_dispatch_path)
dispatch = importlib.util.module_from_spec(dispatch_spec)
assert dispatch_spec and dispatch_spec.loader
dispatch_spec.loader.exec_module(dispatch)
locked = dispatch.resolve_sourcea_model(product="chat_unify", role="bulk", explicit_model="gpt-4o", preserve_explicit=True, keys={})
assert locked["model_id"] == "gpt-4o", locked
assert locked["source"] == "explicit_lock", locked
auto = dispatch.resolve_sourcea_model(product="chat_unify", role="check", preserve_explicit=True, keys={})
assert auto["source"] == "roi_policy", auto
assert auto["model_id"], auto

print("OK models", len(models))
print("OK eval_cases", len(evals["cases"]))
print("OK coverage", coverage)
print("OK dry_run_receipt", receipt["receipt_path"])
print("OK router_policy", locked["model_id"], auto["model_id"])
PY

echo "validate-sourcea-ai-model-roi-tests-v1.sh: ALL PASS"
