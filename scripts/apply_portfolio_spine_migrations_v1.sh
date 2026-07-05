#!/usr/bin/env bash
# Apply portfolio-spine migrations 002+005+006+007 — CI/cloud only (L4 + L16 + L17).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MIGRATIONS=(
  "$ROOT/infra/supabase/portfolio-spine/migrations/002_truth_log_v1.sql"
  "$ROOT/infra/supabase/portfolio-spine/migrations/005_truth_log_external_verify_v1.sql"
  "$ROOT/infra/supabase/portfolio-spine/migrations/006_mac_spine_bridge_v1.sql"
  "$ROOT/infra/supabase/portfolio-spine/migrations/007_agent_session_cost_v1.sql"
  "$ROOT/infra/supabase/portfolio-spine/migrations/012_gmail_inbox_signals_v1.sql"
  "$ROOT/infra/supabase/portfolio-spine/migrations/013_improvement_queue_v1.sql"
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
if [[ -z "$DB_URL" ]]; then
  echo "SKIP: no SUPABASE_DB_URL — ensure_truth_log_schema_v1.py applies via Supabase pooler (IPv4)"
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
  echo "OK: portfolio-spine migrations 002+005+006+007+013 applied"
else
  exit 0
fi
