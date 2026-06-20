#!/usr/bin/env bash
# validate-disclosure-ladder-v1.sh — disclosure SSOT + full wire chain
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=governance-paths-v1.sh
. "$ROOT/scripts/governance-paths-v1.sh"
SINA="${HOME}/.sina"
DOC="$ROOT/docs/SOURCEA_DISCLOSURE_LADDER_AND_PUBLIC_VOICE_LOCKED_v1.md"
SSOT="$ROOT/data/disclosure-ladder-v1.json"
fail=0

check_file() {
  local p="$1"
  if [[ ! -f "$p" ]]; then
    echo "FAIL missing: $p"
    fail=1
  fi
}

check_grep() {
  local file="$1"
  local needle="$2"
  local msg="$3"
  if ! grep -q "$needle" "$file"; then
    echo "FAIL $msg"
    fail=1
  fi
}

check_file "$DOC"
check_file "$SSOT"
check_file "$ROOT/scripts/disclosure_ladder_v1.py"
check_file "$ROOT/investor/README.md"
check_file "$ROOT/docs/research-vault/GOLDEN_REPORT_SOURCEA_SITE_POSITIONING_v1.md"
check_file "$ROOT/docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md"
check_file "$ROOT/docs/SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md"
check_file "$ROOT/archive/attachments/founder-language/linkedin-voice.yaml"
check_file "$ROOT/data/commercial-film-routing-v1.json"
check_file "$ROOT/data/commercial/stack-map-routing-v1.json"

if ! grep -q '\*\*Saved:\*\*.*T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z' "$DOC"; then
  echo "FAIL doc missing Saved: UTC timestamp"
  fail=1
fi

for section in "Five-tier disclosure ladder" "Forbidden terms matrix" "Double-check audit" "Agent & presentation layer map"; do
  if ! grep -q "$section" "$DOC"; then
    echo "FAIL doc missing section: $section"
    fail=1
  fi
done

check_grep "$ROOT/scripts/icp_output_compiler_v1.py" "disclosure_ladder_v1" "icp compiler missing disclosure hook"
check_grep "$ROOT/scripts/advisor_pre_call_email_loop_v1.py" "disclosure_ladder_v1" "advisor loop missing disclosure hook"
check_grep "$ROOT/data/icp-output-compiler-v1.json" "disclosure_tier_picker" "icp compiler SSOT missing disclosure_tier_picker"
check_grep "$ROOT/data/icp-compile/fundmore-v1.json" "disclosure_tier" "fundmore missing disclosure_tier"
check_grep "$ROOT/scripts/icp_output_compiler_v1.py" "disclosure_tier" "icp compiler missing disclosure_tier hook"
check_grep "$SINA_AUTHORITY_INDEX" "DISCLOSURE_LADDER" "authority index missing DISCLOSURE_LADDER row"
check_grep "$SINA_AUTHORITY_INDEX" "MCP_STACK_FREE_TIER" "authority index missing MCP_STACK_FREE_TIER row"
check_grep "$ROOT/scripts/vocabulary_guard_v1.py" "check_disclosure_ladder" "vocabulary guard missing disclosure check"
check_grep "$ROOT/scripts/vocabulary_guard_v1.py" "check_mcp_stack" "vocabulary guard missing mcp_stack check"
check_grep "$ROOT/scripts/disk_live_wire_sync_v1.py" "disclosure_ladder" "disk_live_wire missing disclosure step"
check_grep "$ROOT/scripts/agent_session_gate_run_v1.py" "disclosure_ladder_v1.py" "session gate missing disclosure step"
check_grep "$ROOT/scripts/worker_hub_v1.py" "disclosure_ladder" "worker_hub missing disclosure slice"
check_grep "$ROOT/scripts/sina-command-server.py" "/api/disclosure-ladder/tick/v1" "hub API missing disclosure route"
check_grep "$ROOT/agent-control-panel/worker-hub/index.html" "disclosure-ladder-card" "H1 UI missing disclosure card"
check_grep "$ROOT/data/commercial/stack-map-routing-v1.json" "disclosure_ladder_v1" "stack-map missing disclosure in loop chain"

chmod +x "$ROOT/scripts/disclosure_ladder_v1.py" 2>/dev/null || true
python3 "$ROOT/scripts/disclosure_ladder_v1.py" --json >/dev/null || { echo "FAIL disclosure_ladder run"; fail=1; }
test -f "${SINA}/disclosure-ladder-receipt-v1.json" || { echo "FAIL missing disclosure receipt"; fail=1; }

python3 - <<'PY' || { echo "FAIL receipt schema"; fail=1; }
import json
from pathlib import Path
r = json.loads((Path.home() / ".sina/disclosure-ladder-receipt-v1.json").read_text())
assert r.get("schema") == "disclosure-ladder-receipt-v1"
assert r.get("disclosure_line")
assert r.get("wired") is True
print("OK:", r.get("disclosure_line", "")[:72])
PY

if [[ "$fail" -ne 0 ]]; then
  echo "validate-disclosure-ladder-v1: FAIL"
  exit 1
fi

echo "validate-disclosure-ladder-v1: PASS"
exit 0
