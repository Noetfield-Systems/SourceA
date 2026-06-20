#!/usr/bin/env bash
# validate-chat-unify-standalone-v1 — commercial-grade smoke gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$HOME/Desktop/Chat Unify.app"
BUNDLE="$APP/Contents/Resources/chat-unify-bundle"
PORT="${CHAT_UNIFY_PORT:-13023}"
BASE="http://127.0.0.1:${PORT}"
FAIL=0

fail() { echo "✗ $1"; FAIL=1; }
pass() { echo "✓ $1"; }

[[ -d "$APP" ]] || { fail "missing $APP"; exit 1; }
curl -sf "${BASE}/health" >/dev/null || { fail "health"; exit 1; }
pass "health"

VER="$(curl -sf "${BASE}/health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('version',''))")"
[[ "$VER" == "1.3.0" ]] && pass "version $VER" || fail "version $VER expected 1.3.0"

[[ -f "$APP/Contents/Resources/AppIcon.icns" ]] && pass "icon" || fail "icon"
for f in chat_unify_merge.py chat-unify-server.py; do
  diff -q "$ROOT/scripts/$f" "$BUNDLE/scripts/$f" >/dev/null \
    && pass "bundle $f" || fail "bundle $f"
done
diff -q "$ROOT/scripts/chat-unify-standalone/app.js" "$BUNDLE/app/app.js" >/dev/null \
  && pass "bundle app.js" || fail "bundle app.js"

curl -sf -X POST "${BASE}/api/chat-unify" -H 'Content-Type: application/json' -d '{"action":"report"}' \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
assert d.get('version')=='1.3.0'
assert len(d.get('extracts') or [])>=1
wc=(d.get('quality') or {}).get('weak_count',99)
assert wc==0, f'weak_count={wc}'
print('report ok extracts',len(d.get('extracts') or []),'weak',wc)
" && pass "report quality" || fail "report quality"

export CHAT_UNIFY_PORT="${PORT}"
python3 - <<PY && pass "save dedupe roundtrip" || fail "save dedupe roundtrip"
import json, os, urllib.request
BASE = f"http://127.0.0.1:{os.environ.get('CHAT_UNIFY_PORT', '13023')}"
text = """# CHAT EXTRACT
## Decisions
- Validator dedupe · YES · smoke
## Threads
- QA · open
## Archive recommendation
NO"""

def post(body):
    req = urllib.request.Request(
        f"{BASE}/api/chat-unify",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

s1 = post({"action": "save_extract", "label": "Validator dedupe", "text": text})
assert s1["ok"] and s1["extract"]["id"]
s2 = post({"action": "save_extract", "label": "Validator dedupe again", "text": text})
assert s2.get("duplicate") and s2.get("skipped")
post({"action": "delete_extract", "id": s1["extract"]["id"]})
PY

curl -sf -X POST "${BASE}/api/chat-unify" -H 'Content-Type: application/json' -d '{"action":"unify"}' \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
cc=d.get('contradiction_count',-1)
assert cc==len(d.get('contradictions') or []), (cc, len(d.get('contradictions') or []))
print('unify ok contradictions',cc)
" && pass "unify contradictions" || fail "unify contradictions"

curl -sf -X POST "${BASE}/api/chat-unify" -H 'Content-Type: application/json' -d '{"action":"list_extracts"}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok') and d.get('count',0)>=1" \
  && pass "list_extracts alias" || fail "list_extracts alias"

curl -sf -X POST "${BASE}/api/chat-unify" -H 'Content-Type: application/json' -d '{"action":"import_latest"}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok')" \
  && pass "import_latest alias" || fail "import_latest alias"

[[ "$FAIL" -eq 0 ]] && echo "VALIDATE PASS" || { echo "VALIDATE FAIL"; exit 1; }
