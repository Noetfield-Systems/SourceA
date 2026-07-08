#!/usr/bin/env bash
# deploy_noos_loop_executor_fly_v1.sh — Fly noos-loop-executor (bounded POST /loop)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$ROOT/cloud/noos-loop-executor-fly.toml"

command -v fly >/dev/null 2>&1 || { echo "FAIL: fly CLI required" >&2; exit 1; }
[[ -f "$CONFIG" ]] || { echo "FAIL: missing $CONFIG" >&2; exit 1; }

if [[ -z "${NOOS_LOOP_SECRET:-}" ]]; then
  echo "WARN: NOOS_LOOP_SECRET not set — set before deploy: fly secrets set NOOS_LOOP_SECRET=..." >&2
fi

cd "$ROOT"
fly deploy --config "$CONFIG" --ha=false

BASE="${NOOS_LOOP_EXECUTOR_URL:-https://noos-loop-executor.fly.dev}"
echo "== Fly health =="
curl -sf "$BASE/health" | python3 -m json.tool || echo "WARN: set NOOS_LOOP_EXECUTOR_URL if app name differs"

echo "DONE: deploy_noos_loop_executor_fly_v1 — run validate with:"
echo "  NOOS_LOOP_EXECUTOR_URL=$BASE NOOS_LOOP_SECRET=<secret> bash scripts/validate-noos-loop-executor-v1.sh"
