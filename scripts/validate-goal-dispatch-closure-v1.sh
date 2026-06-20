#!/usr/bin/env bash
# sa-0029 / sa-0079 — goal-dispatch-closure tracks orchestrator_dispatch_ready()
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
from strategic_synthesis_hub import strategic_goals, strategic_synthesis_payload
from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready

exp_ready, _, _ = orchestrator_dispatch_ready()
gdc = next((g for g in strategic_goals() if g.get("id") == "goal-dispatch-closure"), {})
assert gdc, "missing goal-dispatch-closure in strategic_goals()"
exp_status = "done" if exp_ready else "in_progress"
assert gdc.get("status") == exp_status, gdc
blocker = (gdc.get("blocker") or "").lower()
assert "spine" in blocker, f"blocker missing spine: {gdc.get('blocker')!r}"

payload = strategic_synthesis_payload()
pg = next(
    (g for g in (payload.get("strategic_goals") or []) if g.get("id") == "goal-dispatch-closure"),
    {},
)
assert pg.get("status") == exp_status, pg
assert pg.get("blocker") == gdc.get("blocker"), "payload strategic_goals drift"
print(
    f"OK: validate-goal-dispatch-closure-v1 · {exp_status} · "
    f"dispatch_ready={exp_ready} · blocker={gdc.get('blocker')!r}"
)
PY
