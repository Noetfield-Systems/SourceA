#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

from agent_scoreboard import FLEET_AUTO_GREEN_COUNT_KEY, scoreboard_payload

src = Path("agent_scoreboard.py").read_text(encoding="utf-8")
assert FLEET_AUTO_GREEN_COUNT_KEY in src, "fleet_auto_green_count missing from agent_scoreboard.py"
assert "sa-0302" in src, "sa-0302 marker missing"
assert "sa-0352" in src, "sa-0352 marker missing"

sb = scoreboard_payload()
assert sb.get("ok"), sb
count = sb.get(FLEET_AUTO_GREEN_COUNT_KEY)
assert count is not None, "fleet_auto_green_count not exposed in scoreboard_payload"
assert isinstance(count, int), f"fleet_auto_green_count must be int, got {type(count)}"
row_green = sum(1 for r in sb.get("rows") or [] if r.get("auto_green"))
assert count == row_green, f"fleet_auto_green_count={count} != row auto_green sum={row_green}"
assert count == sb.get("auto_pass_count"), "fleet_auto_green_count must match auto_pass_count"

cmd = Path(__file__).resolve().parents[1] / "agent-control-panel" / "command-data.json"
if cmd.is_file():
    hub_sb = (json.loads(cmd.read_text(encoding="utf-8")).get("agent_scoreboard") or {})
    hub_count = hub_sb.get("fleet_auto_green_count")
    assert hub_count == count, f"command-data drift: {hub_count} != live {count}"

print(f"OK: validate-fleet-auto-green-count-v1 · fleet_auto_green_count={count} (sa-0302, sa-0352)")
PY
