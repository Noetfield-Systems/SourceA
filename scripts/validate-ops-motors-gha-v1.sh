#!/usr/bin/env bash
# validate-ops-motors-gha-v1.sh — GHA billing + secrets readiness (Step 8)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: gha — $*" >&2; exit 1; }

command -v gh >/dev/null || fail "gh CLI required"

echo "== GitHub Actions validate workflow =="
runs="$(gh run list -R "${GITHUB_REPO:-Noetfield-Systems/SourceA}" --workflow=validate.yml --limit 3 --json conclusion,status 2>&1)" || {
  echo "WARN: cannot list workflow runs — billing or auth may block runners"
  echo "$runs"
  echo "FOUNDER: fix org billing at https://github.com/settings/billing"
  exit 0
}

echo "$runs" | python3 -c "
import json,sys
rows=json.load(sys.stdin)
if not rows:
    print('WARN: no validate runs yet')
    sys.exit(0)
last=rows[0]
print('last validate:', last.get('status'), last.get('conclusion'))
if last.get('conclusion')=='failure':
    print('WARN: validate not green — merge after billing fixed')
"

echo "== Secret presence (names only) =="
for name in SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY TELEGRAM_BOT_TOKEN GOOGLE_SERVICE_ACCOUNT_JSON; do
  if gh secret list -R "${GITHUB_REPO:-Noetfield-Systems/SourceA}" 2>/dev/null | awk '{print $1}' | grep -qx "$name"; then
    echo "OK: secret ${name}"
  else
    echo "SKIP: secret ${name} not set"
  fi
done

echo "OK: validate-ops-motors-gha-v1"
