#!/usr/bin/env bash
# sa-0623 — governance-rules grounding paths agent_rules scripts
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from eval_packet_v1b.grounding import (
    GOVERNANCE_RULES_PATHS,
    build_task_grounding,
    cross_check_governance_rules_grounding,
)

errs = cross_check_governance_rules_grounding()
if errs:
    for e in errs:
        print(f"FAIL: {e}")
    raise SystemExit(1)

g = build_task_grounding(
    task_id="governance-rules",
    prompt="How does rules-in-charge loop load agent_rules scripts at session start?",
    keywords=["rules_in_charge", "agent_rules", "session", "orchestrator"],
)
paths = list(g.get("expected_paths") or [])
assert paths == list(GOVERNANCE_RULES_PATHS), paths

print(
    "OK: validate-eval-packet-v1b-governance-rules-grounding-v1 · "
    "agent_rules_in_charge + agent_rules_loop_orchestrator (sa-0623)"
)
PY
