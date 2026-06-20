#!/usr/bin/env bash
# sa-0041 / sa-0091 / sa-0016 — index.html lazy bootstrap + shell payload under 500KB
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import json
from pathlib import Path

from hub_worker_mode_v1 import worker_hub_mode
from sina_command_lib import HEAVY_PAYLOAD_KEYS, SHELL_MAX_BYTES

root = Path(__file__).resolve().parents[1]
shell = root / "agent-control-panel" / "command-data-shell.json"
assert shell.is_file(), "command-data-shell.json missing (sa-0041)"
size = shell.stat().st_size
assert size <= SHELL_MAX_BYTES, f"shell {size} bytes > {SHELL_MAX_BYTES} (sa-0041)"
data = json.loads(shell.read_text(encoding="utf-8"))
for key in HEAVY_PAYLOAD_KEYS:
    assert key not in data, f"heavy key {key} leaked into shell (sa-0041)"

if worker_hub_mode():
    boot = root / "agent-control-panel" / "worker-hub" / "boot.json"
    assert boot.is_file(), "worker-hub/boot.json missing in H1 mode (sa-0041)"
    print(
        f"OK: validate-command-data-lazy-shell-v1 · H1 worker-hub shell {size} bytes ≤ {SHELL_MAX_BYTES}"
    )
else:
    index = root / "agent-control-panel" / "index.html"
    ih = index.read_text(encoding="utf-8")
    assert "__COMMAND_DATA_LAZY" in ih, "index.html missing __COMMAND_DATA_LAZY (sa-0041)"
    assert "window.COMMAND_DATA = {" not in ih, "index.html embeds full COMMAND_DATA (sa-0041)"
    assert "fleet" in HEAVY_PAYLOAD_KEYS, "fleet must be deferred from shell (sa-0041)"
    print(f"OK: validate-command-data-lazy-shell-v1 · __COMMAND_DATA_LAZY + shell {size} bytes ≤ {SHELL_MAX_BYTES}")
PY
