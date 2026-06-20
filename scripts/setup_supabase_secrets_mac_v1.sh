#!/usr/bin/env bash
# setup_supabase_secrets_mac_v1.sh — scaffold ~/.sourcea-secrets for daily Supabase keepalive
# Founder: paste real SUPABASE_URL + SUPABASE_ANON_KEY from Supabase dashboard (never commit filled files)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SECRETS_DIR="${HOME}/.sourcea-secrets"
mkdir -p "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"

copy_if_missing() {
  local name="$1"
  local example="$2"
  local dest="$SECRETS_DIR/$name"
  if [[ -f "$dest" ]]; then
    echo "KEEP  $dest (already exists — edit in place if placeholders remain)"
    return 0
  fi
  cp "$example" "$dest"
  chmod 600 "$dest"
  echo "CREATE $dest from example — paste real keys from Supabase dashboard"
}

copy_if_missing "portfolio-spine.env" "$ROOT/infra/supabase/portfolio-spine/config.example.env"
copy_if_missing "labs-sandbox.env" "$ROOT/infra/supabase/labs-sandbox/config.example.env"

echo ""
echo "Next (founder only):"
echo "  1. Open Supabase → portfolio-spine project → Settings → API"
echo "  2. Paste SUPABASE_URL + SUPABASE_ANON_KEY into $SECRETS_DIR/portfolio-spine.env"
echo "  3. Repeat for labs-sandbox (VIRLUX) → $SECRETS_DIR/labs-sandbox.env"
echo "  4. Verify: bash $ROOT/scripts/run-portfolio-supabase-daily-v1.sh"
echo ""
echo "Law: secrets never in repo · agent DB keys labs-sandbox only"
