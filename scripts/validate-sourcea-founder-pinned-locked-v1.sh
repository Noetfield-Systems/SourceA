#!/usr/bin/env bash
# LOCK seal — founder pinned actions + 1000-pack judge + PRIORITY live head.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

for f in \
  SOURCEA_FOUNDER_PINNED_ACTIONS_LOCKED_v1.md \
  SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md \
  SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md; do
  test -f "$ROOT/$f"
done

grep -q "Master result table" "$ROOT/SOURCEA_FOUNDER_PINNED_ACTIONS_LOCKED_v1.md"
grep -q "honest_done" "$ROOT/SOURCEA_FOUNDER_PINNED_ACTIONS_LOCKED_v1.md"
grep -q "COMMERCIAL_GOAL-REF-1000PACK-AUDIT-018" "$ROOT/SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md"
grep -q "250 unique intents" "$ROOT/SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md" || \
  grep -q "250×4" "$ROOT/SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md"

PRI="$ROOT/brain-os/plan-registry/SOURCEA-PRIORITY.md"
grep -q "honest_done" "$PRI"
grep -q "SOURCEA_FOUNDER_PINNED_ACTIONS_LOCKED_v1.md" "$PRI"
grep -q "SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md" "$PRI"
grep -q "SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md" "$PRI"
grep -q "goal-progress-v1.py" "$PRI"
! grep -q "275 done / 725 backlog" "$PRI" || { echo "FAIL: stale 275 counter still in PRIORITY header"; exit 1; }

for f in \
  SOURCEA_SESSION_20260609_COMPLETE_INDEX_LOCKED_v1.md \
  SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md \
  SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md; do
  test -f "$ROOT/$f"
done

python3 <<PY
import json
from datetime import datetime, timezone
from pathlib import Path

receipt = {
    "schema": "sourcea-founder-pinned-lock-v1",
    "locked": True,
    "validated_at": datetime.now(timezone.utc).isoformat(),
    "validator": "validate-sourcea-founder-pinned-locked-v1.sh",
    "documents": [
        "SOURCEA_FOUNDER_PINNED_ACTIONS_LOCKED_v1.md",
        "SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md",
        "SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md",
    ],
    "trace_id": "COMMERCIAL_GOAL-REF-2026-06-10-1000PACK-AUDIT-018",
}
path = Path.home() / ".sina" / "sourcea-founder-pinned-lock-v1.json"
path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(f"OK: receipt {path}")
PY

echo "SOURCEA-FOUNDER-PINNED VALID locked=ok"
