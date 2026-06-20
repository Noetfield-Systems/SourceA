#!/usr/bin/env bash
# Wiring check — Brain disk-before-chat gate exists and is referenced.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
errors=0

check() {
  if ! grep -q "$2" "$1" 2>/dev/null; then
    echo "FAIL: $1 missing $2"
    errors=$((errors + 1))
  fi
}

law="${ROOT}/os/chat-handoffs/BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md"
script="${ROOT}/scripts/brain-session-start.sh"
[[ -f "$law" ]] || { echo "FAIL: missing $law"; errors=$((errors + 1)); }
[[ -x "$script" ]] || { echo "FAIL: brain-session-start.sh not executable"; errors=$((errors + 1)); }

check "${ROOT}/os/chat-handoffs/MANDATORY_BRAIN_CHAT_LOCKED_v1.md" "brain-session-start.sh"
check "${ROOT}/os/chat-handoffs/BRAIN_COMPLETE_TRANSFER_LOCKED_v1.md" "BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP"
check "${ROOT}/os/chat-handoffs/BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md" "Brain disk-before-chat"
check "${ROOT}/scripts/sync-brain-pack.sh" "BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP"
check "${ROOT}/.cursor/rules/000-entry-gate.mdc" "brain-session-start.sh"

bash "$ROOT/scripts/validate-cursor-entry-gate-v1.sh" || errors=$((errors + 1))

if [[ $errors -gt 0 ]]; then
  echo "FAIL: validate-brain-disk-before-chat-v1 ($errors)"
  exit 1
fi
echo "OK: validate-brain-disk-before-chat-v1"
