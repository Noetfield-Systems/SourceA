#!/usr/bin/env bash
# validate-mac-law-surfaces-e2e-v1.sh — from-scratch E2E: :8781 · :8780 · launchd · full chain
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "validate-mac-law-surfaces-e2e-v1.sh" "$ROOT"
LOG="${HOME}/.sina/mac-law-surfaces-e2e-v1.log"
RECEIPT="${HOME}/.sina/mac-law-surfaces-e2e-receipt-v1.json"
FAIL=0
fail() { echo "FAIL: mac-law-surfaces-e2e — $*" | tee -a "$LOG"; FAIL=1; }
ok() { echo "  OK  $*" | tee -a "$LOG"; }

mkdir -p "${HOME}/.sina"
: >"$LOG"
echo "=== mac-law-surfaces-e2e $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"

echo "--- Step 1: install / kick launchd ---" | tee -a "$LOG"
bash "$ROOT/scripts/install-mac-law-surfaces-launchd-v1.sh" >>"$LOG" 2>&1 || fail "launchd install"

echo "--- Step 2: launchd health ---" | tee -a "$LOG"
bash "$ROOT/scripts/validate-mac-law-surfaces-launchd-v1.sh" >>"$LOG" 2>&1 || fail "launchd validate"

echo "--- Step 3: cockpit URL probe ---" | tee -a "$LOG"
for spec in \
  "Mac Law|http://127.0.0.1:8781/|http://127.0.0.1:8781/api/mac-law/health" \
  "Routing Panel|http://127.0.0.1:8780/|http://127.0.0.1:8780/api/panel/health" \
  "Worker Hub|http://127.0.0.1:13020/|http://127.0.0.1:13020/health" \
  "Mac Health|http://127.0.0.1:13024/|http://127.0.0.1:13024/health"
do
  IFS='|' read -r name page health <<<"$spec"
  if curl -sf --max-time 5 "$health" >/dev/null 2>&1 && curl -sf --max-time 5 -o /dev/null "$page"; then
    ok "$name $page"
  else
    fail "$name $page (health $health)"
  fi
done

echo "--- Step 4: Mac Law surfaces API ---" | tee -a "$LOG"
python3 - <<'PY' >>"$LOG" 2>&1 || exit 1
import json, urllib.request
row = json.loads(urllib.request.urlopen("http://127.0.0.1:8781/api/mac-law/surfaces", timeout=8).read())
assert row.get("ok"), row
assert row.get("passed") == row.get("total"), row
for s in row.get("surfaces") or []:
    assert s.get("status") == "PASS", s
print("  OK  mac-law surfaces API", row.get("passed"), "/", row.get("total"))
PY
[[ $? -eq 0 ]] || fail "surfaces API"

echo "--- Step 5: full Mac Law + Routing E2E ---" | tee -a "$LOG"
MONO=""
for d in "$HOME/Desktop/SinaaiMonoRepo" "$HOME/Desktop/Noetfield/SinaaiMonoRepo"; do
  [[ -f "$d/scripts/verify-mac-law-routing-panel-e2e.sh" ]] && MONO="$d" && break
done
[[ -n "$MONO" ]] || fail "mono e2e script missing"
bash "$MONO/scripts/verify-mac-law-routing-panel-e2e.sh" >>"$LOG" 2>&1 || fail "verify-mac-law-routing-panel-e2e"

echo "--- Step 6: Mac Law mandatory gate ---" | tee -a "$LOG"
python3 "$ROOT/scripts/mac_law_mandatory_v1.py" --sync-receipt --enforce --json >>"$LOG" 2>&1 || true
bash "$ROOT/scripts/validate-mac-law-mandatory-v1.sh" >>"$LOG" 2>&1 || fail "mac-law-mandatory"

PASS_FLAG="False"
[[ $FAIL -eq 0 ]] && PASS_FLAG="True"

python3 - <<PY
import json
from datetime import datetime, timezone
from pathlib import Path
p = Path("$RECEIPT")
p.write_text(json.dumps({
    "schema": "mac-law-surfaces-e2e-receipt-v1",
    "saved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "ok": $PASS_FLAG,
    "urls": {
        "mac_law": "http://127.0.0.1:8781/",
        "routing_panel": "http://127.0.0.1:8780/",
        "hub": "http://127.0.0.1:13020/",
        "mac_health": "http://127.0.0.1:13024/",
    },
    "log": "$LOG",
}, indent=2) + "\n")
PY

if [[ $FAIL -eq 0 ]]; then
  echo "PASS: validate-mac-law-surfaces-e2e-v1"
  exit 0
fi
echo "=== FAIL — see $LOG ==="
exit 1
