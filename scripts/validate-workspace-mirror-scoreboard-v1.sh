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
    assert sb.get("no_asf_eval_authority") is True, "mirror must not claim ASF verify authority"
    assert sb.get("verify_authority") == "auto_pass", sb.get("verify_authority")
    print("OK: validate-workspace-mirror-scoreboard-v1 · Worker Hub payload · no ASF verify (sa-0313)")
    raise SystemExit(0)

src = app.read_text(encoding="utf-8")
assert "sa-0313" in src, "sa-0313 marker missing"
assert "auto-green (machine)" in src, "mirror must use auto-green machine copy"
assert "ASF verify" not in src[src.index("scoreboardBlock"):src.index("scoreboardBlock") + 400], (
    "mirror scoreboard block must not say ASF verify"
)
print("OK: validate-workspace-mirror-scoreboard-v1 · no ASF verified copy (sa-0313)")
PY
