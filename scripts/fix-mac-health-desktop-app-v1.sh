#!/usr/bin/env bash
# Rebuild Mac Health Guard — founder double-click only (no alias, no Terminal).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
bash "$ROOT/scripts/build-mac-health-standalone-app-v1.sh"
