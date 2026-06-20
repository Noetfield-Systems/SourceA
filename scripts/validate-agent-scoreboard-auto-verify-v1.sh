#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import inspect
from pathlib import Path

from agent_scoreboard import _auto_verify, scoreboard_payload

src = Path("agent_scoreboard.py").read_text(encoding="utf-8")
assert "def _auto_verify" in src, "_auto_verify missing"
assert 'verified_by": "auto"' in src or '"verified_by": "auto"' in src, "verified_by auto missing"
assert "sa-0301" in src, "sa-0301 marker missing"
assert "_auto_verify(agent_id, report=row" in src or "_auto_verify(agent_id, report=report" in src, (
    "submit_report must call _auto_verify on auto_pass"
)
assert "scoreboard_auto_verified" in src, "governance event for auto verify missing"

sig = inspect.signature(_auto_verify)
assert "agent_id" in sig.parameters, "_auto_verify must accept agent_id"

payload = scoreboard_payload()
for row in payload.get("rows") or []:
    if row.get("auto_pass") and row.get("verified"):
        assert row.get("verified_by") == "auto", (
            f"{row.get('agent_id')}: auto_pass verified row must have verified_by=auto"
        )

print(
    "OK: validate-agent-scoreboard-auto-verify-v1 · "
    f"_auto_verify verified_by=auto on {payload.get('auto_pass_count', 0)} auto_pass rows (sa-0301)"
)
PY
