#!/usr/bin/env bash
# validate-mandatory-read-paths-v1.sh — MANDATORY_READ_BY_ROLE must not cite dead os/chat-handoffs paths
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MR="$ROOT/brain-os/law/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md"

fail() { echo "FAIL: validate-mandatory-read-paths-v1 — $*" >&2; exit 1; }

[[ -f "$MR" ]] || fail "missing MANDATORY_READ_BY_ROLE_LOCKED_v1.md"

if grep -E '`os/chat-handoffs/|^\|.*os/chat-handoffs/' "$MR" >/dev/null 2>&1; then
  echo "FAIL: broken path citations still in MANDATORY_READ_BY_ROLE:" >&2
  grep -En '`os/chat-handoffs/|^\|.*os/chat-handoffs/' "$MR" >&2 || true
  fail "replace with brain-os/ canonical paths per brain-os/INDEX_LOCKED_v1.md"
fi

# Spot-check cited brain-os files exist (sample from Brain + Worker sections)
for rel in \
  brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md \
  brain-os/contract/BRAIN_COMPLETE_TRANSFER_LOCKED_v1.md \
  brain-os/law/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md \
  brain-os/system/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md \
  brain-os/lanes/MANDATORY_CHAT_HANDOFF_INDEX_LOCKED_v1.md
do
  [[ -f "$ROOT/$rel" ]] || fail "mandatory read cites missing: $rel"
done

echo "OK: validate-mandatory-read-paths-v1"
