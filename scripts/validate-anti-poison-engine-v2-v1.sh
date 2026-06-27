#!/usr/bin/env bash
# Anti-Poison Engine v2 — fast scan (<=90s). Mac-safe validate-only.
set -euo pipefail
ROOT="${SOURCEA_ROOT:-$HOME/Desktop/SourceA}"
cd "$ROOT"
python3 scripts/anti_poison_engine_v2.py --tier fast --json
