#!/usr/bin/env bash
# WBC GUARD CHECK — ONE command, any directory. Stable system only — NO invitation.
#
#   bash ~/Desktop/SourceA/scripts/wbc-guard-check.sh
#
set -euo pipefail

WBC_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WBC_ROOT="$(cd "$WBC_SCRIPT/.." && pwd)"

echo "=== WBC GUARD CHECK (stable · no invitation) ==="
echo "    root: $WBC_ROOT"
echo ""

[[ -f "$HOME/.sina/founder-no-agent-invitation-v1.flag" ]] && echo "OK  founder-no-agent-invitation flag ON" \
  || { echo "FAIL  founder-no-agent-invitation flag missing"; exit 1; }
[[ -f "$HOME/.sina/form-agent-submit-forbidden-v1.flag" ]] && echo "OK  form-agent-submit-forbidden flag ON" \
  || { echo "FAIL  form-agent-submit-forbidden flag missing"; exit 1; }
echo ""

bash "$WBC_SCRIPT/validate-no-agent-invitation-v1.sh"
echo ""
bash "$WBC_SCRIPT/wbc-form-check.sh"
echo ""
bash "$WBC_SCRIPT/wbc-ui-first-check.sh"
echo ""
bash "$WBC_SCRIPT/wbc-e2e.sh"
echo ""
echo "PASS: WBC guard chain complete · all validators OK · no invitation"
