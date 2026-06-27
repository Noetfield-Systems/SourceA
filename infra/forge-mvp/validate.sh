#!/usr/bin/env bash
# Forge MVP phase validator — build + optional smoke
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export SOURCEA_ROOT="${SOURCEA_ROOT:-$ROOT}"
API_URL="${FORGE_CORE_API_URL:-http://127.0.0.1:13040}"
RUN_SMOKE="${RUN_SMOKE:-0}"

if [[ "${1:-}" == "--smoke" ]]; then
  RUN_SMOKE=1
fi

echo "[validate] phase 0 — build"
for pkg in forge-core forge-governance forge-worker forge-core-api; do
  echo "  build apps/$pkg"
  (cd "$ROOT/apps/$pkg" && npm run build)
done

echo "[validate] phase 0 — governance cli"
export PYTHONPATH="$ROOT/scripts"
echo '{"agent_id":"forge-worker-1","agent_role":"builder","action_type":"read_file","dry_run":true}' \
  | python3 "$ROOT/apps/forge-governance/service/govern_cli.py" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['status']=='ALLOW', d"

echo "[validate] phase 0 — vault keys"
node --input-type=module -e "
import { bootstrapForgeEnv, secretsReady } from '$ROOT/apps/forge-core/dist/env.js';
bootstrapForgeEnv();
if (!secretsReady()) throw new Error('no_llm_keys_in_vault');
console.log('  secrets_ready=true');
"

if [[ "$RUN_SMOKE" == "1" ]]; then
  if curl -sf "$API_URL/health" >/dev/null 2>&1; then
    echo "[validate] e2e smoke (api already running)"
    FORGE_CORE_API_URL="$API_URL" bash "$ROOT/infra/forge-mvp/smoke.sh"
  else
    echo "[validate] e2e smoke (start-local --smoke-only)"
    bash "$ROOT/infra/forge-mvp/start-local.sh" --smoke --smoke-only
  fi
fi

echo "[validate] PASS"
