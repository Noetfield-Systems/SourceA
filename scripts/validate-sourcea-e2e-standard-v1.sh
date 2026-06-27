#!/usr/bin/env bash
# Brain standard E2E recipe — preconditions → fast ladder → full E2E (tee) → goal1 → brain receipt.
# Budget: ~6–8 min when healthy. Never pipe full E2E to tail — use this script or tee below.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"

LADDER_ONLY=0
SKIP_PRECONDITIONS=0

usage() {
  echo "Usage: $0 [--ladder-only] [--skip-preconditions]"
  echo "  --ladder-only         Stop after fast ladder (~90s)"
  echo "  --skip-preconditions  Skip hygiene curl preflight"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ladder-only) LADDER_ONLY=1; shift ;;
    --skip-preconditions) SKIP_PRECONDITIONS=1; shift ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1"
      usage
      exit 1
      ;;
  esac
done

t0=$SECONDS
echo "=== SOURCEA-E2E-STANDARD start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo ""

echo "=== factory lock preflight ==="
python3 "$SCRIPTS/factory_validation_lock_v1.py" sweep --json >/dev/null 2>&1 || true
if ! python3 "$SCRIPTS/factory_validation_lock_v1.py" status --json | python3 -c "import json,sys; st=json.load(sys.stdin); assert not st.get('locked'), st.get('lock')"; then
  python3 "$SCRIPTS/factory_validation_lock_v1.py" status --json 2>/dev/null || true
  echo "FAIL: factory lock busy — wait for prior E2E/build or release stale lock"
  exit 1
fi
echo "OK: factory lock clear"
echo ""

# 0) Preconditions (~5s+)
if [[ $SKIP_PRECONDITIONS -eq 0 ]]; then
  echo "=== preconditions ==="
  if curl -sf "http://127.0.0.1:13020/health" >/dev/null 2>&1; then
    echo "OK: :13020/health"
  else
    echo "FAIL: hub not up on :13020 — start serve-sina-command.sh"
    exit 1
  fi
  bash "$SCRIPTS/ensure-hub-rebuild-worker-v1.sh" || exit 1
  hygiene_tail="$(bash "$SCRIPTS/enforce-registry-hygiene-v1.sh" 2>&1 | tail -3)"
  echo "$hygiene_tail"
  echo "OK: preconditions"
  echo ""
fi

# 1) Fast ladder — stop here on FAIL (~90s)
bash "$SCRIPTS/validate-e2e-fast-ladder-v1.sh" --require-idle

if [[ $LADDER_ONLY -eq 1 ]]; then
  elapsed=$((SECONDS - t0))
  echo "SOURCEA-E2E-STANDARD PASS (ladder-only) elapsed=${elapsed}s"
  exit 0
fi

# 2) Full E2E only if ladder green (~5 min) — tee for live lines + post-mortem log
LOG="/tmp/e2e-$(date +%Y%m%d-%H%M%S).log"
echo "=== full E2E (budget ≥6 min) log=$LOG ==="
set +e
bash "$SCRIPTS/validate-sourcea-e2e-full-v1.sh" 2>&1 | tee "$LOG"
full_rc=${PIPESTATUS[0]}
set -e
if [[ $full_rc -ne 0 ]]; then
  echo "FAIL: validate-sourcea-e2e-full-v1.sh exit=$full_rc — see $LOG"
  exit 1
fi
echo "OK: full E2E — log=$LOG"
echo ""

# 3) Goal1 dry path AFTER full E2E (not before) — mutex in validate-goal1-e2e-v1.sh
bash "$SCRIPTS/validate-goal1-e2e-v1.sh"
echo ""

# 4) Brain tick + dual_proof
echo "=== brain receipt ==="
brain_out="$(python3 "$SCRIPTS/brain_validate_goal1_v1.py" --json --write-receipt 2>&1)" || true
echo "$brain_out" | head -20
if echo "$brain_out" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok') is True" 2>/dev/null; then
  echo "OK: brain_validate_goal1 --write-receipt"
else
  echo "WARN: brain_validate_goal1 did not return ok:true (see output)"
fi
echo ""

echo "=== dual_proof ==="
dual_line="$(bash "$SCRIPTS/enforce-registry-hygiene-v1.sh" 2>&1 | grep -E 'dual_proof=' || true)"
echo "$dual_line"
if echo "$dual_line" | grep -q "dual_proof=True"; then
  echo "OK: dual_proof=True"
else
  echo "FAIL: dual_proof not True"
  exit 1
fi

elapsed=$((SECONDS - t0))
echo ""
echo "SOURCEA-E2E-STANDARD PASS elapsed=${elapsed}s log=$LOG"

# Durable E2E report (agents read before next run)
python3 "$SCRIPTS/sourcea_e2e_run_v1.py" \
  --ingest-bundle sourcea_standard \
  --ingest-ok \
  --log-path "${LOG:-}" \
  --cadence weekly \
  --write-report \
  --json >/dev/null 2>&1 || true
