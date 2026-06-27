#!/usr/bin/env bash
# Forge MVP — one-shot local start (no Docker required)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export SOURCEA_ROOT="${SOURCEA_ROOT:-$ROOT}"
export FORGE_GOVERNANCE_DRY_RUN="${FORGE_GOVERNANCE_DRY_RUN:-true}"

API_PORT="${FORGE_CORE_API_PORT:-13040}"
API_URL="http://127.0.0.1:${API_PORT}"
SMOKE_ONLY=0

for arg in "$@"; do
  case "$arg" in
    --smoke-only) SMOKE_ONLY=1 ;;
  esac
done

PACKAGES=(forge-core forge-governance forge-worker forge-core-api)

build_all() {
  for pkg in "${PACKAGES[@]}"; do
    if [[ ! -f "$ROOT/apps/$pkg/dist/index.js" && ! -f "$ROOT/apps/$pkg/dist/service/govern.js" ]]; then
      echo "[start] build apps/$pkg"
      (cd "$ROOT/apps/$pkg" && npm install && npm run build)
    else
      (cd "$ROOT/apps/$pkg" && npm run build >/dev/null)
    fi
  done
}

stop_stale_forge() {
  if command -v lsof >/dev/null 2>&1; then
    local pids
    pids="$(lsof -ti ":${API_PORT}" 2>/dev/null || true)"
    if [[ -n "$pids" ]]; then
      echo "[start] freeing port ${API_PORT}"
      echo "$pids" | xargs kill -9 2>/dev/null || true
      sleep 1
    fi
  fi
}

wait_for_redis() {
  for _ in $(seq 1 90); do
    if python3 -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('127.0.0.1',6379)); s.close()" 2>/dev/null; then
      return 0
    fi
    sleep 1
  done
  echo "[start] FAIL redis not ready on 127.0.0.1:6379"
  return 1
}

wait_for_health() {
  for _ in $(seq 1 30); do
    if curl -sf "$API_URL/health" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get('service')=='forge-core-api' else 1)" 2>/dev/null; then
      return 0
    fi
    sleep 1
  done
  echo "[start] FAIL api health timeout on $API_URL"
  return 1
}

cleanup() {
  [[ -n "${WORKER_PID:-}" ]] && kill "$WORKER_PID" 2>/dev/null || true
  [[ -n "${API_PID:-}" ]] && kill "$API_PID" 2>/dev/null || true
  [[ -n "${REDIS_PID:-}" ]] && kill "$REDIS_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

stop_stale_forge
build_all

echo "[start] redis (embedded — no Docker)"
node "$ROOT/apps/forge-core/dist/ensure-redis-cli.js" &
REDIS_PID=$!
wait_for_redis
export FORGE_EMBEDDED_REDIS=0
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379}"

echo "[start] worker"
(cd "$ROOT/apps/forge-worker" && npm run start) &
WORKER_PID=$!
sleep 2

echo "[start] api"
(cd "$ROOT/apps/forge-core-api" && npm run start) &
API_PID=$!

wait_for_health
echo "[start] api ready at $API_URL"

if [[ "${1:-}" == "--smoke" || "${2:-}" == "--smoke" || "${RUN_SMOKE:-}" == "1" ]]; then
  FORGE_CORE_API_URL="$API_URL" bash "$ROOT/infra/forge-mvp/smoke.sh"
  echo "[start] smoke PASS"
  if [[ "$SMOKE_ONLY" == "1" ]]; then
    exit 0
  fi
  echo "[start] services running — Ctrl+C to stop"
fi

wait
