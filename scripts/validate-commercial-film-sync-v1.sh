#!/usr/bin/env bash
set -euo pipefail
ROOT="$HOME/Desktop/SourceA"
exec python3 "$ROOT/scripts/validate_commercial_film_sync_v1.py" "$@"
