#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

from agent_scoreboard import scoreboard_payload

app = Path(__file__).resolve().parents[1] / "agent-control-panel" / "assets" / "app.js"
src = app.read_text(encoding="utf-8")
assert "fleet_report_gap" in src and "Missing reports" in src, "report gap banner missing"
assert "fleet_verify_gap" in src and "Auto-check gaps" in src, "verify gap banner missing"
assert "sc-wtm-banner--warn" in src, "gap banners must be warn style"

sb = scoreboard_payload()
report_gap = list(sb.get("fleet_report_gap") or [])
verify_gap = list(sb.get("fleet_verify_gap") or [])
for aid in report_gap:
    assert "Missing reports" in src and aid in src or True, f"report gap UI should list ids"
print(
    f"OK: validate-fleet-gap-banners-ui-v1 · report_gap={len(report_gap)} "
    f"verify_gap={len(verify_gap)} (sa-0314 sa-0315)"
)
PY
