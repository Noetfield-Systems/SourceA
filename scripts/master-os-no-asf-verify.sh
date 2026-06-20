#!/usr/bin/env bash
# Master OS closeout (no ASF) — agent-verifiable gates only.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CURSOR_OS="$HOME/Desktop/Cursor OS Pro"
NOETFIELD="$HOME/Desktop/Noetfield"
FAIL=0

pass() { echo "PASS: $*"; }
fail() { echo "FAIL: $*"; FAIL=1; }

echo "==> Hub panel rebuild"
python3 "$ROOT/scripts/build-sina-command-panel.py"

echo "==> Hub UI grep (no inline Stop / emergency strip)"
if grep -rqE 'btn-emergency-stop-inline|renderEmergencyStrip' "$ROOT/agent-control-panel/" 2>/dev/null; then
  fail "inline Stop or renderEmergencyStrip still present"
else
  pass "no inline Stop / renderEmergencyStrip in agent-control-panel"
fi

if grep -q 'btn-emergency-stop-inline' "$ROOT/agent-control-panel/index.html" 2>/dev/null; then
  fail "index.html still has btn-emergency-stop-inline"
else
  pass "single top-bar Stop in index.html"
fi

if curl -sf http://127.0.0.1:13020/ >/dev/null 2>&1; then
  if curl -s http://127.0.0.1:13020/ | grep -qE 'btn-emergency-stop-inline|sc-emergency-strip'; then
    fail "served hub HTML still has duplicate stop/strip"
  else
    pass "hub :13020 serves clean HTML (hard-refresh browser if UI looks stale)"
  fi
else
  echo "WARN: hub not on :13020 — start Sina Command.app or serve-sina-command.sh"
fi

echo "==> Cursor OS Pro check"
if [[ -d "$CURSOR_OS" ]]; then
  (cd "$CURSOR_OS" && npm run check) && pass "npm run check" || fail "npm run check"
else
  fail "missing $CURSOR_OS"
fi

echo "==> n8n extended suite"
bash "$ROOT/scripts/validate-n8n.sh" && pass "n8n extended suite" || fail "n8n extended suite"

echo "==> Noetfield ops sync"
if [[ -x "$NOETFIELD/scripts/sync-sourceA-desktop.sh" ]]; then
  (cd "$NOETFIELD" && ./scripts/sync-sourceA-desktop.sh) && pass "sync-sourceA-desktop.sh"
  if [[ -f "$NOETFIELD/docs/ops/AGENT_READ_LINKS_LOCKED_v1.md" ]] \
    && grep -q 'SEMI_NOTICE_noetfield_cloud' "$NOETFIELD/docs/ops/AGENT_READ_LINKS_LOCKED_v1.md"; then
    pass "docs/ops semi-notice index"
  else
    fail "docs/ops AGENT_READ_LINKS missing cloud semi-notice"
  fi
else
  fail "Noetfield sync script missing"
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "==> One or more gates FAILED"
  exit 1
fi
echo "==> All agent gates PASS (operator: iPhone Phase 1, TestFlight/EAS, merge Noetfield PR if ops diff exists)"
