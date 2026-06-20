#!/usr/bin/env bash
# sa-0038 / sa-0088 / sa-0013 — sidebar NAV_TABS must match app.js NAV ids
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 audit_essentials_nav.py

python3 - <<'PY'
import audit_hub_source_alignment as audit
from hub_essentials_index import NAV_TABS

errors: list[str] = []
audit._check_essentials_nav_regression(errors)
assert not errors, errors
assert len(NAV_TABS) >= 42, f"expected >=42 NAV_TABS, got {len(NAV_TABS)}"

print(
    f"OK: validate-essentials-nav-sync-v1 · "
    f"{len(NAV_TABS)} sidebar tabs · audit regression clean"
)
PY
