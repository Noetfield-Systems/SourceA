#!/usr/bin/env bash
# verify:wire — assert run receipt artifacts exist (fail when missing; no auto-build)
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import sys

from runreceipt.pack_v1 import assert_runreceipt_artifacts

out = assert_runreceipt_artifacts()
if not out.get("ok"):
    detail = out.get("missing") or out.get("error") or out
    print("FAIL: verify:wire missing run receipt artifact:", detail)
    sys.exit(1)

run_id = out.get("run_id") or "unknown"
print(f"OK: validate-verify-wire-v1 · {run_id}")
PY
