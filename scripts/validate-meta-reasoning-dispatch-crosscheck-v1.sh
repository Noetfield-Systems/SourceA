#!/usr/bin/env bash
# sa-0610 — META_REASONING_POLICY_STACK vs dispatch Layer-1 classes (orthogonal namespaces)
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
from meta_reasoning_policy import meta_reasoning_payload
from runtime.dispatch_policy.policy_engine import LAW_LAYER1_CLASSES, cross_check_law_policy_classes

mr = meta_reasoning_payload()
xc = mr.get("dispatch_policy_crosscheck") or {}
assert xc.get("ok") is True, xc
assert cross_check_law_policy_classes() == [], cross_check_law_policy_classes()

mr_classes = {x["class"] for x in mr.get("input_classes") or []}
dp_classes = set(LAW_LAYER1_CLASSES)
assert not (mr_classes & dp_classes), f"namespace collision: {mr_classes & dp_classes}"

emap = mr.get("enforcement_map") or []
dispatch_rows = [r for r in emap if "dispatch" in (r.get("enforcement") or "").lower()]
assert dispatch_rows, "enforcement_map missing dispatch_policy link"

print(
    f"OK: validate-meta-reasoning-dispatch-crosscheck-v1 · "
    f"input_classes={len(mr_classes)} dispatch_layer1={len(dp_classes)} alignment_ok=True"
)
PY
