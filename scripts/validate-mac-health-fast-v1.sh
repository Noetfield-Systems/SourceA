#!/usr/bin/env bash
# validate-mac-health-fast-v1.sh — alias → ship-fast (≤90s · Mac founder session default)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "$ROOT/scripts/validate-mac-health-ship-fast-v1.sh" "$@"
