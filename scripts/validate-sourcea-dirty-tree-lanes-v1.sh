#!/usr/bin/env bash
# Validate dirty tree lane ownership map and classifier.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== sourcea dirty tree lanes ==="

SOURCEA_ROOT="$ROOT" python3 - <<'PY'
import importlib.util
import json
import os
from pathlib import Path

root = Path(os.environ["SOURCEA_ROOT"])
map_path = root / "data/sourcea-dirty-tree-lane-map-v1.json"
artifact_policy_path = root / "data/sourcea-generated-artifact-review-policy-v1.json"
script_path = root / "scripts/sourcea_dirty_tree_lane_map_v1.py"
doc_path = root / "docs/SOURCEA_DIRTY_TREE_LANE_OWNERSHIP_LOCKED_v1.md"
rule_path = root / ".cursor/rules/048-dirty-tree-lane-ownership-v1.mdc"

lane_map = json.loads(map_path.read_text(encoding="utf-8"))
artifact_policy = json.loads(artifact_policy_path.read_text(encoding="utf-8"))
assert lane_map["schema"] == "sourcea-dirty-tree-lane-map-v1"
assert artifact_policy["schema"] == "sourcea-generated-artifact-review-policy-v1"
assert str(lane_map["report"]).startswith("~/.sina/")
assert doc_path.is_file()
assert rule_path.is_file()
lanes = lane_map["lanes"]
ids = {lane["id"] for lane in lanes}
required = {
    "brain_chat_runtime",
    "generated_brain_corpus",
    "chat_unify",
    "model_roi",
    "intent_approval_machine",
    "supabase_db",
    "incidents_rules",
    "docs_plan_registry",
    "site_assets",
    "other_control",
}
assert required <= ids, sorted(required - ids)
for lane in lanes:
    assert lane.get("owner"), lane
    assert lane.get("globs"), lane

spec = importlib.util.spec_from_file_location("lane_map", script_path)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

checks = {
    "scripts/model_dispatch.py": "model_roi",
    "data/sourcea-ai-model-roi-test-matrix-v1.json": "model_roi",
    "data/chatbot-knowledge/brain_knowledge_v1.sqlite": "generated_brain_corpus",
    "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json": "generated_brain_corpus",
    "cloud/workers/sourcea-brain-chat-v1/src/index.js": "brain_chat_runtime",
    "scripts/chat_unify_smart_router_v1.py": "chat_unify",
    "docs/FOUNDER_INTENT_APPROVAL_MACHINE_LOCKED_v1.md": "intent_approval_machine",
    "infra/supabase/portfolio-spine/migrations/004_sourcea_plan_registry_v1.sql": "supabase_db",
    "scripts/sourcea_supabase_plan_registry_import_v1.py": "supabase_db",
    "docs/SOURCEA_SUPABASE_CONNECTION_BLOCKER_LOCKED_v1.md": "supabase_db",
    "data/sourcea-generated-artifact-review-policy-v1.json": "other_control",
    ".cursor/rules/048-dirty-tree-lane-ownership-v1.mdc": "incidents_rules",
}
for path, expected in checks.items():
    got = mod.classify_path(path)["lane"]
    assert got == expected, (path, got, expected)

corpus = mod.classify_path("data/chatbot-knowledge/brain_knowledge_v1.sqlite")
assert corpus["freeze_default"] is True, corpus
report = mod.build_report()
assert report["schema"] == "sourcea-dirty-tree-lane-report-v1"
assert report["dirty_count"] >= 0

print("OK lanes", len(lanes))
print("OK classified_paths", len(checks))
print("OK dirty_count", report["dirty_count"])
PY

echo "validate-sourcea-dirty-tree-lanes-v1.sh: ALL PASS"
