#!/usr/bin/env bash
# LOCK seal — session 2026-06-09 complete index + Worker E2E post-mortem + result policy.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"

for f in \
  SOURCEA_SESSION_20260609_COMPLETE_INDEX_LOCKED_v1.md \
  SOURCEA_WORKER_E2E_POSTMORTEM_LOCKED_v1.md \
  SOURCEA_GOLDEN_INSIGHT_AND_SAFETY_LOCKED_v1.md \
  SOURCEA_BRAIN_MONITOR_FIX_REPORT_LOCKED_v1.md \
  SOURCEA_MASTER_SESSION_MANIFEST_LOCKED_v1.md \
  SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md \
  SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md; do
  test -f "$ROOT/$f"
done

GI="$ROOT/SOURCEA_GOLDEN_INSIGHT_AND_SAFETY_LOCKED_v1.md"
grep -q "two companies inside one factory" "$GI"
grep -q "Golden recommendations" "$GI"
grep -q "golden.*operating system" "$GI"
grep -q "FOUNDER_LANE_SEPARATION" "$GI"
grep -q "validate-ecosystem-safety-v1" "$GI"
test -f "$ROOT/brain-os/enforcement/FOUNDER_LANE_SEPARATION_LOCKED_v1.md"

BM="$ROOT/SOURCEA_BRAIN_MONITOR_FIX_REPORT_LOCKED_v1.md"
grep -q "Brain was right to push back" "$BM"
grep -q "STALE broker 67" "$BM"
grep -q "HERE stuck on sa-0035" "$BM"
grep -q ":13021" "$BM"
grep -q "Two separate problems" "$BM"
grep -q "monitor_honesty_lib" "$BM"

MM="$ROOT/SOURCEA_MASTER_SESSION_MANIFEST_LOCKED_v1.md"
grep -q "MASTER-MANIFEST" "$MM"
grep -q "FULLY ON DISK" "$MM"
grep -q "Gaps / partial" "$MM"
grep -q "SOURCEA_WORKER_E2E_POSTMORTEM" "$MM"
grep -q "SinaaiDataBase" "$MM"

PM="$ROOT/SOURCEA_WORKER_E2E_POSTMORTEM_LOCKED_v1.md"
grep -q "Executive verdict" "$PM"
grep -q "22:33:50" "$PM"
grep -q "22:33:59" "$PM"
grep -q "Six reasons wall-clock exploded" "$PM"
grep -q "feedback_hub_sync_assert_v1.py" "$PM"
grep -q "Worker vs Brain vs Monitor" "$PM"
grep -q "One-line truth" "$PM"

IDX="$ROOT/SOURCEA_SESSION_20260609_COMPLETE_INDEX_LOCKED_v1.md"
grep -q "Master result table" "$IDX"
grep -q "Worker E2E post-mortem" "$IDX"

grep -q "SA-2026-06-09-WORKER-E2E-POSTMORTEM" "$ROOT/SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md" || \
  grep -q "SOURCEA_WORKER_E2E_POSTMORTEM" "$ROOT/SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md"
grep -q "SOURCEA_SESSION_20260609" "$ROOT/brain-os/plan-registry/SOURCEA-PRIORITY.md"
grep -q "SOURCEA_FOUNDER_PINNED_ACTIONS_LOCKED_v1.md" "$ROOT/brain-os/plan-registry/SOURCEA-PRIORITY.md"

bash "$SCRIPTS/validate-sourcea-e2e-playbook-locked-v1.sh" >/dev/null
test -f "$ROOT/SOURCEA_FOUNDER_PINNED_ACTIONS_LOCKED_v1.md"
test -f "$ROOT/SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md"
test -f "$ROOT/SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md"
grep -q "COMMERCIAL_GOAL-REF-1000PACK-AUDIT-018" "$ROOT/SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md"
grep -q "LAYER 11" "$ROOT/SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md"

python3 <<PY
import json
from datetime import datetime, timezone
from pathlib import Path

receipt = {
    "schema": "sourcea-session-20260609-lock-v1",
    "locked": True,
    "session_date": "2026-06-09",
    "validated_at": datetime.now(timezone.utc).isoformat(),
    "validator": "validate-sourcea-session-index-locked-v1.sh",
    "documents": [
        "SOURCEA_SESSION_20260609_COMPLETE_INDEX_LOCKED_v1.md",
        "SOURCEA_WORKER_E2E_POSTMORTEM_LOCKED_v1.md",
        "SOURCEA_GOLDEN_INSIGHT_AND_SAFETY_LOCKED_v1.md",
        "SOURCEA_BRAIN_MONITOR_FIX_REPORT_LOCKED_v1.md",
        "SOURCEA_MASTER_SESSION_MANIFEST_LOCKED_v1.md",
        "SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md",
        "SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md",
    ],
    "post_mortem_verdict": "Worker analysis correct; sa-0042 late check; 9s flake not 40min system break",
}
out = Path.home() / ".sina" / "sourcea-session-20260609-lock-v1.json"
out.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
print(f"OK: session lock receipt → {out}")
PY

echo "PASS: validate-sourcea-session-index-locked-v1"
