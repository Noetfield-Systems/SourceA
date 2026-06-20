#!/usr/bin/env bash
# Quick probe — SourceA + WitnessBC Vercel deploy URLs
set -euo pipefail
FAIL=0
check() {
  local url="$1"
  local code body
  code="$(curl -sI -m 15 -o /dev/null -w '%{http_code}' "$url")"
  if [[ "$code" =~ ^2 ]]; then
    echo "PASS $code $url"
  else
    err="$(curl -sI -m 15 "$url" 2>/dev/null | rg -i '^x-vercel-error:' | head -1 | tr -d '\r' || true)"
    echo "FAIL $code $url${err:+ · $err}"
    FAIL=1
  fi
}
check "https://source-a.vercel.app/sourcea/"
check "https://source-a.vercel.app/sourcea/trust/"
check "https://deploy-witnessbc-agents-governance.vercel.app/"
exit "$FAIL"
