#!/usr/bin/env bash
# Full SourceA E2E validation chain — gates, pick, build, hub, critical bugs.
# CANCELLED by default (founder 2026-06-10). Set SINA_E2E_FORCE=1 to run.
set -euo pipefail
if [[ "${SINA_E2E_FORCE:-}" != "1" && "${SINA_E2E_FORCE:-}" != "true" && "${SINA_E2E_FORCE:-}" != "yes" ]]; then
  echo "OK: validate-sourcea-e2e-full-v1 CANCELLED — see SINA_HUB_E2E_CANCELLED_LOCKED_v1.md"
  exit 0
fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
SCRIPTS="$ROOT/scripts"
errors=0
export SINA_UNDER_FACTORY_E2E=1

_factory_e2e_release() {
  python3 "$SCRIPTS/factory_validation_lock_v1.py" release --holder full_e2e --pid "$$" --json >/dev/null 2>&1 || true
}
trap _factory_e2e_release EXIT

if ! python3 "$SCRIPTS/factory_validation_lock_v1.py" acquire --holder full_e2e --pid "$$" --json | python3 -c "import json,sys; assert json.load(sys.stdin)['ok']"; then
  echo "FAIL: factory lock — another validation run in progress (or goal1 executor busy)"
  exit 1
fi
echo "OK: factory lock acquired (full_e2e)"
echo ""

_run() {
  local label="$1"
  shift
  echo "=== $label ==="
  if "$@"; then
    echo "OK: $label"
  else
    echo "FAIL: $label"
    errors=$((errors + 1))
  fi
  echo ""
}

# Layer 2/3 gates
_run "cursor entry gate" bash "$SCRIPTS/validate-cursor-entry-gate-v1.sh"
_run "brain disk-before-chat" bash "$SCRIPTS/validate-brain-disk-before-chat-v1.sh"
_run "agent loop gate receipt" bash "$SCRIPTS/validate-agent-loop-gate-receipt-v1.sh"
_run "worker one-sa turn gate" bash "$SCRIPTS/validate-worker-one-sa-turn-v1.sh"
_run "registry drain rail" bash "$SCRIPTS/validate-registry-drain-rail-v1.sh"
_run "file storage governance" bash "$SCRIPTS/validate-file-storage-v1.sh"

# REGISTRY + pick order
_run "sourcea-1000 pack" bash "$SCRIPTS/validate-sourcea-1000-pack.sh"
_run "pick order" python3 "$SCRIPTS/validate-sourcea-pick-order-v1.py"

# Hub up (required for backend E2E + find_critical_bugs)
if ! curl -sf "http://127.0.0.1:13020/health" >/dev/null 2>&1; then
  echo "=== hub health ==="
  echo "FAIL: hub not up on :13020 — start serve-sina-command.sh"
  errors=$((errors + 1))
  echo ""
else
  echo "=== hub health ==="
  echo "OK: :13020/health"
  echo ""
fi

echo "=== rebuild worker health ==="
if bash "$SCRIPTS/ensure-hub-rebuild-worker-v1.sh"; then
  echo ""
else
  errors=$((errors + 1))
  echo ""
fi

# Spine + strict build (includes SA queue + atomic command-data validators)
_run "execution spine" bash "$SCRIPTS/validate-execution-spine-v1.sh"
echo "=== strict build ==="
if (cd "$SCRIPTS" && SINA_AUDIT_STRICT=1 python3 build-sina-command-panel.py); then
  echo "OK: strict build"
else
  echo "FAIL: strict build"
  errors=$((errors + 1))
fi
echo ""

# Post-build hub alignment
_run "command-data SA queue" python3 "$SCRIPTS/validate-command-data-sa-queue-v1.py"

# Backend + critical path
if curl -sf "http://127.0.0.1:13020/health" >/dev/null 2>&1; then
  _run "backend E2E" python3 "$SCRIPTS/audit_backend_e2e.py"
  _run "shell heal" python3 "$SCRIPTS/heal_command_data_shell_v1.py" --force
  _run "feedback sync" python3 "$SCRIPTS/sync_feedback_aggregate_hub_built_at_v1.py"
  echo "=== find_critical_bugs ==="
  fcb_out="$(cd "$SCRIPTS" && python3 find_critical_bugs.py 2>&1)" || true
  echo "$fcb_out" | tail -8
  crit="$(echo "$fcb_out" | python3 -c "import sys,re; t=sys.stdin.read(); m=re.search(r'\"critical\":\s*(\d+)', t); print(m.group(1) if m else '1')")"
  if [[ "$crit" == "0" ]] && echo "$fcb_out" | grep -q '"ok": true'; then
    echo "OK: find_critical_bugs critical=0"
  else
    echo "FAIL: find_critical_bugs critical=$crit"
    errors=$((errors + 1))
  fi
  echo ""
fi

# Brain session mechanical pick
echo "=== brain-session-start ==="
pick="$(bash "$SCRIPTS/brain-session-start.sh" 2>/dev/null | awk -F= '/^NEXT_PICK=/{print $2}')"
live="$(bash "$SCRIPTS/plan-no-asf-run.sh" pick 1 2>/dev/null | awk '/^sa-/{print $1}')"
if [[ -n "$pick" && "$pick" == "$live" ]]; then
  echo "OK: brain NEXT_PICK=$pick matches pick 1"
else
  echo "FAIL: brain pick=$pick live pick=$live"
  errors=$((errors + 1))
fi
echo ""

if [[ $errors -gt 0 ]]; then
  echo "SOURCEA-E2E-FULL FAIL errors=$errors"
  exit 1
fi
echo "SOURCEA-E2E-FULL PASS"
