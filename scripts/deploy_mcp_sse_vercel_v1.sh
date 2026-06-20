#!/usr/bin/env bash
# deploy_mcp_sse_vercel_v1.sh — deploy SourceA MCP package to Vercel (founder tap)
set -euo pipefail
PKG="$(cd "$(dirname "$0")/../packages/mcp-sourcea-verify" && pwd)"
cd "$PKG"
echo "Deploying sourcea-mcp-verify from $PKG"
if command -v vercel >/dev/null 2>&1; then
  vercel --prod --yes
else
  npx vercel --prod --yes
fi
echo "Set env: SOURCEA_MCP_CLOUD=1 SOURCEA_HUB_URL=http://127.0.0.1:13020 SOURCEA_MCP_API_KEYS=<token>"
