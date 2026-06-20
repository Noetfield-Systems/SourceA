#!/usr/bin/env bash
# sa-0213 sa-0309 sa-0359 governance-fleet nudges + verify_gap SSOT
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

from agent_essay_discourse import essay_discourse_payload
from agent_scoreboard import scoreboard_payload

essays = essay_discourse_payload()
assert essays.get("ok"), essays
nudges = essays.get("essay_nudges")
assert isinstance(nudges, list), "essay_nudges must be list"
assert "essay_nudges" in essays, "essay nudge list required"
assert essays.get("nudge_count") == len(nudges), "nudge_count must match essay_nudges length"

sb = scoreboard_payload()
assert sb.get("ok"), sb
verify_gap = sb.get("fleet_verify_gap")
report_gap = sb.get("fleet_report_gap")
assert isinstance(verify_gap, list), "fleet_verify_gap must be list"
assert isinstance(report_gap, list), "fleet_report_gap must be list"
assert "fleet_verify_gap" in sb, sb
assert "fleet_report_gap" in sb, sb

rows = sb.get("rows") or []
expected_verify = [r["agent_id"] for r in rows if r.get("has_report") and not r.get("auto_pass")]
expected_report = [r["agent_id"] for r in rows if not r.get("has_report")]
assert sorted(verify_gap) == sorted(expected_verify), (
    f"fleet_verify_gap SSOT drift: {verify_gap!r} vs {expected_verify!r}"
)
assert sorted(report_gap) == sorted(expected_report), (
    f"fleet_report_gap SSOT drift: {report_gap!r} vs {expected_report!r}"
)

trust = Path(__file__).resolve().parents[1] / "TRUST_LEDGER_SCHEMA_LOCKED_v1.md"
assert trust.is_file(), "TRUST_LEDGER_SCHEMA_LOCKED_v1.md missing"

# Monolith index.html retired — H1 Worker Hub uses API fetch (no command-data lazy blob)
idx = Path(__file__).resolve().parents[1] / "agent-control-panel" / "worker-hub" / "index.html"
html = idx.read_text(encoding="utf-8")
assert "fetchPayload" in html, "worker-hub API fetch regression"
assert "command-data.json" not in html, "H1 must not prefetch command-data.json"

print(
    "OK: validate-governance-fleet-v1 · nudges",
    essays.get("nudge_count"),
    "verify_gap",
    len(verify_gap),
    "· SSOT sa-0359",
)
PY
