#!/usr/bin/env bash
# Deprecated — use witnessbc-site run recipe
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "WitnessBC-landing is deprecated → witnessbc-site/"
bash "$ROOT/witnessbc-site/scripts/run-recipe.sh" --open
