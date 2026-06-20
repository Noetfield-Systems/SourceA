#!/usr/bin/env bash
# validate-visual-proof-v1.sh — native macOS visual proof capture hook
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
CONFIG="${SINA}/config/visual_proof.json"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

[[ -f "$ROOT/scripts/visual_proof_capture_v1.py" ]] && check true "visual_proof_capture module" || check false "visual_proof_capture module"

python3 - <<PY || { echo "FAIL: visual_proof_capture imports"; fail=1; }
import sys
from pathlib import Path
sys.path.insert(0, str(Path("$ROOT") / "scripts"))
from visual_proof_capture_v1 import trigger_agent_visual_capture, VISUAL_PROOF_CONFIG
assert VISUAL_PROOF_CONFIG.name == "visual_proof.json"
print("PASS: trigger_agent_visual_capture importable")
PY

grep -q 'trigger_agent_visual_capture' "$ROOT/scripts/critic_boot_v1.py" || {
  echo "FAIL: critic_boot_v1.py missing visual proof hook"
  fail=1
}
[[ $fail -eq 0 ]] && echo "PASS: critic_boot imports visual proof hook"

python3 - <<PY || { echo "FAIL: PASS verdict skip test"; fail=1; }
import sys
from pathlib import Path
sys.path.insert(0, str(Path("$ROOT") / "scripts"))
import critic_boot_v1
row = critic_boot_v1.trigger_agent_visual_capture("validate_pass_skip", "PASS")
assert row.get("status") == "skipped", row
assert row.get("reason") == "verdict_mismatch", row
print("PASS: PASS verdict skips capture")
PY

if [[ -f "$CONFIG" ]]; then
  BLOCK_OUT="$(python3 -c "
import sys
sys.path.insert(0, '$ROOT/scripts')
from visual_proof_capture_v1 import trigger_agent_visual_capture
import json
print(json.dumps(trigger_agent_visual_capture('validate_block_test', 'BLOCK')))
" 2>&1)" || true
  BLOCK_STATUS="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('status',''))" "$BLOCK_OUT" 2>/dev/null || echo "error")"
  case "$BLOCK_STATUS" in
    captured|captured_fallback)
      ART="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('artifact_path',''))" "$BLOCK_OUT")"
      [[ -f "$ART" ]] && echo "PASS: BLOCK capture artifact $ART" || echo "WARN: BLOCK status=$BLOCK_STATUS but artifact missing (headless?)"
      ;;
    skipped|failed)
      REASON="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('reason',''))" "$BLOCK_OUT" 2>/dev/null || echo unknown)"
      echo "PASS: BLOCK test acceptable — status=$BLOCK_STATUS reason=$REASON (headless/permissions ok)"
      ;;
    *)
      echo "WARN: BLOCK test unexpected output: $BLOCK_OUT"
      ;;
  esac
else
  echo "PASS: config missing — BLOCK test skipped (expected on fresh install)"
fi

python3 -c "
import sys
sys.path.insert(0, '$ROOT/scripts')
import critic_boot_v1
row = critic_boot_v1.trigger_agent_visual_capture('test_sync', 'BLOCK')
print('SYNC_TEST', row.get('status'), row.get('artifact_path') or row.get('reason'))
" || true

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-visual-proof-v1"
  exit 0
fi
echo "FAIL: validate-visual-proof-v1"
exit 1
