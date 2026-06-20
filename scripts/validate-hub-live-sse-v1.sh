#!/usr/bin/env bash
# Track 2 L1 — SSE live feed gate (curl/python, no browser).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

curl -sf "http://127.0.0.1:13020/health" >/dev/null || {
  echo "FAIL: hub :13020 not up"
  exit 1
}

# curl -N matches browser SSE; urllib read() blocks on single-thread hub until next flush.
SSE_SAMPLE="$(curl -N -m 5 -s -H "Accept: text/event-stream" "http://127.0.0.1:13020/api/live/v1" | head -c 4096 || true)"
if echo "$SSE_SAMPLE" | grep -q '"type": "live.connect"' \
  && echo "$SSE_SAMPLE" | grep -qE '"type": "live\.heartbeat"|"type": "hub\.generation"'; then
  echo "OK: SSE events received (live.connect + heartbeat/generation)"
else
  echo "FAIL: no SSE connect/heartbeat in sample:" >&2
  echo "$SSE_SAMPLE" | head -5 >&2
  exit 1
fi

echo "OK: validate-hub-live-sse-v1"
