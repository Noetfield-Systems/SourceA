#!/usr/bin/env bash
# Contract: all hub_built_at asserts use shared retry sync (prevents sa-0042 class flake).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
cd "$ROOT"

test -f "$SCRIPTS/feedback_hub_sync_assert_v1.py"
grep -q "assert_feedback_hub_aligned" "$SCRIPTS/feedback_hub_sync_assert_v1.py"
grep -q "feedback_hub_sync_assert_v1" "$SCRIPTS/validate-feedback-aggregate-hub-sync-v1.sh"
grep -q "feedback_hub_sync_assert_v1" "$SCRIPTS/validate-phase-s0-ssot-alignment-v1.sh"
grep -q "for attempt in range(retries)" "$SCRIPTS/feedback_hub_sync_assert_v1.py"
grep -q "DEFAULT_RETRIES = 3" "$SCRIPTS/feedback_hub_sync_assert_v1.py"

python3 "$SCRIPTS/feedback_hub_sync_assert_v1.py" --label contract-check

echo "PASS: validate-hub-built-at-sync-contract-v1"
