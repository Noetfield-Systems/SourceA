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
  DB_HOST="db.${SUPABASE_PROJECT_ID}.supabase.co"
  DB_IPV4=""
  if command -v getent >/dev/null 2>&1; then
    DB_IPV4="$(getent ahostsv4 "$DB_HOST" 2>/dev/null | awk '{print $1; exit}' || true)"
  fi
  if [[ -z "$DB_IPV4" ]] && command -v dig >/dev/null 2>&1; then
    DB_IPV4="$(dig +short A "$DB_HOST" 2>/dev/null | head -1 || true)"
  fi
  if [[ -n "$DB_IPV4" ]]; then
    DB_URL="postgresql://postgres@${DB_HOST}:5432/postgres?sslmode=require&hostaddr=${DB_IPV4}"
  else
    DB_URL="postgresql://postgres@${DB_HOST}:5432/postgres?sslmode=require"
  fi
  echo "INFO: built direct DB URL from SUPABASE_DB_PASSWORD + SUPABASE_PROJECT_ID (IPv4=${DB_IPV4:-auto})"
fi
if [[ -z "$DB_URL" ]]; then
  echo "SKIP: no SUPABASE_DB_URL — apply migrations via Supabase SQL editor or ensure_truth_log_schema_v1.py"
  exit 0
fi

PSQL_OK=1
for SQL in "${MIGRATIONS[@]}"; do
  if ! psql "$DB_URL" -v ON_ERROR_STOP=1 -f "$SQL"; then
    PSQL_OK=0
    echo "WARN: psql failed on $(basename "$SQL") — ensure_truth_log_schema_v1.py will retry" >&2
    break
  fi
done
if [[ "$PSQL_OK" -eq 1 ]]; then
  psql "$DB_URL" -v ON_ERROR_STOP=1 -c "NOTIFY pgrst, 'reload schema';"
  echo "OK: portfolio-spine migrations 002+005+006+007 applied"
else
  exit 0
fi
