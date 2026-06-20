#!/usr/bin/env bash
# validate-mcp-chain-e2e-v1.sh — local E2E: start servers · health · MCP initialize
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "validate-mcp-chain-e2e-v1.sh" "$ROOT"
VIRLUX_ROOT="$(cd "$ROOT/../VIRLUX" && pwd)"
SA_PORT="${SOURCEA_MCP_E2E_PORT:-8787}"
VLX_PORT="${VIRLUX_MCP_E2E_PORT:-8790}"
FAIL=0
fail() { echo "FAIL: mcp-chain-e2e — $*" >&2; FAIL=1; }

cleanup() {
  [[ -n "${SA_PID:-}" ]] && kill "$SA_PID" 2>/dev/null || true
  [[ -n "${VLX_PID:-}" ]] && kill "$VLX_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "== E2E build =="
cd "$ROOT/packages/mcp-sourcea-verify" && npm run build >/dev/null
cd "$VIRLUX_ROOT" && npm run build -w @virlux/mcp-verify-factory >/dev/null && npm run build -w @virlux/api >/dev/null

echo "== E2E start SourceA HTTP :$SA_PORT =="
PORT="$SA_PORT" SOURCEA_MCP_CLOUD=1 node "$ROOT/packages/mcp-sourcea-verify/dist/http-server.js" &
SA_PID=$!
sleep 2

echo "== E2E start VIRLUX API :$VLX_PORT =="
cd "$VIRLUX_ROOT/apps/api"
NODE_ENV=development PORT="$VLX_PORT" TRUST_PROXY=1 node dist/index.js &
VLX_PID=$!
sleep 3

health_json() {
  local url="$1"
  curl -sf --max-time 5 "$url" 2>/dev/null
}

SA_HEALTH="$(health_json "http://127.0.0.1:${SA_PORT}/health")" || fail "SourceA /health down"
echo "$SA_HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('ok') is True" || fail "SourceA health not ok"

VLX_HEALTH="$(health_json "http://127.0.0.1:${VLX_PORT}/mcp/health")" || fail "VIRLUX /mcp/health down"
echo "$VLX_HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('ok') is True" || fail "VIRLUX mcp health not ok"

mcp_init() {
  local url="$1"
  local raw
  raw="$(curl -sf --max-time 10 -X POST "$url" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"mcp-e2e","version":"1.0.0"}}}')"
  # Streamable HTTP returns SSE — extract first data: payload
  if echo "$raw" | grep -q '^data: '; then
    echo "$raw" | grep '^data: ' | head -1 | sed 's/^data: //'
  else
    echo "$raw"
  fi
}

SA_INIT="$(mcp_init "http://127.0.0.1:${SA_PORT}/mcp")" || fail "SourceA MCP initialize failed"
echo "$SA_INIT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'result' in d" 2>/dev/null || {
  echo "$SA_INIT" | head -c 400
  fail "SourceA MCP initialize bad response"
}

VLX_INIT="$(mcp_init "http://127.0.0.1:${VLX_PORT}/mcp")" || fail "VIRLUX MCP initialize failed"
echo "$VLX_INIT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'result' in d" 2>/dev/null || {
  echo "$VLX_INIT" | head -c 400
  fail "VIRLUX MCP initialize bad response"
}

if [[ "$FAIL" -ne 0 ]]; then
  echo "FAIL: mcp-chain-e2e — see errors above" >&2
  exit 1
fi
echo "OK: mcp-chain-e2e · SourceA :${SA_PORT} · VIRLUX :${VLX_PORT} · health + initialize"
