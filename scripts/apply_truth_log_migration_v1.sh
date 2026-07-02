#!/usr/bin/env bash
# Apply truth_log external-verify migration (portfolio-spine) — CI/cloud only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SQL="$ROOT/infra/supabase/portfolio-spine/migrations/005_truth_log_external_verify_v1.sql"
ENV="${HOME}/.sourcea-secrets/portfolio-spine.env"

if [[ ! -f "$SQL" ]]; then
  echo "FAIL: missing $SQL" >&2
  exit 1
fi

if [[ -f "$ENV" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV"
  set +a
fi

DB_URL="${SUPABASE_DB_URL:-${DATABASE_URL:-}}"
if [[ -z "$DB_URL" ]]; then
  echo "SKIP: no SUPABASE_DB_URL — apply $SQL via Supabase SQL editor or supabase db push"
  exit 0
fi

psql "$DB_URL" -v ON_ERROR_STOP=1 -f "$SQL"
echo "OK: truth_log migration 005 applied"
