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
    rows = sb.get("rows") or []
    assert rows, "scoreboard rows missing"
    assert sb.get("verify_authority") == "auto_pass", sb.get("verify_authority")
    assert sb.get("no_asf_eval_authority") is True, "scoreboard must not claim ASF verify"
    for row in rows:
        if row.get("auto_pass"):
            assert row.get("auto_green") is True, row.get("agent_id")
    print(
        "OK: validate-scoreboard-auto-green-pill-v1 · Worker Hub payload · "
        f"auto_green={sb.get('fleet_auto_green_count')}/{sb.get('agent_count')} (sa-0306 · sa-0356)"
    )
    raise SystemExit(0)

src = app.read_text(encoding="utf-8")
assert "function renderScoreboardVerifyCell" in src, "renderScoreboardVerifyCell missing"
assert "sa-0306" in src, "sa-0306 marker missing"
assert "sa-0356" in src, "sa-0356 marker missing"
assert "renderScoreboardVerifyCell(r)" in src, "table must use renderScoreboardVerifyCell"

fn_start = src.index("function renderScoreboardVerifyCell")
fn_end = src.index("function renderAgentScoreboard", fn_start)
fn = src[fn_start:fn_end]
assert "if (r.auto_pass)" in fn, "auto_pass branch missing"
pill_idx = fn.index("sc-sb-auto-pill")
force_idx = fn.find("sc-sb-verify-force")
assert force_idx == -1 or pill_idx < force_idx, "auto_pass pill must come before any Force button in helper"
assert "sc-sb-verify\"" not in fn and "sc-sb-verify " not in fn, "public Verify button removed from helper"

assert ".sc-sb-verify\"" not in src and ".sc-sb-verify " not in src, (
    "public Verify button binding removed"
)

print("OK: validate-scoreboard-auto-green-pill-v1 · auto_pass pill replaces Verify/Force (sa-0306 · sa-0356)")
PY
