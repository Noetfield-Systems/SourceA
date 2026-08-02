#!/usr/bin/env bash
# validate-founder-reply-quality-loop-v1.sh — fast gate for founder-facing reply quality
set -euo pipefail
cd "$(dirname "$0")/.."

fail() { echo "FAIL: validate-founder-reply-quality-loop-v1 — $*" >&2; exit 1; }

test -f data/founder-reply-glossary-v1.json || fail "missing glossary"
test -f scripts/founder_reply_translator_v1.py || fail "missing translator"
test -f scripts/founder_reply_quality_loop_v1.py || fail "missing loop"

FOUNDER_MSG="agents repeat words without understanding me"

GOOD='You are saying agents repeat words without understanding you. That is the real problem. I added a machine loop that translates technical drafts into plain language and blocks replies that still have no meaning for you.'
python3 scripts/founder_reply_quality_loop_v1.py \
  --text "$GOOD" \
  --founder-message "$FOUNDER_MSG" \
  --json >/dev/null || fail "good reply should SHIP"

BAD='Language standard wired. Gate PASS. SSOT updated.'
if python3 scripts/founder_reply_quality_loop_v1.py --text "$BAD" --founder-message "$FOUNDER_MSG" --json >/dev/null 2>&1; then
  fail "parrot reply should REJECT"
fi

TECH='sites=RED; defer flag ON.'
python3 scripts/founder_reply_quality_loop_v1.py \
  --text "$TECH" \
  --founder-message "why is email blocked" \
  --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('ok'), r
assert r.get('verdict') in ('SHIP','SHIP_TRANSLATED'), r
t=r.get('founder_text','').lower()
assert 'block' in t or 'fail' in t or 'email' in t, r
" || fail "technical line should translate to meaningful founder text"

grep -q 'founder_reply_quality_loop' scripts/agentic_conduct_gate_v1.py || fail "conduct gate not wired"

echo "PASS: validate-founder-reply-quality-loop-v1"
