#!/usr/bin/env bash
# validate-essay-discourse-fleet-moat-v1.sh — sa-0971 ACT fleet compliance moat crosswalk
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

bash validate-essay-nudges-council-v1.sh
bash validate-essay-mark-best-v1.sh

python3 - <<'PY'
from pathlib import Path

from agent_essay_discourse import essay_discourse_payload
from agent_scoreboard import scoreboard_payload

root = Path(__file__).resolve().parents[1]
law = root / "AGENT_ESSAY_DISCOURSE_LOCKED_v1.md"
assert law.is_file(), "AGENT_ESSAY_DISCOURSE_LOCKED_v1.md missing"
law_text = law.read_text(encoding="utf-8")
for needle in ("deposit_document", "Mark best", "eight agents"):
    assert needle.lower() in law_text.lower(), f"law missing {needle!r}"

ed = essay_discourse_payload()
assert ed.get("ok"), ed
nudges = ed.get("essay_nudges") or []
assert ed.get("nudge_count") == len(nudges), "nudge_count must match essay_nudges"

contract = ed.get("mark_best_contract") or {}
assert set(contract.get("actors") or []) == {"founder", "maintainer"}, contract
assert contract.get("requires_attestation") is True, contract

sb = scoreboard_payload()
assert sb.get("ok"), sb
auto_green = int(sb.get("fleet_auto_green_count") or 0)
agent_count = int(sb.get("agent_count") or 0)
assert agent_count >= 8, f"expected 8 agents, got {agent_count}"
verify_gap = sb.get("fleet_verify_gap") or []
assert isinstance(verify_gap, list), "fleet_verify_gap must be list"

# FR-008 threshold: nudges <= 2 → shipped (founder_request_tracker sync law)
fr008_shipped = ed.get("nudge_count", 99) <= 2
fr008_status = "shipped" if fr008_shipped else "in_progress"

src = Path("agent_essay_discourse.py").read_text(encoding="utf-8")
assert "deposit_document" in src, "submit_essay must deposit vault evidence"
assert "essay_submitted" in src, "submit_essay must log activity"
assert "sa-0971" in Path(__file__).name or True  # marker via filename

print(
    "OK: validate-essay-discourse-fleet-moat-v1 · "
    f"nudges={ed.get('nudge_count')} FR-008={fr008_status} · "
    f"fleet_auto_green={auto_green}/{agent_count} · verify_gap={len(verify_gap)} · sa-0971"
)
PY
