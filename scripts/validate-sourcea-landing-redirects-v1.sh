#!/usr/bin/env bash
# validate-sourcea-landing-redirects-v1.sh — no 301 .html strip (CF Pages 308 loop poison)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 scripts/build_sourcea_vercel_output_v1.py --json >/dev/null
REDIR="$ROOT/SourceA-landing/green-unified/dist/_redirects"
test -f "$REDIR" || { echo "FAIL: missing dist/_redirects"; exit 1; }

if grep -E '\.html[[:space:]]+/[^[:space:]]+[[:space:]]+301' "$REDIR"; then
  echo "FAIL: 301 .html→clean rules cause Cloudflare Pages redirect loops"
  exit 1
fi

grep -q '/platform' "$REDIR" || grep -q '/start' "$REDIR" || {
  echo "FAIL: missing short alias rules in _redirects"
  exit 1
}

if grep -E '\.html[[:space:]]+/' "$REDIR" | grep -q ' 200'; then
  echo "WARN: html 200 rewrites present — may loop with CF Pretty URLs"
fi

echo "PASS: validate-sourcea-landing-redirects-v1 ($(wc -l < "$REDIR" | tr -d ' ') rules, no 301 poison)"
