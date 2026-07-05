#!/usr/bin/env bash
# Sync portfolio-spine secrets from ~/.sourcea-secrets → GitHub Actions repo secrets.
# Never echoes secret values.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="${GITHUB_REPO:-Noetfield-Systems/SourceA}"

command -v gh >/dev/null || { echo "FAIL: gh CLI required" >&2; exit 1; }

load_env_file() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  set -a
  # shellcheck disable=SC1090
  source "$f"
  set +a
}

load_env_file "${HOME}/.sourcea-secrets/portfolio-spine.env"
load_env_file "${HOME}/.sourcea-secrets/portfolio-spine-db.env"

if [[ -z "${SUPABASE_URL:-}" || -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
  echo "FAIL: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required in ~/.sourcea-secrets/portfolio-spine.env" >&2
  exit 1
fi

REF="${SUPABASE_PROJECT_ID:-}"
if [[ -z "$REF" ]]; then
  REF="$(python3 -c "import os,urllib.parse; u=os.environ.get('SUPABASE_URL',''); print((urllib.parse.urlparse(u).hostname or '').split('.')[0])")"
fi

if [[ -z "${SUPABASE_DB_URL:-}" && -n "${SUPABASE_DB_PASSWORD:-}" && -n "$REF" ]]; then
  ENC_PW="$(python3 -c "import os,urllib.parse; print(urllib.parse.quote(os.environ['SUPABASE_DB_PASSWORD'], safe=''))")"
  export SUPABASE_DB_URL="postgresql://postgres:${ENC_PW}@db.${REF}.supabase.co:5432/postgres?sslmode=require"
fi

set_secret() {
  local name="$1"
  local value="$2"
  if [[ -z "$value" ]]; then
    echo "SKIP: ${name} (empty)"
    return 0
  fi
  printf '%s' "$value" | gh secret set "$name" -R "$REPO"
  echo "OK: ${name}"
}

echo "Syncing GitHub Actions secrets → ${REPO}"

set_secret SUPABASE_URL "$SUPABASE_URL"
set_secret SUPABASE_SERVICE_ROLE_KEY "$SUPABASE_SERVICE_ROLE_KEY"
set_secret SUPABASE_ANON_KEY "${SUPABASE_ANON_KEY:-}"
set_secret SUPABASE_PROJECT_ID "${SUPABASE_PROJECT_ID:-$REF}"
set_secret SUPABASE_DB_PASSWORD "${SUPABASE_DB_PASSWORD:-}"
set_secret SUPABASE_DB_URL "${SUPABASE_DB_URL:-}"

for token_path in "${HOME}/.config/supabase/access-token" "${HOME}/.supabase/access-token"; do
  if [[ -z "${SUPABASE_ACCESS_TOKEN:-}" && -f "$token_path" ]]; then
    SUPABASE_ACCESS_TOKEN="$(tr -d '[:space:]' < "$token_path")"
  fi
done
set_secret SUPABASE_ACCESS_TOKEN "${SUPABASE_ACCESS_TOKEN:-}"

echo "DONE: github actions secrets synced from disk"
