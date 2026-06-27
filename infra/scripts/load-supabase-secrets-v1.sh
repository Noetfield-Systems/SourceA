#!/usr/bin/env bash
# Load Supabase env for one tier — secrets live outside the workspace.
set -euo pipefail

TIER="${1:-}"
SECRETS_DIR="${SOURCEA_SECRETS_DIR:-$HOME/.sourcea-secrets}"

usage() {
  echo "Usage: source infra/scripts/load-supabase-secrets-v1.sh <portfolio-spine|labs-sandbox|noetfield>" >&2
  return 1
}

case "$TIER" in
  portfolio-spine|labs-sandbox|noetfield) ;;
  *) usage ;;
esac

ENV_FILE="$SECRETS_DIR/$TIER.env"
DB_ENV_FILE="$SECRETS_DIR/${TIER}-db.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE — copy from infra/supabase/$TIER/config.example.env" >&2
  return 1
fi

set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

if [[ -f "$DB_ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$DB_ENV_FILE"
  set +a
fi

export SOURCEA_SUPABASE_TIER="$TIER"
echo "Loaded SOURCEA_SUPABASE_TIER=$TIER from $ENV_FILE"
[[ -f "$DB_ENV_FILE" ]] && echo "Loaded DB password from $DB_ENV_FILE"
