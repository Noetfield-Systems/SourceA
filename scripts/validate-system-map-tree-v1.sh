#!/usr/bin/env bash
# validate-system-map-tree-v1.sh — canonical navigation tree wired
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TREE="$ROOT/SOURCEA_SYSTEM_MAP_TREE_LOCKED_v1.md"
AUTH="$ROOT/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md"
ENTRY="$ROOT/brain-os/entry/START_HERE_LOCKED_v1.md"

fail() { echo "FAIL: validate-system-map-tree-v1 — $*" >&2; exit 1; }

[[ -f "$TREE" ]] || fail "missing $TREE"
grep -q "SOURCEA_SYSTEM_MAP_TREE_LOCKED_v1" "$AUTH" || fail "authority index missing map tree row"
grep -q "DISK_TRUTH_E2E" "$AUTH" || fail "authority index missing DISK_TRUTH_E2E row"
grep -q "SOURCEA_DISK_TRUTH_E2E_MATRIX" "$TREE" || fail "map tree missing DISK_TRUTH_E2E node"
grep -q "SYSTEM_MAP_TREE" "$ENTRY" || fail "START_HERE missing map tree pointer"

for f in \
  "$ROOT/SOURCEA_DISK_TRUTH_E2E_MATRIX_LOCKED_v1.md" \
  "$ROOT/RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md" \
  "$ROOT/SOURCEA_MONITOR_DISK_LIVE_WIRE_LOCKED_v1.md" \
  "$ROOT/brain-os/laws/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md" \
  "$ROOT/brain-os/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md" \
  "$ROOT/scripts/brain_sync_lib_v1.py" \
  "$ROOT/scripts/factory_control_v1.py"
do
  [[ -f "$f" ]] || fail "tree cites missing path: $f"
done

grep -q "archive/attachments" "$TREE" && grep -q "INDEX ONLY" "$TREE" || fail "archive rule missing"

echo "OK: validate-system-map-tree-v1"
