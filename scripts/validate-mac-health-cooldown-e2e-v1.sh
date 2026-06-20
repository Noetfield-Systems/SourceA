#!/usr/bin/env bash
# Mac Health Cool Down E2E — local :13024
# Default: fast wire + cached read-only (~15s). --invoke-cooldown runs relief actions. --full adds scan/heal.
set -euo pipefail
PORT="${MAC_HEALTH_PORT:-13024}"
BASE="http://127.0.0.1:${PORT}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
SINA="${HOME}/.sina"
LIVE_CACHE="${SINA}/mac-health/live-pulse-v1.json"

INVOKE=0
FULL=0
RESTART=0
for arg in "$@"; do
  case "$arg" in
    --invoke-cooldown) INVOKE=1 ;;
    --full) FULL=1; INVOKE=1 ;;
    --restart) RESTART=1 ;;
  esac
done

fail=0
started=$(date +%s)

log() { echo "$@" ; }

ensure_heart() {
  if [[ "$RESTART" -eq 1 ]]; then
    log "→ restart Mac Health server…"
    pkill -f 'mac-health-guard-server.py' 2>/dev/null || true
    sleep 0.5
    bash "$ROOT/scripts/serve-mac-health-guard.sh" >/dev/null || true
  fi
  curl -sf --max-time 5 "${BASE}/health" >/dev/null || {
    log "→ heart down — starting Mac Health Guard…"
    bash "$ROOT/scripts/serve-mac-health-guard.sh" >/dev/null || true
  }
  curl -sf --max-time 5 "${BASE}/health" >/dev/null || {
    log "FAIL: heart down on :${PORT} — open Mac Health Guard.app"
    exit 1
  }
}

load_live_json() {
  local body
  body=$(curl -sf --max-time 12 "${BASE}/api/mac-health/live" 2>/dev/null || echo '{"ok":false}')
  local ok
  ok=$(python3 -c "import json,sys; d=json.load(sys.stdin); cs=d.get('cursor_session') or {}; print('true' if d.get('ok') is not False and cs.get('founder_line') else 'false')" <<<"$body")
  if [[ "$ok" == "true" ]]; then
    echo "$body"
    return 0
  fi
  if [[ -f "$LIVE_CACHE" ]]; then
    python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$LIVE_CACHE" 2>/dev/null && cat "$LIVE_CACHE" && return 0
  fi
  echo "$body"
}

check_post() {
  local name="$1"
  local action="$2"
  local timeout="${3:-90}"
  log "→ ${name} POST ${action} (${timeout}s max)…"
  local body
  body=$(curl -sf --max-time "$timeout" -X POST "${BASE}/api/mac-health" \
    -H "Content-Type: application/json" \
    -d "{\"action\":\"${action}\",\"standalone\":true}" 2>/dev/null || echo '{"ok":false,"error":"timeout_or_unreachable"}')
  local ok
  ok=$(python3 -c "import json,sys; d=json.load(sys.stdin); print('true' if d.get('ok') is not False else 'false')" <<<"$body")
  if [[ "$ok" != "true" ]]; then
    err=$(python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('error','')[:80])" <<<"$body" 2>/dev/null || echo "")
    log "FAIL: $name ($action) ${err:+$err}"
    fail=1
  else
    log "PASS: $name"
  fi
}

ensure_heart
ver=$(curl -sf --max-time 5 "${BASE}/health" | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))")
html=$(curl -sf --max-time 5 "${BASE}/")
log "Mac Health v${ver}"
log "=== UI (founder-glance v3.3) ==="

bash "$ROOT/scripts/validate-mac-health-founder-glance-v1.sh" && log "PASS: founder-glance SSOT UI" || { log "FAIL: founder-glance SSOT UI"; fail=1; }

for needle in "btn-cool-down" "cpu_cool_down" "panel-more" "panel-settings" "log-shield" "hub-truth-badge" "btn-ram-purge" "ram-truth-live"; do
  if ! grep -q "$needle" <<<"$html"; then
    log "FAIL: UI missing $needle (More disclosure / hidden compat)"
    fail=1
  fi
done
[[ $fail -eq 0 ]] && log "PASS: Cool down + settings + log shield in founder-glance More"

log "=== Cool down wire (static) ==="
grep -q 'data-action="cpu_cool_down"' "$ROOT/scripts/mac-health-standalone/index.html" \
  && grep -q 'cpu_cool_down' "$ROOT/scripts/mac_health_cpu_relief_v1.py" \
  && log "PASS: Cool down button → cpu_cool_down backend" \
  || { log "FAIL: Cool down button wire"; fail=1; }

for action in cpu_clear_ghosts cpu_clear_pipeline cpu_kill_scripts; do
  if grep -q "$action" "$ROOT/scripts/mac_health_cpu_relief_v1.py"; then
    log "PASS: backend wired $action"
  else
    log "FAIL: backend missing $action in cpu_relief"
    fail=1
  fi
done

if grep -q 'auto_guard_explainer' "$ROOT/scripts/mac_health_guard.py" \
  && grep -q 'settings_schema' "$ROOT/scripts/mac_health_guard.py" \
  && grep -q 'cpu_warn_state' "$ROOT/scripts/mac_health_guard.py"; then
  log "PASS: report payload fields present in engine"
else
  log "FAIL: report payload fields missing in engine"
  fail=1
fi

log "=== API (read-only, cached) ==="
log "→ live pulse (disk cache or GET 12s)…"
live=$(load_live_json)
live_ok=$(python3 -c "import json,sys; d=json.load(sys.stdin); print('true' if d.get('ok') is not False else 'false')" <<<"$live")
if [[ "$live_ok" != "true" ]]; then
  if [[ "$RESTART" -eq 0 ]]; then
    RESTART=1
    ensure_heart
    live=$(load_live_json)
    live_ok=$(python3 -c "import json,sys; d=json.load(sys.stdin); print('true' if d.get('ok') is not False else 'false')" <<<"$live")
  fi
fi
[[ "$live_ok" == "true" ]] && log "PASS: live pulse" || { log "FAIL: live pulse unavailable"; fail=1; }

has_live=$(python3 -c "import json,sys; d=json.load(sys.stdin); mp=d.get('machine_pressure') or {}; rt=mp.get('ram_truth') or {}; print('yes' if d.get('ok') and d.get('security_score') is not None and d.get('score') is not None and rt.get('ok') else 'no')" <<<"$live")
[[ "$has_live" == "yes" ]] && log "PASS: live score + ram_truth" || { log "FAIL: live missing score or ram_truth"; fail=1; }

has_sa=$(python3 -c "import json,sys; d=json.load(sys.stdin); sa=d.get('stranger_agent') or {}; print('yes' if sa.get('one_line') else 'no')" <<<"$live")
[[ "$has_sa" == "yes" ]] && log "PASS: live stranger_agent wired" || { log "FAIL: live stranger_agent one_line"; fail=1; }

has_cs=$(python3 -c "import json,sys; d=json.load(sys.stdin); cs=d.get('cursor_session') or {}; print('yes' if cs.get('founder_line') else 'no')" <<<"$live")
[[ "$has_cs" == "yes" ]] && log "PASS: live cursor_session wired" || { log "FAIL: live cursor_session"; fail=1; }

log "→ settings_save round-trip (20s max)…"
save_body=$(curl -sf --max-time 20 -X POST "${BASE}/api/mac-health" \
  -H "Content-Type: application/json" \
  -d '{"action":"settings_save","standalone":true,"settings":{"chrome":{"quit_on_cool_down_mode":"when_mac_hot"}}}' 2>/dev/null || echo '{"ok":false}')
save_ok=$(python3 -c "import json,sys; d=json.load(sys.stdin); ch=(d.get('values') or {}).get('chrome') or {}; print('yes' if d.get('ok') and ch.get('quit_on_cool_down_mode')=='when_mac_hot' else 'no')" <<<"$save_body")
[[ "$save_ok" == "yes" ]] && log "PASS: settings_save round-trip" || { log "FAIL: settings_save round-trip"; fail=1; }

if grep -q 'run_ram_purge' "$ROOT/scripts/mac_health_guard.py" && grep -q 'btn-ram-purge' "$ROOT/scripts/mac-health-standalone/index.html"; then
  log "PASS: ram_purge action wired (not invoked — needs password)"
else
  log "FAIL: ram_purge action not wired"
  fail=1
fi

if [[ "$INVOKE" -eq 1 ]]; then
  log "=== Cool down invoke (--invoke-cooldown) ==="
  log "NOTE: relief actions can take 1–3 minutes each on a busy Mac"
  check_post "cpu_cool_down" "cpu_cool_down" 180
  check_post "cpu_clear_ghosts" "cpu_clear_ghosts" 90
  check_post "cpu_clear_pipeline" "cpu_clear_pipeline" 90
  check_post "cpu_kill_scripts" "cpu_kill_scripts" 90
else
  log "SKIP: cooldown invoke (use --invoke-cooldown to run relief actions on this Mac)"
fi

if [[ "$FULL" -eq 1 ]]; then
  log "=== Full tier (--full) ==="
  check_post "scan" "scan" 300
  check_post "heal" "heal" 300
  check_post "pipeline" "pipeline" 120
fi

elapsed=$(( $(date +%s) - started ))
log ""
if [[ $fail -ne 0 ]]; then
  log "validate-mac-health-cooldown-e2e-v1: FAIL (${elapsed}s)"
  exit 1
fi
log "validate-mac-health-cooldown-e2e-v1: PASS (${elapsed}s)"
exit 0
