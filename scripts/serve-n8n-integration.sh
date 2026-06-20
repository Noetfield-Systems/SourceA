#!/usr/bin/env bash
# N8N Integration — standalone mini app (:13026). Does NOT start Sina Command hub.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${N8N_INTEGRATION_PORT:-13026}"
unset N8N_INTEGRATION_BUNDLE_ROOT
export SINA_SOURCE_A="${SINA_SOURCE_A:-$ROOT}"
export N8N_INTEGRATION_STANDALONE=1
export N8N_INTEGRATION_PORT="$PORT"
exec python3 "$ROOT/scripts/n8n-integration-server.py"
