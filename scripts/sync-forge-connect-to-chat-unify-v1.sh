#!/usr/bin/env bash
# Sync Connect shell assets to chat-unify-standalone (parity :13023 ↔ :13029).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/apps/forge-terminal-connect-v1"
DST="${ROOT}/scripts/chat-unify-standalone"

for f in app.js app.css forge-connect.css forge-connect-boot.js forge-quality-bridge.js index.html; do
  if [[ -f "${SRC}/${f}" ]]; then
    cp "${SRC}/${f}" "${DST}/${f}"
  fi
done

echo "✓ Synced forge-terminal-connect-v1 → chat-unify-standalone ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
