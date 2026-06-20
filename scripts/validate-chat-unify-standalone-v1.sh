#!/usr/bin/env bash
# validate-chat-unify-standalone-v1 — commercial-grade smoke gate (UI 3.4 + ORD rules)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$HOME/Desktop/Chat Unify.app"
BUNDLE="$APP/Contents/Resources/chat-unify-bundle"
PORT="${CHAT_UNIFY_PORT:-13023}"
BASE="http://127.0.0.1:${PORT}"
EXPECTED_UI="${CHAT_UNIFY_UI_VERSION:-3.4.0}"
FAIL=0

fail() { echo "✗ $1"; FAIL=1; }
pass() { echo "✓ $1"; }

bash "$ROOT/scripts/serve-chat-unify.sh" >/dev/null 2>&1 || true
sleep 1

for _ in {1..12}; do
  if curl -sf "${BASE}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

curl -sf "${BASE}/health" >/dev/null || { fail "health unreachable"; exit 1; }
pass "health"

VER="$(curl -sf "${BASE}/health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ui_version',''))")"
[[ "$VER" == "$EXPECTED_UI" ]] && pass "ui_version $VER" || fail "ui_version $VER expected $EXPECTED_UI"

FEAT="$(curl -sf "${BASE}/health" | python3 -c "import sys,json; print('live_http_verify' in json.load(sys.stdin).get('features',[]))")"
[[ "$FEAT" == "True" ]] && pass "live_http_verify feature" || fail "live_http_verify feature missing"

if [[ -d "$BUNDLE/scripts" ]]; then
  for f in chat_ord_claim_rules_v1.py chat_unify_live_http_verify_v1.py; do
    diff -q "$ROOT/scripts/$f" "$BUNDLE/scripts/$f" >/dev/null \
      && pass "bundle $f" || fail "bundle $f drift"
  done
  if [[ -f "$BUNDLE/data/chat-unify-ord-claim-rules-v1.json" ]]; then
    diff -q "$ROOT/data/chat-unify-ord-claim-rules-v1.json" "$BUNDLE/data/chat-unify-ord-claim-rules-v1.json" >/dev/null \
      && pass "bundle rules JSON" || fail "bundle rules JSON drift"
  else
    fail "bundle rules JSON missing"
  fi
  diff -q "$ROOT/scripts/chat-unify-standalone/app.js" "$BUNDLE/app/app.js" >/dev/null \
    && pass "bundle app.js" || fail "bundle app.js drift"
fi

bash "$ROOT/scripts/validate-chat-unify-ord-rules-v1.sh" && pass "ORD rules validator" || fail "ORD rules validator"

curl -sf -X POST "${BASE}/api/chat-unify" -H 'Content-Type: application/json' -d '{"action":"report"}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok'), d" \
  && pass "report API" || fail "report API"

[[ "$FAIL" -eq 0 ]] && echo "VALIDATE PASS" || { echo "VALIDATE FAIL"; exit 1; }
