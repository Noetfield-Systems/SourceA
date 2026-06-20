#!/usr/bin/env bash
# Deprecated alias — use validate-goal1-auto-run-v1.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "$ROOT/scripts/validate-goal1-auto-run-v1.sh"
