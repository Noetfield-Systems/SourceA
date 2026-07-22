#!/usr/bin/env bash
# FORM founder supremacy — ONE command, any directory (INCIDENT-037 · INCIDENT-019)
#
#   bash ~/Desktop/SourceA/scripts/wbc-form-check.sh
#
set -euo pipefail

WBC_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WBC_ROOT="$(cd "$WBC_SCRIPT/.." && pwd)"
REGISTRY="$WBC_ROOT/brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md"
INCIDENT_037="$WBC_ROOT/docs/SOURCEA_INCIDENT_037_FORM_FOUNDER_SUPREMACY_LOCKED_v1.md"

echo "=== WBC FORM CHECK (founder supremacy) ==="
echo "    site root: $WBC_ROOT"
echo ""

[[ -f "$REGISTRY" ]] || { echo "FAIL: missing incident registry"; exit 1; }
incident_rows="$(grep -cE '^\| \*\*[0-9]' "$REGISTRY" || true)"
echo "OK  incident registry on disk — $incident_rows canonical rows (001–037)"
[[ -f "$INCIDENT_037" ]] || { echo "FAIL: missing INCIDENT-037 body"; exit 1; }
echo "OK  INCIDENT-037 body: docs/SOURCEA_INCIDENT_037_FORM_FOUNDER_SUPREMACY_LOCKED_v1.md"
echo ""

if [[ -f "$HOME/.sina/form-agent-submit-forbidden-v1.flag" ]]; then
  echo "OK  agent submit block flag ON"
else
  echo "FAIL  form-agent-submit-forbidden-v1.flag missing"
  exit 1
fi

applied="$(python3 -c "import json,pathlib; p=pathlib.Path.home()/'.sina/canvas-form-picks-applied-v1.json'; d=json.loads(p.read_text()) if p.is_file() else {}; print(len((d.get('picks') or {})))" 2>/dev/null || echo "?")"
draft="$(python3 -c "import json,pathlib; p=pathlib.Path.home()/'.sina/canvas-form-picks-draft-v1.json'; d=json.loads(p.read_text()) if p.is_file() else {}; print(len((d.get('picks') or {})))" 2>/dev/null || echo "?")"
open_q="$(python3 -c "import sys; sys.path.insert(0,'$WBC_SCRIPT'); from live_founder_decision_form_v1 import payload; print(int(payload().get('open_questions_count') or 0))" 2>/dev/null || echo "?")"
echo "GUARD  open_questions=$open_q · applied_picks=$applied · draft_picks=$draft"
if [[ "$applied" != "0" ]]; then
  echo "FAIL  applied picks non-zero — agent bulk or fake submit detected"
  exit 1
fi
echo ""

bash "$WBC_SCRIPT/validate-form-founder-supremacy-v1.sh"
bash "$WBC_SCRIPT/validate-copy-safety-hub-v1.sh"
echo ""
echo "PASS: form supremacy guard chain OK · no invitation"
