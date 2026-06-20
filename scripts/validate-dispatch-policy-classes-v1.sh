#!/usr/bin/env bash
# Cross-check DISPATCH_POLICY_LOCKED_v1.md Layer-1 classes vs policy_engine._build_classes (sa-0158).
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from runtime.dispatch_policy.policy_engine import (
    LAW_LAYER1_CLASSES,
    cross_check_law_policy_classes,
    dispatch_policy_payload,
)

errs = cross_check_law_policy_classes()
if errs:
    for e in errs:
        print(f"FAIL: {e}")
    raise SystemExit(1)

payload = dispatch_policy_payload()
alignment = payload.get("alignment") or {}
assert alignment.get("law_classes_ok") is True, alignment
assert alignment.get("mapping_ok") is True, alignment
classes = payload.get("classes") or []
assert len(classes) == len(LAW_LAYER1_CLASSES), classes
assert payload.get("doc_path") == "brain-os/law/DISPATCH_POLICY_LOCKED_v1.md", payload.get("doc_path")

print(
    f"OK: validate-dispatch-policy-classes-v1 · "
    f"law_classes_ok=True · {len(classes)} classes · mapping_ok=True"
)
PY
