#!/usr/bin/env bash
# sa-0033 / sa-0083 — MAP_POINTER_DOCS must reference WORLD_TARGET_MODEL_MAP_LOCKED_v5.md only
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import audit_hub_source_alignment as audit

root = audit.SOURCE_A
v5_name = audit.MAP_DOC.split("/")[-1]
assert v5_name == "WORLD_TARGET_MODEL_MAP_LOCKED_v5.md", audit.MAP_DOC
stale_maps = (
    "WORLD_TARGET_MODEL_MAP_LOCKED_v1.md",
    "WORLD_TARGET_MODEL_MAP_LOCKED_v2.md",
    "WORLD_TARGET_MODEL_MAP_LOCKED_v3.md",
    "WORLD_TARGET_MODEL_MAP_LOCKED_v4.md",
)

errors: list[str] = []
for rel in audit.MAP_POINTER_DOCS:
    path = root / rel
    if not path.is_file():
        errors.append(f"missing MAP_POINTER doc: {rel}")
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    if audit.MAP_DOC not in text and v5_name not in text:
        errors.append(f"{rel} missing {audit.MAP_DOC}")
    for stale in stale_maps:
        if stale in text:
            errors.append(f"{rel} stale map reference {stale}")

assert not errors, errors
print(
    f"OK: validate-map-pointer-docs-v1 · {len(audit.MAP_POINTER_DOCS)} docs · "
    f"v5-only · {audit.MAP_DOC}"
)
PY
