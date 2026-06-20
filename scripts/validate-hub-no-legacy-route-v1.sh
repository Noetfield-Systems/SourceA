#!/usr/bin/env bash
# validate-hub-no-legacy-route-v1.sh — /legacy/ retired (301 → /)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVER="$ROOT/scripts/sina-command-server.py"
BASE="${HUB_BASE:-http://127.0.0.1:13020}"

fail() { echo "FAIL: $*" >&2; exit 1; }

grep -q 'path.startswith("/assets/")' "$SERVER" || fail "server must block /assets/ monolith"
grep -q 'path == "/index.html"' "$SERVER" || fail "server must block /index.html monolith"

for p in /legacy/ /index.html /assets/app.js; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-redirs 0 "$BASE$p" || true)"
  test "$code" = "301" || fail "GET $p expected 301 got $code"
done

body="$(curl -s --max-redirs 0 "$BASE/assets/app.js" | head -c 40)"
echo "$body" | grep -qi 'Sina Command' && fail "/assets/app.js still serves monolith body"

grep -qi 'Founder Museum' "$ROOT/agent-control-panel/worker-hub/index.html" && \
  fail "H1 must not mention Founder Museum"

echo "OK validate-hub-no-legacy-route-v1"
