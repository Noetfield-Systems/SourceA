#!/usr/bin/env bash
# Fast E2E ladder (~90s) — run before full E2E when debugging or in standard recipe step 1.
# Brain post-mortem: pack → phase-s0 → strict build → hub source alignment.
# --require-idle: exit 2 in <5s if factory mid-slice (INCIDENT-026 / E2E_EXECUTOR_CHECKLIST step 2).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "validate-e2e-fast-ladder-v1.sh" "$ROOT"
errors=0
t0=$SECONDS
REQUIRE_IDLE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --require-idle) REQUIRE_IDLE=1; shift ;;
    -h | --help)
      echo "Usage: $0 [--require-idle]"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1"
      exit 1
      ;;
  esac
done

if [[ "$REQUIRE_IDLE" -eq 1 ]]; then
  echo "=== factory idle gate ==="
  if python3 "$SCRIPTS/factory_idle_gate_v1.py" --json; then
    :
  else
    ec=$?
    if [[ "$ec" -eq 2 ]]; then
      echo "E2E-FAST-LADDER BLOCKED — factory not idle (exit 2)"
      echo "Hint: run inbox once · one brain_sync · then retry (max 1 ladder per turn)"
      exit 2
    fi
    echo "WARN: idle probe error ec=$ec — continuing"
  fi
  echo ""
fi

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

echo "=== E2E-FAST-LADDER start ==="
echo ""

if python3 "$SCRIPTS/factory_validation_lock_v1.py" status --json | python3 -c "import json,sys; st=json.load(sys.stdin); exit(0 if not st.get('locked') else 1)" 2>/dev/null; then
  :
else
  echo "=== factory lock ==="
  python3 "$SCRIPTS/factory_validation_lock_v1.py" status --json 2>/dev/null || true
  echo "FAIL: factory lock busy — cannot strict-build during full_e2e"
  exit 1
fi

if curl -sf "http://127.0.0.1:13020/health" >/dev/null 2>&1; then
  echo "=== hub health ==="
  echo "OK: :13020/health"
  echo ""
else
  echo "=== hub health ==="
  echo "WARN: hub not up on :13020 — ladder continues (strict build may still pass)"
  echo ""
fi

_run "sourcea-1000 pack" bash "$SCRIPTS/validate-sourcea-1000-pack.sh"
_run "phase-s0 SSOT alignment" bash "$SCRIPTS/validate-phase-s0-ssot-alignment-v1.sh"
_run "strict build" bash -c "cd '$SCRIPTS' && SINA_AUDIT_STRICT=1 python3 build-sina-command-panel.py"
_run "hub source alignment" bash -c "cd '$SCRIPTS' && python3 audit_hub_source_alignment.py"

elapsed=$((SECONDS - t0))
if [[ $errors -gt 0 ]]; then
  echo "E2E-FAST-LADDER FAIL errors=$errors elapsed=${elapsed}s"
  exit 1
fi
echo "E2E-FAST-LADDER PASS elapsed=${elapsed}s"
