#!/usr/bin/env bash
# P0 WitnessBC ship gate — Screen Studio master → ingest → critic → unfreeze
set -euo pipefail
ROOT="$HOME/Desktop/SourceA"
exec python3 "$ROOT/scripts/commercial_film_ship_gate_v1.py" --lane witnessbc "$@"
