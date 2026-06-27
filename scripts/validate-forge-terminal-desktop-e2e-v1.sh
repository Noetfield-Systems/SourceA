#!/usr/bin/env bash
# Unified Forge Terminal desktop E2E — ship window / founder one-tap verify.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
PORT="${FORGE_TERMINAL_PORT:-13029}"
RECEIPT="${SINA}/forge-terminal-desktop-e2e-v1.json"
RESULTS_FILE="${SINA}/forge-terminal-desktop-e2e-steps.log"
FAILED=0

: >"${RESULTS_FILE}"

log() { echo "$*"; }
record() { echo "$1" >>"${RESULTS_FILE}"; }

ensure_server() {
  log "→ Cold-start dev server (live SourceA UI)…"
  lsof -ti:"${PORT}" 2>/dev/null | xargs kill -9 2>/dev/null || true
  sleep 0.5
  while read -r pid; do
    [[ -z "${pid}" ]] && continue
    cmd=$(ps -p "$pid" -o command= 2>/dev/null || true)
    if echo "$cmd" | grep -q forge-terminal-server.py; then kill -9 "$pid" 2>/dev/null || true; fi
  done < <(lsof -ti:"${PORT}" 2>/dev/null || true)
  FORGE_TERMINAL_PORT="${PORT}" FORGE_TERMINAL_STANDALONE=1 \
    env -u FORGE_TERMINAL_BUNDLE_ROOT \
    python3 "${ROOT}/scripts/forge-terminal-server.py" >/dev/null 2>&1 &
  SMOKE_PID=$!
  for _ in {1..24}; do
    if curl -sf "http://127.0.0.1:${PORT}/health" 2>/dev/null | grep -q forge-terminal; then
      log "✓ Dev server ready on :${PORT} (pid ${SMOKE_PID})"
      export FORGE_DESKTOP_E2E_SMOKE_PID="${SMOKE_PID}"
      return 0
    fi
    sleep 0.5
  done
  log "FAIL: no forge-terminal on :${PORT}"
  return 1
}

run_step() {
  local name="$1"
  shift
  log ""
  log "=== ${name} ==="
  if "$@"; then
    record "PASS ${name}"
    log "PASS ${name}"
  else
    record "FAIL ${name}"
    log "FAIL ${name}"
    FAILED=$((FAILED + 1))
  fi
}

ensure_server || { FAILED=$((FAILED + 1)); record "FAIL ensure_server"; }

export FORGE_KEEP_E2E_SERVER=1

run_step "quality_desktop" bash "${ROOT}/scripts/validate-forge-terminal-quality-desktop-e2e-v1.sh"

run_step "living_desktop" bash "${ROOT}/scripts/validate-forge-terminal-living-desktop-e2e-v1.sh"

ensure_server || { FAILED=$((FAILED + 1)); record "FAIL ensure_server_post_living"; }

run_step "main_e2e" python3 "${ROOT}/scripts/forge_terminal_e2e_verify_v1.py"
run_step "critic_e2e" python3 "${ROOT}/scripts/forge_terminal_critic_verify_v1.py"
run_step "ui_e2e" python3 "${ROOT}/scripts/forge_terminal_ui_e2e_verify_v1.py"
run_step "execution_matrix" python3 "${ROOT}/scripts/forge_terminal_execution_matrix_v1.py"
run_step "e2e_all" python3 "${ROOT}/scripts/forge_terminal_e2e_all_v1.py"
run_step "buttons_e2e" python3 "${ROOT}/scripts/forge_terminal_buttons_e2e_v1.py"
run_step "model_clear" python3 "${ROOT}/scripts/forge_terminal_model_clear_verify_v1.py"
run_step "desktop_send" python3 "${ROOT}/scripts/forge_terminal_desktop_send_e2e_verify_v1.py"
run_step "platform_pages" python3 "${ROOT}/scripts/forge_terminal_platform_pages_e2e_verify_v1.py"

mkdir -p "${SINA}"
python3 - <<PY
import json, time
from pathlib import Path
results = Path("${RESULTS_FILE}").read_text(encoding="utf-8").strip().splitlines()
Path("${RECEIPT}").write_text(json.dumps({
  "schema": "forge-terminal-desktop-e2e-v1",
  "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
  "port": int("${PORT}"),
  "failed_steps": int("${FAILED}"),
  "results": results,
  "app_version": "2.8.0",
}, indent=2) + "\\n", encoding="utf-8")
PY

if [[ -n "${FORGE_DESKTOP_E2E_SMOKE_PID:-}" ]]; then
  kill "${FORGE_DESKTOP_E2E_SMOKE_PID}" 2>/dev/null || true
fi

log ""
if [[ "${FAILED}" -eq 0 ]]; then
  log "✓ Forge Terminal desktop E2E — ALL PASS"
  log "  Receipt: ${RECEIPT}"
  exit 0
fi
log "✗ Forge Terminal desktop E2E — ${FAILED} step(s) failed"
log "  Receipt: ${RECEIPT}"
exit 1
