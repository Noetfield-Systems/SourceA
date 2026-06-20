#!/usr/bin/env bash
# npm_publish_mcp_chain_v1.sh — founder tap after npm login (P1 step 043)
set -euo pipefail

echo "Pre-flight: npm whoami"
npm whoami

echo "Publishing @sourcea/mcp-verify..."
cd "$(dirname "$0")/../packages/mcp-sourcea-verify"
npm run build
npm publish --access public

echo "Publishing @virlux/mcp-verify-factory..."
cd "$(dirname "$0")/../../VIRLUX"
npm run build -w @virlux/mcp-verify-factory
npm publish -w @virlux/mcp-verify-factory --access public

echo "OK: both packages published — submit registry.modelcontextprotocol.io metadata next"
