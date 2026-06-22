#!/bin/zsh
# Desktop .app launcher — start hub, run engines via API, always open browser (cache-bust).
set -uo pipefail

SA="$HOME/Desktop/SourceA"
PORT="${SINA_COMMAND_PORT:-13020}"
BASE="http://127.0.0.1:${PORT}"
ACTION="${1:-apps}"
CURL="${CURL:-/usr/bin/curl}"
OPEN="${OPEN:-/usr/bin/open}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:/usr/bin:/bin:/usr/sbin:/sbin"

notify() {
  /usr/bin/osascript -e "display notification \"${1}\" with title \"${2:-Sina}\"" 2>/dev/null || true
}

alert_fail() {
  /usr/bin/osascript -e "display alert \"Sina\" message \"${1}\"" 2>/dev/null || true
}

# Standalone mini-apps — never require Sina Command hub
case "$ACTION" in
  mac-health-guard|mac-health|health-guard)
    SERVE_MH="$SA/scripts/serve-mac-health-guard.sh"
    MH_PORT="${MAC_HEALTH_PORT:-13024}"
    TS="$(date +%s)"
    if ! "$CURL" -sf "http://127.0.0.1:${MH_PORT}/health" >/dev/null 2>&1; then
      notify "Starting Mac Health Guard…" "Mac Health Guard"
      "$SERVE_MH" || true
      for _ in {1..40}; do
        "$CURL" -sf "http://127.0.0.1:${MH_PORT}/health" >/dev/null 2>&1 && break
        sleep 0.25
      done
    fi
    if ! "$CURL" -sf "http://127.0.0.1:${MH_PORT}/health" >/dev/null 2>&1; then
      alert_fail "Mac Health Guard not ready. See ~/.sina/mac-health-guard-server.log"
      exit 1
    fi
    notify "Opening Mac Health Guard…" "Mac Health Guard"
    "$OPEN" "http://127.0.0.1:${MH_PORT}/?t=${TS}"
    exit 0
    ;;
  chat-unify|chat-merge|unify-chats)
    CU_APP="$HOME/Desktop/Chat Unify.app"
    if [[ -d "$CU_APP" ]]; then
      notify "Opening Chat Unify…" "Chat Unify"
      "$OPEN" "$CU_APP"
      exit 0
    fi
    CU_PORT="${CHAT_UNIFY_PORT:-13023}"
    CU_BASE="http://127.0.0.1:${CU_PORT}"
    if ! "$CURL" -sf "${CU_BASE}/health" >/dev/null 2>&1; then
      notify "Starting Chat Unify…" "Chat Unify"
      "$SA/scripts/serve-chat-unify.sh" || true
      for _ in {1..40}; do
        "$CURL" -sf "${CU_BASE}/health" >/dev/null 2>&1 && break
        sleep 0.25
      done
    fi
    if ! "$CURL" -sf "${CU_BASE}/health" >/dev/null 2>&1; then
      alert_fail "Chat Unify not ready. See ~/.sina/chat-unify-server.log"
      exit 1
    fi
    notify "Opening Chat Unify…" "Chat Unify"
    "$OPEN" "${CU_BASE}/?t=$(date +%s)"
    exit 0
    ;;
  n8n-integration|n8n|automation-spine)
    N8_APP="$HOME/Desktop/N8N Integration.app"
    if [[ -d "$N8_APP" ]]; then
      notify "Opening N8N Integration…" "N8N Integration"
      "$OPEN" "$N8_APP"
      exit 0
    fi
    N8_PORT="${N8N_INTEGRATION_PORT:-13026}"
    N8_BASE="http://127.0.0.1:${N8_PORT}"
    if ! "$CURL" -sf "${N8_BASE}/health" >/dev/null 2>&1; then
      notify "Starting N8N Integration…" "N8N Integration"
      "$SA/scripts/serve-n8n-integration.sh" || true
      for _ in {1..40}; do
        "$CURL" -sf "${N8_BASE}/health" >/dev/null 2>&1 && break
        sleep 0.25
      done
    fi
    if ! "$CURL" -sf "${N8_BASE}/health" >/dev/null 2>&1; then
      alert_fail "N8N Integration not ready. See ~/.sina/n8n-integration-boot.log"
      exit 1
    fi
    notify "Opening N8N Integration…" "N8N Integration"
    "$OPEN" "${N8_BASE}/?t=$(date +%s)"
    exit 0
    ;;
  portfolio-mail|mail-hub|mail)
    bash "$SA/scripts/portfolio-stack-start-v1.sh" || true
    PM_APP="$HOME/Desktop/Portfolio Mail.app"
    if [[ -d "$PM_APP" ]]; then
      notify "Opening Portfolio Mail…" "Portfolio Mail"
      "$OPEN" "$PM_APP"
      exit 0
    fi
    CU_PORT="${CHAT_UNIFY_PORT:-13023}"
    N8_PORT="${N8N_INTEGRATION_PORT:-13026}"
    if ! "$CURL" -sf "http://127.0.0.1:${CU_PORT}/health" >/dev/null 2>&1; then
      notify "Starting Chat Unify…" "Portfolio Mail"
      "$SA/scripts/serve-chat-unify.sh" || true
    fi
    if ! "$CURL" -sf "http://127.0.0.1:${N8_PORT}/health" >/dev/null 2>&1; then
      notify "Starting N8N Integration…" "Portfolio Mail"
      "$SA/scripts/serve-n8n-integration.sh" || true
    fi
    if ! "$CURL" -sf "${BASE}/health" >/dev/null 2>&1; then
      notify "Starting Worker Hub…" "Portfolio Mail"
      "$SA/scripts/serve-sina-command.sh" || true
      for _ in {1..40}; do
        "$CURL" -sf "${BASE}/health" >/dev/null 2>&1 && break
        sleep 0.25
      done
    fi
    python3 "$SA/scripts/portfolio_mail_integration_wire_v1.py" --wire --json >/dev/null 2>&1 || true
    notify "Opening Portfolio Mail…" "Portfolio Mail"
    "$OPEN" "${BASE}/mail-hub/?t=$(date +%s)"
    exit 0
    ;;
  worker-hub|hub|open|command|home)
    bash "$SA/scripts/portfolio-stack-start-v1.sh" || true
    WH_APP="$HOME/Desktop/Worker Hub.app"
    if [[ -d "$WH_APP" ]]; then
      notify "Opening Worker Hub…" "Worker Hub"
      "$OPEN" "$WH_APP"
      exit 0
    fi
    if ! "$CURL" -sf "${BASE}/health" >/dev/null 2>&1; then
      notify "Starting Worker Hub stack…" "Worker Hub"
      bash "$SA/scripts/worker-hub-stack-boot.sh" || true
      for _ in {1..40}; do
        "$CURL" -sf "${BASE}/health" >/dev/null 2>&1 && break
        sleep 0.25
      done
    fi
    notify "Opening Worker Hub…" "Worker Hub"
    "$OPEN" "${BASE}/?t=$(date +%s)"
    exit 0
    ;;
esac

ensure_server() {
  if "$CURL" -sf "${BASE}/health" >/dev/null 2>&1; then
    return 0
  fi
  notify "Starting Sina Command server…" "Sina"
  if ! "$SA/scripts/serve-sina-command.sh"; then
    return 1
  fi
  for _ in {1..80}; do
    if "$CURL" -sf "${BASE}/health" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.25
  done
  return 1
}

api_launch() {
  local app_id="$1"
  "$CURL" -sf -X POST "${BASE}/api/apps/launch" \
    -H "Content-Type: application/json" \
    -d "{\"id\":\"${app_id}\"}" >/dev/null 2>&1
}

ensure_promptos() {
  local pos="$HOME/Desktop/SinaPromptOS"
  local log="$HOME/.sina/promptos-ui.log"
  mkdir -p "$HOME/.sina"
  if [[ -f "$HOME/.sina/secrets.env" ]]; then
    set -a
    source "$HOME/.sina/secrets.env"
    set +a
  fi
  if ! "$CURL" -sf "http://127.0.0.1:8765/_stcore/health" >/dev/null 2>&1; then
    notify "Starting Prompt OS UI…" "Sina Prompt OS"
    "$pos/scripts/start-promptos-ui.sh" >>"$log" 2>&1 || true
    for _ in {1..40}; do
      "$CURL" -sf "http://127.0.0.1:8765/_stcore/health" >/dev/null 2>&1 && return 0
      sleep 0.5
    done
    return 1
  fi
  return 0
}

if [[ ! -d "$SA" ]]; then
  alert_fail "SourceA not found at ~/Desktop/SourceA"
  exit 1
fi

if ! ensure_server; then
  err="$(grep -E 'Error|Traceback|Address already' "$HOME/.sina/command-server.log" 2>/dev/null | tail -2 | tr '\n' ' ')"
  alert_fail "Server not ready. Log: ~/.sina/command-server.log ${err}"
  exit 1
fi

TS="$(date +%s)"
case "$ACTION" in
  open|command|home)
    WH_APP="$HOME/Desktop/Worker Hub.app"
    if [[ -d "$WH_APP" ]]; then
      notify "Opening Worker Hub…" "Worker Hub"
      "$OPEN" "$WH_APP"
      exit 0
    fi
    URL="${BASE}/?tab=command&t=${TS}"
    TITLE="Sina Command"
    ;;
  apps|branches|hub)
    URL="${BASE}/?tab=apps&t=${TS}"
    TITLE="Connected Apps"
    ;;
  dispatch)
    api_launch "sina-dispatch" || true
    URL="${BASE}/?tab=apps&run=pos-dispatch&t=${TS}"
    TITLE="Sina Dispatch"
    notify "Dispatch started — output in Command Apps tab" "$TITLE"
    ;;
  execute)
    api_launch "sina-execute" || true
    URL="${BASE}/?tab=apps&run=pos-execute&t=${TS}"
    TITLE="Sina Execute All"
    notify "Execute All started — run Status when done" "$TITLE"
    ;;
  decide)
    api_launch "sina-decide" || true
    URL="${BASE}/?tab=apps&run=pos-decide&t=${TS}"
    TITLE="Sina Decide"
    notify "Decide finished — see Command Apps output panel" "$TITLE"
    ;;
  run)
    api_launch "sina-run" || true
    URL="${BASE}/?tab=apps&run=pos-run&t=${TS}"
    TITLE="Sina Run Now"
    notify "Run Now started in background" "$TITLE"
    ;;
  status)
    api_launch "sina-status" || true
    URL="${BASE}/?tab=apps&run=pos-status&t=${TS}"
    TITLE="Sina Status"
    notify "Status loaded in Command Apps tab" "$TITLE"
    ;;
  promptos|ui|pos-ui)
    if ensure_promptos; then
      notify "Opening Prompt OS in browser" "Sina Prompt OS"
      "$OPEN" "http://127.0.0.1:8765/?t=${TS}"
      exit 0
    fi
    alert_fail "Prompt OS UI did not start. See ~/.sina/promptos-ui.log"
    exit 1
    ;;
  apple-health|health-wellness)
    AH_PORT="${APPLE_HEALTH_PORT:-13025}"
    AH_BASE="http://127.0.0.1:${AH_PORT}"
    if ! "$CURL" -sf "${AH_BASE}/health" >/dev/null 2>&1; then
      notify "Starting Apple Health…" "Apple Health"
      "$SA/scripts/serve-apple-health.sh" || true
      for _ in {1..40}; do
        "$CURL" -sf "${AH_BASE}/health" >/dev/null 2>&1 && break
        sleep 0.25
      done
    fi
    if ! "$CURL" -sf "${AH_BASE}/health" >/dev/null 2>&1; then
      alert_fail "Apple Health not ready. See ~/.sina/apple-health-server.log"
      exit 1
    fi
    notify "Opening Apple Health…" "Apple Health"
    "$OPEN" "${AH_BASE}/?t=${TS}"
    exit 0
    ;;
  mac-health-guard|mac-health|health-guard)
    SERVE_MH="$SA/scripts/serve-mac-health-guard.sh"
    MH_PORT="${MAC_HEALTH_PORT:-13024}"
    if ! "$CURL" -sf "http://127.0.0.1:${MH_PORT}/health" >/dev/null 2>&1; then
      notify "Starting Mac Health Guard…" "Mac Health Guard"
      "$SERVE_MH" || true
      for _ in {1..40}; do
        "$CURL" -sf "http://127.0.0.1:${MH_PORT}/health" >/dev/null 2>&1 && break
        sleep 0.25
      done
    fi
    URL="http://127.0.0.1:${MH_PORT}/?t=${TS}"
    TITLE="Mac Health Guard"
    ;;
  chat-unify|chat-merge|unify-chats)
    CU_APP="$HOME/Desktop/Chat Unify.app"
    if [[ -d "$CU_APP" ]]; then
      notify "Opening Chat Unify…" "Chat Unify"
      "$OPEN" "$CU_APP"
      exit 0
    fi
    CU_PORT="${CHAT_UNIFY_PORT:-13023}"
    CU_BASE="http://127.0.0.1:${CU_PORT}"
    if ! "$CURL" -sf "${CU_BASE}/health" >/dev/null 2>&1; then
      notify "Starting Chat Unify…" "Chat Unify"
      "$SA/scripts/serve-chat-unify.sh" || true
      for _ in {1..40}; do
        "$CURL" -sf "${CU_BASE}/health" >/dev/null 2>&1 && break
        sleep 0.25
      done
    fi
    URL="${CU_BASE}/?t=${TS}"
    TITLE="Chat Unify"
    ;;
  n8n-integration|n8n|automation-spine)
    N8_APP="$HOME/Desktop/N8N Integration.app"
    if [[ -d "$N8_APP" ]]; then
      notify "Opening N8N Integration…" "N8N Integration"
      "$OPEN" "$N8_APP"
      exit 0
    fi
    N8_PORT="${N8N_INTEGRATION_PORT:-13026}"
    N8_BASE="http://127.0.0.1:${N8_PORT}"
    if ! "$CURL" -sf "${N8_BASE}/health" >/dev/null 2>&1; then
      notify "Starting N8N Integration…" "N8N Integration"
      "$SA/scripts/serve-n8n-integration.sh" || true
      for _ in {1..40}; do
        "$CURL" -sf "${N8_BASE}/health" >/dev/null 2>&1 && break
        sleep 0.25
      done
    fi
    URL="${N8_BASE}/?t=${TS}"
    TITLE="N8N Integration"
    ;;
  portfolio-mail|mail-hub|mail)
    PM_APP="$HOME/Desktop/Portfolio Mail.app"
    if [[ -d "$PM_APP" ]]; then
      notify "Opening Portfolio Mail…" "Portfolio Mail"
      "$OPEN" "$PM_APP"
      exit 0
    fi
    CU_PORT="${CHAT_UNIFY_PORT:-13023}"
    N8_PORT="${N8N_INTEGRATION_PORT:-13026}"
    if ! "$CURL" -sf "http://127.0.0.1:${CU_PORT}/health" >/dev/null 2>&1; then
      api_launch "chat-unify" || "$SA/scripts/serve-chat-unify.sh" || true
    fi
    if ! "$CURL" -sf "http://127.0.0.1:${N8_PORT}/health" >/dev/null 2>&1; then
      api_launch "n8n-integration" || "$SA/scripts/serve-n8n-integration.sh" || true
    fi
    python3 "$SA/scripts/portfolio_mail_integration_wire_v1.py" --wire --json >/dev/null 2>&1 || true
    URL="${BASE}/mail-hub/?t=${TS}"
    TITLE="Portfolio Mail"
    ;;
  roadmaps|goals)
    URL="${BASE}/?tab=roadmaps&t=${TS}"
    TITLE="Roadmaps & goals"
    ;;
  daily)
    URL="${BASE}/?tab=daily&t=${TS}"
    TITLE="Daily"
    ;;
  rules)
    URL="${BASE}/?tab=rules&t=${TS}"
    TITLE="Rules"
    ;;
  *)
    URL="${BASE}/?tab=apps&run=${ACTION}&t=${TS}"
    TITLE="Sina"
    ;;
esac

notify "Opening browser…" "${TITLE:-Sina}"
"$OPEN" "$URL"
exit 0
