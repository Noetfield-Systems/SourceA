#!/usr/bin/env bash
# N2/N3 scaffold — optional services on :13031/:13032 (not in default boot chain).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

bash "$ROOT/scripts/serve-hub-state-service.sh"
bash "$ROOT/scripts/serve-hub-agent-runtime.sh"

curl -sf "http://127.0.0.1:13031/health" >/dev/null
curl -sf "http://127.0.0.1:13031/api/queue" >/dev/null
curl -sf "http://127.0.0.1:13032/health" >/dev/null
curl -sf "http://127.0.0.1:13032/api/factory" >/dev/null

echo "OK: validate-hub-n2-n3-scaffold-v1 · State :13031 + Agent runtime :13032"
