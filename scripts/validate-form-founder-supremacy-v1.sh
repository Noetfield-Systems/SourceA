#!/usr/bin/env bash
# FORM founder supremacy — permanent guard chain (INCIDENT-037)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-form-founder-supremacy-v1 — $*" >&2; exit 1; }

[[ -f "$HOME/.sina/form-agent-submit-forbidden-v1.flag" ]] \
  || fail "missing form-agent-submit-forbidden-v1.flag"

bash "$ROOT/scripts/validate-hub-form-automatic-v1.sh"
bash "$ROOT/scripts/validate-ui-zero-drift-v1.sh"
bash "$ROOT/scripts/validate-founder-no-invitation-v1.sh"
bash "$ROOT/scripts/validate-copy-safety-hub-v1.sh"

# Agent apply blocked
apply_out="$(python3 "$ROOT/scripts/canvas_form_apply_picks_v1.py" --sync-applied --apply --json 2>&1 || true)"
echo "$apply_out" | grep -q 'FORM_AGENT_SUBMIT_FORBIDDEN\|blocked' \
  || fail "canvas_form_apply must block agent apply when flag ON"

# Agent canvas submit blocked
submit_out="$(python3 "$ROOT/scripts/canvas_form_submit_v1.py" --json 2>&1 || true)"
echo "$submit_out" | grep -q 'FORM_AGENT_SUBMIT_FORBIDDEN\|blocked' \
  || fail "canvas_form_submit must block agent CLI when flag ON"

# CLI --founder spoof blocked without unlock flag
if [[ -f "$HOME/.sina/form-founder-submit-unlock-v1.flag" ]]; then
  echo "WARN: unlock flag present — skipping CLI founder spoof test"
else
  spoof_out="$(python3 "$ROOT/scripts/canvas_form_apply_picks_v1.py" --apply --founder --json 2>&1 || true)"
  echo "$spoof_out" | grep -q 'FOUNDER_HUB_SUBMIT_ONLY\|blocked' \
    || fail "CLI --founder must NOT bypass block without unlock flag"
fi

# Hub form HTML must not pre-select from recommended alone
grep -q 'explicit' "$ROOT/agent-control-panel/form/index.html" \
  || fail "hub form missing explicit pick tracking"

# Guard module must require trusted channel
grep -q 'TRUSTED_CHANNELS' "$ROOT/scripts/form_founder_supremacy_guard_v1.py" \
  || fail "guard missing TRUSTED_CHANNELS"

# apply() must not backfill recommended
if grep -q 'open_recommended' "$ROOT/scripts/canvas_form_apply_picks_v1.py"; then
  fail "canvas_form_apply still has recommended backfill — forbidden INCIDENT-037"
fi

echo "PASS: validate-form-founder-supremacy-v1"
