#!/usr/bin/env bash
# Recover Forge Terminal — kill stale :13029, sync UI, rebuild .app
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${FORGE_TERMINAL_PORT:-13029}"

echo "→ Killing stale forge-terminal on :${PORT}…"
for pid in $(lsof -ti:"${PORT}" 2>/dev/null || true); do
  cmd=$(ps -p "$pid" -o command= 2>/dev/null || true)
  if echo "$cmd" | grep -q forge-terminal-server.py; then
    kill -9 "$pid" 2>/dev/null || true
  fi
done
sleep 0.5

echo "→ Sync forge-terminal-v1 → connect bundle…"
rsync -a "${ROOT}/apps/forge-terminal-v1/" "${ROOT}/apps/forge-terminal-connect-v1/terminal/"

echo "→ Rebuild Forge Terminal.app…"
bash "${ROOT}/scripts/build-forge-terminal-standalone-app-v1.sh" || true

echo "→ Smoke health (live UI)…"
FORGE_TERMINAL_PORT="${PORT}" FORGE_TERMINAL_USE_LIVE_UI=1 \
  python3 "${ROOT}/scripts/forge-terminal-server.py" >/dev/null 2>&1 &
SP=$!
for _ in $(seq 1 20); do
  if curl -sf "http://127.0.0.1:${PORT}/health" 2>/dev/null | grep -q forge-terminal; then
    echo "✓ Server OK on :${PORT}"
    kill "$SP" 2>/dev/null || true
    echo "✓ Done — Cmd+Q app, reopen from Desktop. Look for v4.11.12-living-chat-fast"
    exit 0
  fi
  sleep 0.5
done
kill "$SP" 2>/dev/null || true
echo "WARN: smoke health timeout — still try Cmd+Q and reopen app"
exit 0
