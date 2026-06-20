#!/usr/bin/env bash
# run-portfolio-supabase-daily-v1.sh — daily stay-up: sites + Supabase + accounts + priority + fix plan
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
python3 "$ROOT/scripts/portfolio_supabase_daily_pulse_v1.py" --wire --json || true
python3 "$ROOT/scripts/portfolio_fix_plan_pulse_v1.py" --wire --json || true
python3 "$ROOT/scripts/portfolio_daily_priority_queue_v1.py" --wire --json || true
