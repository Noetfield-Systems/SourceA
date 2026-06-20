#!/usr/bin/env bash
# validate-mcp-chain-motor-v1.sh — P1 publish gate for sourcea-verify MCP
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
FAIL=0
fail() { echo "FAIL: validate-mcp-chain-motor — $*" >&2; FAIL=1; }

PKG="packages/mcp-sourcea-verify"
REG="$PKG/registry/server-v1.json"
PLUGIN="cursor-plugin/sourcea-forge-governance/plugin-v1.json"
PLUGIN_MANIFEST="cursor-plugin/sourcea-forge-governance/.cursor-plugin/plugin.json"
PLUGIN_MCP="cursor-plugin/sourcea-forge-governance/.mcp.json"
PLUGIN_README="cursor-plugin/sourcea-forge-governance/README.md"
DEMO="receipts/mcp-chain-consumer-demo.json"
SSOT="data/mcp-chain-campus-registries-v1.json"

[[ -f "$PKG/package.json" ]] || fail "missing mcp-sourcea-verify package.json"
[[ -f "$PKG/src/index.ts" ]] || fail "missing MCP server entry"
[[ -f "$REG" ]] || fail "missing registry server-v1.json"
[[ -f "$PLUGIN" ]] || fail "missing cursor plugin manifest"
[[ -f "$PLUGIN_MANIFEST" ]] || fail "missing .cursor-plugin/plugin.json (Card 1 bundle)"
[[ -f "$PLUGIN_MCP" ]] || fail "missing .mcp.json fragment"
[[ -f "$PLUGIN_README" ]] || fail "missing plugin README"
[[ -f "cursor-plugin/sourcea-forge-governance/skills/verify-after-mcp/SKILL.md" ]] || fail "missing verify-after-mcp skill"
[[ -f "cursor-plugin/sourcea-forge-governance/rules/receipt-native-governance.mdc" ]] || fail "missing receipt-native-governance rule"
[[ -f "scripts/publish_sourcea_forge_governance_card_v1.py" ]] || fail "missing publish card script"
[[ -f "$DEMO" ]] || fail "missing mcp-chain-consumer-demo.json"
[[ -f "$SSOT" ]] || fail "missing mcp-chain-campus-registries-v1.json"
[[ -f "scripts/mcp_chain_pick_v1.py" ]] || fail "missing mcp_chain_pick_v1.py"

python3 - <<'PY' || fail "registry metadata"
import json
from pathlib import Path
reg = json.loads(Path("packages/mcp-sourcea-verify/registry/server-v1.json").read_text())
assert "io.github.sinakazemnezhad/sourcea-verify" in reg["name"]
tools = {t["name"] for t in reg["tools"]}
for need in ("verify_run", "factory_status", "form_pick_parse", "emit_receipt_readonly"):
    assert need in tools, need
print("OK: registry metadata · 4 tools")
PY

if [[ -f "$PKG/dist/http-app.js" ]]; then
  echo "OK: mcp-sourcea-verify dist built (stdio + http)"
else
  echo "WARN: run npm run build in $PKG"
fi

SSE_URL="${SOURCEA_MCP_SSE_URL:-http://127.0.0.1:8787/health}"
if curl -sf "$SSE_URL" >/dev/null 2>&1; then
  echo "OK: SSE health $SSE_URL"
else
  echo "INFO: SSE not running — running local E2E..."
  bash scripts/validate-mcp-chain-e2e-v1.sh || fail "mcp-chain-e2e failed"
fi

[[ -f "data/mcp-chain-publish-receipt-v2.json" ]] || fail "missing mcp-chain-publish-receipt-v2 (run deploy_mcp_sse_v1.py)"
[[ -f "data/brain-cloud-practical-300-mcp-v1.json" ]] || fail "missing C300-MCP rows"

bash scripts/validate-cursor-bootstrap-v1.sh >/dev/null || fail "cursor-bootstrap pack"

if [[ "$FAIL" -ne 0 ]]; then exit 1; fi
echo "OK: validate-mcp-chain-motor-v1 · P1+P2 publish scaffold"
