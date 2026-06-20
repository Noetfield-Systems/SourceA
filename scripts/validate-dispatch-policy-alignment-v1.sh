#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

from runtime.dispatch_policy.allowlist import TASK_CLASS_REGISTRY, infer_task_class
from runtime.dispatch_policy.classifier import classify_action
from runtime.dispatch_policy.policy_engine import dispatch_policy_payload

SOURCE_A = Path.cwd().parent
locked_path = SOURCE_A / "brain-os" / "law" / "DISPATCH_POLICY_LOCKED_v1.md"
if not locked_path.is_file():
    locked_path = SOURCE_A / "DISPATCH_POLICY_LOCKED_v1.md"
locked = locked_path.read_text(encoding="utf-8")
assert "Phase 2a" in locked, "DISPATCH_POLICY_LOCKED_v1.md missing Phase 2a"
assert "task-class registry" in locked.lower() or "Task-class registry" in locked, locked[:200]
assert "classifier" in locked.lower(), locked[:200]
assert "SAFE_AUTO" in locked, locked[:200]

assert classify_action("pos-dispatch") == "suggest", classify_action("pos-dispatch")
assert classify_action("spine-smoke-echo") == "auto_low_risk", classify_action("spine-smoke-echo")

task = infer_task_class("spine-smoke-echo")
assert task == "validate-only", task
assert TASK_CLASS_REGISTRY.get(task) == "SAFE_AUTO", TASK_CLASS_REGISTRY.get(task)

payload = dispatch_policy_payload()
alignment = payload.get("alignment") or {}
assert alignment.get("mapping_ok") is True, alignment
assert alignment.get("task_class_registry_version") == "v1", alignment
assert alignment.get("classifier_classes"), alignment
print("OK: validate-dispatch-policy-alignment-v1 · mapping_ok=True")
PY
