#!/usr/bin/env bash
# Local preview — Witness AI site (run recipe + http.server)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PORT:-8090}"
bash "$ROOT/scripts/run-recipe.sh" --serve
