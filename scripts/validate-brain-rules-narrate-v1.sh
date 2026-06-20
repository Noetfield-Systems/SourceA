#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
check() {
  if eval "$2"; then
    echo "PASS: $1"
  else
    echo "FAIL: $1"
    fail=1
  fi
}

check "000-brain-unified forbids sick spawn on narrate" \
  'grep -q goal1_auto_loop .cursor/rules/000-brain-unified.mdc && grep -qi forbidden .cursor/rules/000-brain-unified.mdc'

check "GOAL1_LOOP_ACTIVATION uses brain_narrate for narrate prompt" \
  'grep -q brain_narrate_loop_v1.py brain-os/law/enforcement/GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md'

check "MANDATORY_BRAIN points to unified" \
  'grep -q BRAIN_UNIFIED_RULES_LOCKED_v1.md brain-os/contract/MANDATORY_BRAIN_CHAT_LOCKED_v1.md'

check "agent-loop points to brain unified" \
  'grep -q BRAIN_UNIFIED_RULES_LOCKED_v1.md .cursor/rules/agent-loop.mdc'

bash scripts/validate-brain-narrate-not-execute-v1.sh
bash scripts/validate-brain-narrate-loop-v1.sh

test "$fail" -eq 0
echo "OK: validate-brain-rules-narrate-v1"
