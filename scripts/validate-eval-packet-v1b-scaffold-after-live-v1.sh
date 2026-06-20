#!/usr/bin/env bash
# sa-0140 — scaffold arm after live pass (validate-eval-packet-v1b.sh chain)
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from eval_report_capture import cross_check_scaffold_survives_after_live

errs = cross_check_scaffold_survives_after_live()
if errs:
    for e in errs:
        print(f"FAIL: {e}")
    raise SystemExit(1)

print(
    "OK: validate-eval-packet-v1b-scaffold-after-live-v1 · "
    "scaffold survives after live pass (sa-0140)"
)
PY
