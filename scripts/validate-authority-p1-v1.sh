#!/usr/bin/env bash
# P1 authority loops — rail enforce lib wired + reconciled stub.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f "$ROOT/scripts/authority_enforce_p1_lib.py"
test -f "$ROOT/brain-os/system/GOVERNANCE_P1_LOOPS_LOCKED_v1.md"

bash "$ROOT/scripts/validate-authority-runtime-v1.sh"

python3 <<PY
import sys
from pathlib import Path

root = Path("${ROOT}")
sys.path.insert(0, str(root / "scripts"))
from authority_enforce_p1_lib import (  # noqa: E402
    DEFAULT_GOVERNANCE_TRACES,
    check_rail_manual_inject,
    check_prompt_pick_authority,
    check_reconciled_before_inject,
    ensure_reconciled_decision_stub,
    sync_reconciled_decision,
    validate_manual_fallback,
)

r = check_rail_manual_inject(source="worker1_paste_queue")
assert not r.get("ok"), r
assert r.get("error") == "RAIL_A_MANUAL_INJECT_BLOCKED", r

ok = check_rail_manual_inject(source="healthy-drain-orchestrator")
assert ok.get("ok"), ok

p = check_prompt_pick_authority(
    text="PLAN WITH NO ASF — bash scripts/plan-no-asf-run.sh pick 1",
    source="manual_paste",
)
assert not p.get("ok"), p

stub = ensure_reconciled_decision_stub()
assert stub.is_file(), stub

row = sync_reconciled_decision()
cited = row.get("trace_ids_cited") or []
for tid in DEFAULT_GOVERNANCE_TRACES:
    assert tid in cited, (tid, cited)
assert row.get("next_sa", "").startswith("sa-"), row

adv = check_prompt_pick_authority(
    text="run plan-no-asf-run.sh pick 1 for sa-0999",
    source="gpt_advisor",
)
assert not adv.get("ok"), adv
assert adv.get("error") == "AUTHORITY_ADVISOR_PICK_BREACH", adv

unsigned = validate_manual_fallback({"manual_fallback": True})
assert not unsigned.get("ok"), unsigned

recon = check_reconciled_before_inject(source="healthy-drain-orchestrator", sa_id=row.get("next_sa"))
assert recon.get("ok"), recon

print("OK: validate-authority-p1-v1")
PY

test -f "$ROOT/brain-os/system/EVENT_CONTRACT.yaml"
test -f "$ROOT/scripts/execution_event_log_v1.py"
