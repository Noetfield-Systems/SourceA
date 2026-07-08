#!/usr/bin/env bash
# Cross-domain auth surface probe — Tier 0 public 200, auth routes present, contract SKUs ungated.
# SSOT: data/cross-domain-auth-surfaces-v1.json
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${BASE:-https://sourcea.app}"
FAIL=0

pass() { echo "OK $*"; }
fail() { echo "FAIL $*"; FAIL=1; }

check_200() {
  local url_path="$1"
  local label="${2:-$url_path}"
  local code
  code="$(curl -sS -o /dev/null -w '%{http_code}' "${BASE}${url_path}")"
  if [[ "$code" == "200" ]]; then
    pass "200 ${label}"
  else
    fail "${code} ${label}"
  fi
}

check_body() {
  local url_path="$1"
  local needle="$2"
  local label="${3:-$url_path}"
  local body
  body="$(curl -sS "${BASE}${url_path}")"
  if grep -qF "$needle" <<< "$body"; then
    pass "body ${label} · ${needle}"
  else
    fail "body ${label} missing · ${needle}"
  fi
}

echo "=== auth surfaces (${BASE}) ==="

# Tier 0 — must stay public (no login wall)
for p in "/" "/operating-brain-install" "/ai-value-governance" "/enterprise-ai-control-plane" "/eval" "/sourcea/pricing"; do
  check_200 "$p"
done

# Tier 1 — canonical auth routes
for p in "/auth/sign-in" "/auth/sign-up" "/auth/callback"; do
  check_200 "$p"
done

check_body "/auth/sign-in" "Sign in to SourceA"
check_body "/auth/sign-up" "Create your SourceA account"
check_body "/" "/auth/sign-in" "home header auth link"

# Auth config public (anon key only — no service role)
if curl -sS "${BASE}/sourcea/data/sourcea-platform-auth-config-v1.json" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('schema')=='sourcea-platform-auth-config-v1'
assert d.get('venture')=='sourcea'
assert d.get('configured') is True
assert 'service_role' not in json.dumps(d)
urls=d.get('redirect_urls') or []
assert any('auth/callback' in u for u in urls)
print('config ok')
"; then
  pass "auth config JSON"
else
  fail "auth config JSON"
fi

# Legacy forge routes still work
check_200 "/sourcea/forge/terminal/signin"
check_200 "/platform"

echo "=== summary ==="
if [[ "$FAIL" -eq 0 ]]; then
  echo "verify_auth_surfaces_e2e_v1.sh: ALL PASS"
  exit 0
fi
echo "verify_auth_surfaces_e2e_v1.sh: FAIL"
exit 1
