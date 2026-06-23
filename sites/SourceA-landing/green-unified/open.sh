#!/usr/bin/env bash
# cwd-safe open — SourceA green-unified canonical landing
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
bash "$ROOT/scripts/run-recipe.sh" --open
