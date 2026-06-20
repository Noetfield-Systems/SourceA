#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

from agent_scoreboard import scoreboard_payload
from hub_worker_mode_v1 import worker_hub_mode

root = Path(__file__).resolve().parents[1]
app = root / "agent-control-panel" / "assets" / "app.js"

if worker_hub_mode() or not app.is_file():
    sb = scoreboard_payload()
    assert sb.get("tagline"), "scoreboard tagline missing"
    assert "fleet_auto_green_count" in sb, "fleet_auto_green_count missing from payload"
    assert "fleet_report_gap" in sb and "fleet_verify_gap" in sb, "gap lists missing from payload"
    assert sb.get("no_asf_eval_authority") is True, "scoreboard must not claim ASF verify authority"
    assert sb.get("verify_authority") == "auto_pass", sb.get("verify_authority")
    print(
        "OK: validate-render-agent-scoreboard-v1 · Worker Hub payload SSOT · "
        f"fleet_auto_green={sb.get('fleet_auto_green_count')}/{sb.get('agent_count')} (sa-0305)"
    )
    raise SystemExit(0)

src = app.read_text(encoding="utf-8")
assert "function renderAgentScoreboard" in src, "renderAgentScoreboard missing"
assert "sa-0305" in src, "sa-0305 marker missing"
assert "sb.tagline" in src, "hero must use sb.tagline"
assert "fleet_auto_green_count" in src, "fleet_auto_green_count in hero meta"
assert "fleet_report_gap" in src and "fleet_verify_gap" in src, "gap banners required"
assert "sc-wtm-banner--warn" in src and "Auto-check gaps" in src, "verify gap warn banner required"
assert "Fleet auto-green" in src, "fleet full green banner required"
assert "ASF verify ✓" not in src or "not ASF verify" in src, "sidebar must not promote ASF verify"
assert "auto-checks green" in src, "sidebar auto-checks green copy required"
print("OK: validate-render-agent-scoreboard-v1 · renderAgentScoreboard hero + gap banners (sa-0305)")
PY
