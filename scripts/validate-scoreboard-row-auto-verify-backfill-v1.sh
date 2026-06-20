#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

from agent_scoreboard import _maybe_backfill_auto_verify, scoreboard_payload
from agent_workspace_registry import AGENT_WORKSPACES

src = Path("agent_scoreboard.py").read_text(encoding="utf-8")
assert "def _maybe_backfill_auto_verify" in src, "_maybe_backfill_auto_verify missing"
assert "sa-0303" in src, "sa-0303 marker missing"
assert "_maybe_backfill_auto_verify(aid" in src, "scoreboard_row must call backfill helper"

payload = scoreboard_payload()
gaps = []
for spec in AGENT_WORKSPACES:
    row = next((r for r in payload.get("rows") or [] if r.get("agent_id") == spec["id"]), None)
    if not row:
        continue
    if row.get("auto_pass") and row.get("has_report"):
        if not row.get("verified"):
            gaps.append(f"{spec['id']}: auto_pass+report but not verified")
        elif row.get("verified_by") != "auto":
            gaps.append(f"{spec['id']}: verified_by={row.get('verified_by')!r} expected auto")

assert not gaps, "scoreboard_row backfill gaps: " + "; ".join(gaps)
print(
    "OK: validate-scoreboard-row-auto-verify-backfill-v1 · "
    f"{payload.get('auto_pass_count', 0)} rows backfilled verified_by=auto (sa-0303)"
)
PY
