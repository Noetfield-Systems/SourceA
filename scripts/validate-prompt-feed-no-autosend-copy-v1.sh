#!/usr/bin/env bash
# validate-prompt-feed-no-autosend-copy-v1.sh — INCIDENT-028: no founder-facing auto-send confirm copy
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-prompt-feed-no-autosend-copy-v1 — $*" >&2; exit 1; }

# Founder-facing surfaces that must not resurrect pre-024 "confirm auto-send" model
# Monolith app.js retired (ASF_RETIRE_SINA_COMMAND_FOREVER) — H1 Worker Hub is daily surface
declare -a CHECKS=(
  "agent-control-panel/worker-hub/index.html|review before auto-send|auto-send"
  "agent-control-panel/worker-hub/index.html|review the 10 steps|review 10 steps"
  "agent-control-panel/worker-hub/index.html|auto-send|auto-send"
  "agent-control-panel/worker-hub/index.html|Prompt feed|Prompt feed"
  "scripts/founder_commitments.py|auto-sending|auto-send"
  "scripts/sync_founder_missed_actions_v1.py|confirm 10 steps|confirm 10"
  "scripts/hub_home_founder_view_v1.py|confirm 10 follow-up|confirm 10"
  "scripts/hub_essentials_index.py|confirm 10 prompts|confirm 10"
  "scripts/prompt_direction.py|confirm then auto-feed|confirm then auto-feed"
)

for entry in "${CHECKS[@]}"; do
  IFS='|' read -r file pattern label <<<"$entry"
  path="$ROOT/$file"
  [[ -f "$path" ]] || fail "missing $file"
  if grep -Eiq "$pattern" "$path"; then
    echo "FAIL: stale prompt-feed copy ($label) in $file:" >&2
    grep -Ein "$pattern" "$path" >&2 || true
    fail "$file still contains forbidden: $label"
  fi
done

queue_doc="$ROOT/SINA_CURSOR_PROMPT_QUEUE_ORDER_v1.md"
confirm_row="$(grep -E '^\| `confirm`' "$queue_doc" || true)"
if echo "$confirm_row" | grep -Eiq 'auto-feed|auto-send'; then
  echo "FAIL: stale confirm API row in SINA_CURSOR_PROMPT_QUEUE_ORDER_v1.md:" >&2
  echo "$confirm_row" >&2
  fail "confirm row still promotes auto-feed"
fi

# Disk law — positive close-line only (INCIDENT-034 · no prohibition inject in rule)
rule="$ROOT/.cursor/rules/prompt-queue.mdc"
[[ -f "$rule" ]] || fail "missing prompt-queue.mdc"
grep -q 'Next steps' "$rule" || fail "prompt-queue.mdc must name daily surface Next steps"
grep -q 'Worker Hub\|127.0.0.1:13020' "$rule" || fail "prompt-queue.mdc must point to Worker Hub"
grep -q 'RUN INBOX' "$rule" || fail "prompt-queue.mdc must name RUN INBOX primary"
grep -q 'factory_now_line' "$rule" || fail "prompt-queue.mdc must quote factory_now_line"
if grep -qiE 'auto[- ]?send|confirm.*10.*prompt|review the 10 steps|Prompt feed.*Confirm' "$rule"; then
  fail "prompt-queue.mdc contains stale auto-send steer"
fi

inc="$ROOT/brain-os/incidents/SINA_WORKER_STALE_PROMPT_FEED_AUTOSEND_INCIDENT_028_LOCKED_v1.md"
[[ -f "$inc" ]] || fail "missing INCIDENT-028 body"

echo "OK: validate-prompt-feed-no-autosend-copy-v1"
