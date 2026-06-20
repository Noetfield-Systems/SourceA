#!/usr/bin/env bash
# validate-mcp-stack-free-tier-v1.sh — MCP free-tier SSOT + wire chain
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
DOC="$ROOT/docs/SOURCEA_MCP_STACK_FREE_TIER_OPTIMIZATION_LOCKED_v1.md"
SSOT="$ROOT/data/mcp-stack-free-tier-v1.json"
MANIFEST="$ROOT/data/cursor-mcp-free-tier-manifest-v1.json"
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
check_file "$MANIFEST"
check_file "$ROOT/scripts/mcp_stack_free_tier_v1.py"
check_file "$ROOT/data/integration-leverage-registry-v1.json"

if ! grep -q '\*\*Saved:\*\*.*T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z' "$DOC"; then
  echo "FAIL doc missing Saved: UTC timestamp"
  fail=1
fi

check_grep "$ROOT/data/integration-leverage-registry-v1.json" "mcp_stack_ssot" "registry missing mcp_stack_ssot"
check_grep "$ROOT/scripts/disk_live_wire_sync_v1.py" "mcp_stack" "disk_live_wire missing mcp_stack step"
check_grep "$ROOT/scripts/agent_session_gate_run_v1.py" "mcp_stack_free_tier_v1.py" "session gate missing mcp_stack step"
check_grep "$ROOT/scripts/worker_hub_v1.py" "mcp_stack" "worker_hub missing mcp_stack slice"
check_grep "$ROOT/scripts/sina-command-server.py" "/api/mcp-stack/tick/v1" "hub API missing mcp_stack route"
check_grep "$ROOT/agent-control-panel/worker-hub/index.html" "mcp-stack-card" "H1 UI missing mcp stack card"
check_grep "$ROOT/data/commercial/stack-map-routing-v1.json" "mcp_stack_free_tier_v1" "stack-map missing mcp_stack in loop chain"
check_grep "$ROOT/data/commercial/stack-map-routing-v1.json" "mcp_stack_free_tier" "stack-map missing mcp_stack cross_ref"
check_grep "$ROOT/scripts/validate-trust-center-v1.sh" "trust-center-receipt" "missing trust center validator"

chmod +x "$ROOT/scripts/mcp_stack_free_tier_v1.py" 2>/dev/null || true
python3 "$ROOT/scripts/mcp_stack_free_tier_v1.py" --json >/dev/null || { echo "FAIL mcp_stack run"; fail=1; }
test -f "${SINA}/mcp-stack-free-tier-receipt-v1.json" || { echo "FAIL missing mcp stack receipt"; fail=1; }

python3 - <<'PY' || { echo "FAIL receipt schema"; fail=1; }
import json
from pathlib import Path
r = json.loads((Path.home() / ".sina/mcp-stack-free-tier-receipt-v1.json").read_text())
assert r.get("schema") == "mcp-stack-free-tier-receipt-v1"
assert r.get("mcp_stack_line")
assert r.get("wired") is True
print("OK:", r.get("mcp_stack_line", "")[:72])
PY

if [[ "$fail" -ne 0 ]]; then
  echo "validate-mcp-stack-free-tier-v1: FAIL"
  exit 1
fi

echo "validate-mcp-stack-free-tier-v1: PASS"
exit 0
