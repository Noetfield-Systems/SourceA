#!/usr/bin/env bash
# validate-all-e2e-v1.sh — master E2E: bootstrap · video factory · MCP · hub · governance
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "validate-all-e2e-v1.sh" "$ROOT"
FAIL=0
fail() { echo "FAIL: all-e2e — $*" >&2; FAIL=1; }

echo "== 1/6 cursor bootstrap =="
bash scripts/validate-cursor-bootstrap-v1.sh || fail "cursor-bootstrap"

echo "== 2/6 video ad factory =="
bash scripts/validate-video-ad-factory-chain-v1.sh || fail "video-ad-factory"

echo "== 3/6 MCP chain =="
lsof -ti:8787,8790 | xargs kill -9 2>/dev/null || true
bash scripts/validate-mcp-chain-e2e-v1.sh || fail "mcp-chain-e2e"

echo "== 4/6 super-fast hub =="
bash scripts/validate-super-fast-hub-v1.sh || fail "super-fast-hub"

echo "== 5/6 governance chain =="
python3 scripts/debug_e2e_governance_chain_v1.py || fail "governance-e2e"

echo "== 6/6 MCP motor =="
bash scripts/validate-mcp-chain-motor-v1.sh || fail "mcp-motor"

python3 - <<'PY' || fail "mcp-campus bootstrap wire"
import json
from pathlib import Path
reg = json.loads(Path("data/mcp-chain-campus-registries-v1.json").read_text())
cb = reg.get("cursor_bootstrap") or {}
assert cb.get("ledger") == "data/cursor-bootstrap-ledger-v1.json"
assert cb.get("validator") == "scripts/validate-cursor-bootstrap-v1.sh"
assert (reg.get("campuses") or {}).get("sourcea", {}).get("cursor_bootstrap_ledger")
print("OK: mcp-campus-registries cursor_bootstrap wired")
PY

if [[ "$FAIL" -ne 0 ]]; then exit 1; fi
echo "OK: validate-all-e2e-v1 · bootstrap · video-factory · MCP · hub · governance · motor"
