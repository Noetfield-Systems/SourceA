#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from sina_command_lib import verify_command_data_atomic

ok, detail = verify_command_data_atomic()
assert ok, detail
print(f"OK: validate-command-data-atomic-v1 · {detail}")
PY
