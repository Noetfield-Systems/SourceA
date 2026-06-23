#!/usr/bin/env bash
# Local preview — SourceA green-unified (run recipe + Agent Run server hint)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
bash "$ROOT/scripts/run-recipe.sh" --serve
