#!/usr/bin/env bash
# Apply portfolio-spine migrations 002+005+006+007 — CI/cloud only (L4 + L16 + L17).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MIGRATIONS=(
  "$ROOT/infra/supabase/portfolio-spine/migrations/002_truth_log_v1.sql"
  "$ROOT/infra/supabase/portfolio-spine/migrations/005_truth_log_external_verify_v1.sql"
  "$ROOT/infra/supabase/portfolio-spine/migrations/006_mac_spine_bridge_v1.sql"
  "$ROOT/infra/supabase/portfolio-spine/migrations/007_agent_session_cost_v1.sql"
)

for SQL in "${MIGRATIONS[@]}"; do
  if [[ ! -f "$SQL" ]]; then
    echo "FAIL: missing $SQL" >&2
    exit 1
  fi
done

if [[ -f "${ENV:-$HOME/.sourcea-secrets/portfolio-spine.env}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV:-$HOME/.sourcea-secrets/portfolio-spine.env}"
  set +a
fi

DB_URL="${SUPABASE_DB_URL:-${DATABASE_URL:-}}"
if [[ -z "$DB_URL" && -n "${SUPABASE_DB_PASSWORD:-}" && -n "${SUPABASE_PROJECT_ID:-}" ]]; then
  export PGPASSWORD="$SUPABASE_DB_PASSWORD"
  DB_URL="postgresql://postgres@db.${SUPABASE_PROJECT_ID}.supabase.co:5432/postgres?sslmode=require"
  echo "INFO: built direct DB URL from SUPABASE_DB_PASSWORD + SUPABASE_PROJECT_ID"
fi
if [[ -z "$DB_URL" ]]; then
  echo "SKIP: no SUPABASE_DB_URL — apply migrations via Supabase SQL editor or ensure_truth_log_schema_v1.py"
  exit 0
fi

for SQL in "${MIGRATIONS[@]}"; do
  psql "$DB_URL" -v ON_ERROR_STOP=1 -f "$SQL"
done
psql "$DB_URL" -v ON_ERROR_STOP=1 -c "NOTIFY pgrst, 'reload schema';"
echo "OK: portfolio-spine migrations 002+005+006+007 applied"
