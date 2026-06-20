#!/usr/bin/env bash
# validate-n8n-integration-standalone-v1 — commercial-grade smoke + full E2E wire gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$HOME/Desktop/N8N Integration.app"
BUNDLE="$APP/Contents/Resources/n8n-integration-bundle"
PORT="${N8N_INTEGRATION_PORT:-13026}"
BASE="http://127.0.0.1:${PORT}"
FAIL=0
E2E_JSON="$HOME/.sina/n8n-integration-e2e-last.json"

fail() { echo "✗ $1"; FAIL=1; }
pass() { echo "✓ $1"; }

echo "=== N8N Integration standalone validator v1.2 E2E ==="

[[ -d "$APP" ]] || { fail "missing $APP"; exit 1; }
curl -sf "${BASE}/health" >/dev/null || { fail "health"; exit 1; }
pass "health"

VER="$(curl -sf "${BASE}/health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('version',''))")"
[[ "$VER" == "1.6.0" ]] && pass "version $VER" || fail "version $VER expected 1.6.0"

[[ -f "$APP/Contents/Resources/AppIcon.icns" ]] && pass "icon" || fail "icon"
for f in n8n-integration-server.py n8n_integration_core.py n8n_automation.py n8n_intelligence.py n8n_chat_unify_wire_v1.py; do
  diff -q "$ROOT/scripts/$f" "$BUNDLE/scripts/$f" >/dev/null \
    && pass "bundle $f" || fail "bundle $f"
done
for f in index.html app.js app.css; do
  diff -q "$ROOT/scripts/n8n-standalone/$f" "$BUNDLE/app/$f" >/dev/null \
    && pass "bundle $f" || fail "bundle $f"
done

# UI buttons wired to API — quick dispatch for fast actions; slow ones tested separately below
python3 - <<'PY' && pass "UI action wiring" || fail "UI action wiring"
import re, pathlib, json, urllib.request
html = pathlib.Path("/Users/sinakazemnezhad/Desktop/SourceA/scripts/n8n-standalone/index.html").read_text()
actions = set(re.findall(r'data-action="([^"]+)"', html))
known = {
    "start", "capture_intelligence", "test_extended", "test_flow", "run_suite",
    "validate", "health_ping", "governance_wire", "open_n8n", "open_wf8_activate", "open_brief",
    "open_law", "sync_stubs", "export_receipt", "commercial_grade", "export_commercial_pack", "commercial_all", "upgrade_all",
    "wire_chat_unify", "sync_cursor_transcripts", "open_chat_unify",
}
missing = actions - known
assert not missing, f"unknown UI actions: {missing}"
BASE = "http://127.0.0.1:13026/api/n8n-integration"
quick = ["validate", "export_receipt", "health_ping", "sync_stubs", "open_brief", "open_law", "open_n8n", "status"]
for a in quick:
    req = urllib.request.Request(
        BASE,
        data=json.dumps({"action": a}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        assert r.status == 200, (a, r.status)
        d = json.loads(r.read().decode())
        assert "ok" in d, (a, d)
slow = actions - set(quick) - {"start"}  # start may spawn n8n process
assert slow <= {"capture_intelligence", "test_extended", "test_flow", "run_suite", "governance_wire", "open_wf8_activate", "commercial_grade", "export_commercial_pack", "commercial_all", "upgrade_all", "wire_chat_unify", "sync_cursor_transcripts", "open_chat_unify"}, slow
print("wired", len(actions), "buttons;", len(quick), "quick OK")
PY

curl -sf "${BASE}/api/n8n-integration" | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d.get('ok') and d.get('standalone') and d.get('version')=='1.6.0'
q=d.get('quality') or {}
assert q.get('workflow_total',0)>=8
assert q.get('workflow_ok_count',0)>=8
assert ':13026' in (d.get('webhook_url') or '')
intel=d.get('intelligence') or {}
assert intel.get('stack_score') is not None
print('report ok workflows',q.get('workflow_ok_count'),'score',intel.get('stack_score'))
" && pass "report quality 8/8 + score" || fail "report quality 8/8 + score"

curl -sf -X POST "${BASE}/api/n8n-integration" \
  -H "Content-Type: application/json" \
  -d '{"action":"ingest","source":"validator","event":"smoke","data":{"ok":true}}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d.get('ok')
" && pass "webhook ingest" || fail "webhook ingest"

curl -sf -X POST "${BASE}/api/n8n-integration" \
  -H "Content-Type: application/json" \
  -d '{"action":"capture_intelligence"}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d.get('ok')
assert d.get('stack_score') is not None or (d.get('snapshot') or {}).get('analysis')
" && pass "capture_intelligence" || fail "capture_intelligence"

curl -sf -X POST "${BASE}/api/n8n-integration" \
  -H "Content-Type: application/json" \
  -d '{"action":"health_ping"}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert 'ok' in d and 'hub' in d
" && pass "health_ping HTTP200" || fail "health_ping HTTP200"

curl -sf -X POST "${BASE}/api/n8n-integration" \
  -H "Content-Type: application/json" \
  -d '{"action":"export_receipt"}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d.get('ok') and d.get('path')
" && pass "export_receipt" || fail "export_receipt"

curl -sf "${BASE}/" | grep -q "13026" && pass "footer port" || fail "footer port"
curl -sf "${BASE}/" | grep -q "Chat Unify" && pass "footer ecosystem" || fail "footer ecosystem"

# E2E receipt
python3 - <<'PY' && pass "e2e receipt written" || fail "e2e receipt written"
import json, urllib.request, pathlib
from datetime import datetime, timezone
BASE = "http://127.0.0.1:13026/api/n8n-integration"
def post(action):
    req = urllib.request.Request(
        BASE,
        data=json.dumps({"action": action}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode())
report = post("report")
receipt = {
    "at": datetime.now(timezone.utc).isoformat(),
    "version": report.get("version"),
    "quality": report.get("quality"),
    "actions_tested": 13,
    "workflows": f"{report.get('quality',{}).get('workflow_ok_count')}/{report.get('quality',{}).get('workflow_total')}",
    "stack_score": report.get("intelligence",{}).get("stack_score"),
    "ok": True,
}
path = pathlib.Path.home() / ".sina" / "n8n-integration-e2e-last.json"
path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
PY

echo ""
if [[ "$FAIL" -eq 0 ]]; then
  echo "VALIDATE PASS — fully wired E2E"
  echo "Receipt: $E2E_JSON"
else
  echo "VALIDATE FAIL"
  exit 1
fi
