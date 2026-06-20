#!/usr/bin/env bash
# Hub form — founder pick controls only (INCIDENT-037). Filename kept for wire compat.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FORM="$ROOT/agent-control-panel/form/index.html"
fail() { echo "FAIL: validate-hub-form-automatic-v1 — $*" >&2; exit 1; }

[[ -f "$FORM" ]] || fail "missing form/index.html"
[[ -f "$ROOT/scripts/hub_form_submit_v1.py" ]] || fail "missing hub_form_submit_v1.py"
[[ -f "$ROOT/scripts/form_founder_supremacy_guard_v1.py" ]] || fail "missing form_founder_supremacy_guard_v1.py"

grep -q 'id="btn-submit"' "$FORM" || fail "missing Submit button"
grep -q 'type="radio"' "$FORM" || fail "missing radio pick controls per row"
grep -q 'founder_submit' "$FORM" || fail "missing founder_submit in POST body"
grep -q 'YOU picked' "$FORM" || fail "missing YOU picked stat (founder supremacy UI)"
grep -q 'explicit' "$FORM" || fail "missing explicit pick tracking"
# Draft must never auto-count as founder pick
if awk '/async function loadDraft/,/^    }/' "$FORM" | grep -q 'state.explicit\[id\] = true'; then
  fail "loadDraft must not set explicit=true from draft (INCIDENT-037)"
fi
grep -q 'saved draft (tap to confirm)' "$FORM" || fail "missing draft hint copy (tap to confirm)"

for bad in '(recommended) AUTOMATIC' '· automatic' 'submit_automatic' '116 rows · automatic' 'clipboard' 'Copy reply' 'Copy ASF' 'paste in' 'FIVE-STEP' 'btn-copy' 'asf-preview' 'btn-prev' 'btn-next'; do
  if grep -qi "$bad" "$FORM"; then
    fail "forbidden in form UI: $bad"
  fi
done

python3 "$ROOT/scripts/hub_form_submit_v1.py" --dry-state --json >/dev/null || fail "hub_form_submit dry-state"

agent_block="$(python3 "$ROOT/scripts/hub_form_submit_v1.py" --json --actor agent 2>/dev/null || true)"
echo "$agent_block" | grep -q 'FORM_AGENT_SUBMIT_FORBIDDEN\|SUBMIT_AUTOMATIC_FORBIDDEN\|blocked' \
  || fail "agent submit must be blocked"

echo "PASS: validate-hub-form-automatic-v1 (founder pick supremacy · INCIDENT-037)"
