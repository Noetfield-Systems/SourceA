#!/usr/bin/env bash
# run-portfolio-supabase-daily-v1.sh — one daily stay-up pulse (≤90s · read-only)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
python3 "$ROOT/scripts/portfolio_supabase_daily_pulse_v1.py" --wire --json
