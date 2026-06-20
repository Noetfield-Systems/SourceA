#!/usr/bin/env bash
# Sync brain-os knowledge pack from SourceA to ~/.sina/brain/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BO="$ROOT/brain-os"
DEST="${HOME}/.sina/brain"
mkdir -p "$DEST/entry"
cp "$BO/entry/"*.md "$DEST/entry/" 2>/dev/null || true
cp "$BO/law/"*.md "$DEST/" 2>/dev/null || true
cp "$BO/memory/"*.md "$DEST/" 2>/dev/null || true
cp "$BO/contract/"*.md "$DEST/" 2>/dev/null || true
cp "$BO/enforcement/"BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md "$DEST/" 2>/dev/null || true
cp "$BO/system/"CONTROLLED_EXECUTION_OS_MASTER_LOCKED_v1.md "$DEST/" 2>/dev/null || true
cp "$BO/system/"GOAL_HIERARCHY_LOCKED_v1.md "$DEST/" 2>/dev/null || true
cp "$BO/system/"FOUNDER_DAILY_OPERATING_MODEL_LOCKED_v1.md "$DEST/" 2>/dev/null || true
cp "$BO/system/"WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md "$DEST/" 2>/dev/null || true
cp "$BO/system/"AGENT_MISS_DISK_FIRST_CORRECTION_LOOP_LOCKED_v1.md "$DEST/" 2>/dev/null || true
cp "$BO/system/"ECOSYSTEM_BRAIN_ROLLOUT_LOCKED_v1.md "$DEST/" 2>/dev/null || true
cp "$BO/system/"UNIFIED_RESEARCH_ROOT_LOCKED_v1.md "$DEST/" 2>/dev/null || true
cp "$BO/system/"SINAAIDB_ARCHIVE_RETIREMENT_HANDOFF_LOCKED_v1.md "$DEST/" 2>/dev/null || true
cp "$BO/INDEX_LOCKED_v1.md" "$DEST/" 2>/dev/null || true
echo "OK: brain-os synced to $DEST (canonical: $BO)"
