#!/usr/bin/env bash
# Avatar pipeline — LinkedIn / social human layer (NOT WitnessBC hero)
set -euo pipefail
ROOT="$HOME/Desktop/SourceA"
LANE="${1:-linkedin}"
shift || true
exec python3 "$ROOT/scripts/avatar_pipeline_v1.py" --lane "$LANE" --json "$@"
