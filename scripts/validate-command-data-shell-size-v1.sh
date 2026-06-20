#!/usr/bin/env bash
# validate-command-data-shell-size-v1.sh — sa-0802 / sa-0852 / sa-0877 shell size measure + 500KB cap
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import json
from pathlib import Path

from sina_command_lib import SHELL_MAX_BYTES

root = Path(__file__).resolve().parents[1]
shell = root / "agent-control-panel" / "command-data-shell.json"
assert shell.is_file(), "command-data-shell.json missing (sa-0852)"
size = shell.stat().st_size
kb = round(size / 1024, 1)
headroom = SHELL_MAX_BYTES - size
assert size <= SHELL_MAX_BYTES, f"shell {size} bytes ({kb} KB) > cap {SHELL_MAX_BYTES} (sa-0852)"
data = json.loads(shell.read_text(encoding="utf-8"))
built_at = data.get("built_at") or "unknown"
print(
    f"OK: validate-command-data-shell-size-v1 · {size} bytes ({kb} KB) ≤ {SHELL_MAX_BYTES} "
    f"· headroom {headroom} B · built_at {built_at[:19]} (sa-0852)"
)
PY
