#!/usr/bin/env bash
# validate-agent-scoreboard-auto-green-header-v1.sh — sa-0855 / sa-0805 scoreboard Auto green thead
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

bash validate-scoreboard-auto-green-pill-v1.sh

python3 - <<'PY'
from pathlib import Path

from agent_scoreboard import scoreboard_payload
from hub_worker_mode_v1 import worker_hub_mode

root = Path(__file__).resolve().parents[1]
app = root / "agent-control-panel" / "assets" / "app.js"

if worker_hub_mode() or not app.is_file():
    sb = scoreboard_payload()
    assert sb.get("tagline"), "scoreboard tagline missing"
    assert sb.get("verify_authority") == "auto_pass", sb.get("verify_authority")
    green_n = sb.get("fleet_auto_green_count", 0)
    agent_n = sb.get("agent_count", 0)
    print(
        f"OK: validate-agent-scoreboard-auto-green-header-v1 · "
        f"Worker Hub payload · fleet_auto_green={green_n}/{agent_n} (sa-0855)"
    )
    raise SystemExit(0)

src = app.read_text(encoding="utf-8")

assert "function renderAgentScoreboard" in src, "renderAgentScoreboard missing"
assert "sa-0305" in src, "sa-0305 marker missing"

sb_start = src.index("function renderAgentScoreboard")
sb_end = src.index("function bindAgentScoreboard", sb_start)
sb_block = src[sb_start:sb_end]

assert "sc-sb-table" in sb_block, "scoreboard table class missing"
assert "<thead>" in sb_block, "scoreboard thead missing"
assert 'class="sc-sb-th-verify">Auto green</th>' in sb_block, (
    "thead must use sc-sb-th-verify with Auto green label (sa-0855)"
)
assert "sc-sb-col-verify" in sb_block, "tbody must use sc-sb-col-verify column (sa-0855)"
assert "renderScoreboardVerifyCell" in sb_block, "verify cell helper must be used in table"

assert "Verify ✓" not in sb_block, "stale Verify ✓ header copy in renderAgentScoreboard"
thead_start = sb_block.index("<thead>")
thead_end = sb_block.index("</thead>", thead_start) + len("</thead>")
thead_block = sb_block[thead_start:thead_end]
assert "ASF verify" not in thead_block, "thead must not promote ASF verify (sa-0855)"

sb = scoreboard_payload()
green_n = sb.get("fleet_auto_green_count", 0)
agent_n = sb.get("agent_count", 0)
print(
    f"OK: validate-agent-scoreboard-auto-green-header-v1 · "
    f"Auto green thead wired · fleet_auto_green={green_n}/{agent_n} (sa-0855)"
)
PY
