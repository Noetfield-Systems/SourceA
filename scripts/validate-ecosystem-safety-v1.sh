#!/usr/bin/env bash
# Ecosystem safety preflight — factory lock, monitor truth, dual_proof, hub, lanes wired.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
cd "$ROOT"
errors=0

_fail() {
  echo "FAIL: $1"
  errors=$((errors + 1))
}

_ok() {
  echo "OK: $1"
}

echo "=== validate-ecosystem-safety-v1 ==="

# 0) Stale factory lock sweep
sweep="$(python3 "$SCRIPTS/factory_validation_lock_v1.py" sweep --json)"
echo "$sweep" | python3 -c "import json,sys; s=json.load(sys.stdin); print('sweep:', s)" 2>/dev/null || true
if python3 "$SCRIPTS/factory_validation_lock_v1.py" status --json | python3 -c "
import json,sys
st=json.load(sys.stdin)
assert not st.get('locked'), st.get('lock')
"; then
  _ok "factory lock clear (or stale swept)"
else
  _fail "factory lock busy — wait or kill orphan validate-sourcea-e2e-full-v1.sh"
fi

# 1) Hub health
if curl -sf "http://127.0.0.1:13020/health" >/dev/null 2>&1; then
  _ok "hub :13020/health"
else
  _fail "hub :13020 down — serve-sina-command.sh"
fi

# 2) Monitor honesty + queue tab sanity
if PYTHONPATH="$SCRIPTS" python3 "$SCRIPTS/_ecosystem_safety_monitor_check_v1.py"; then
  _ok "monitor honesty + queue tab aligned"
else
  _fail "monitor honesty or queue tab"
fi

# 3) INBOX vs orchestrator
if PYTHONPATH="$SCRIPTS" python3 "$SCRIPTS/_ecosystem_safety_orchestrator_check_v1.py"; then
  _ok "orchestrator + INBOX aligned"
else
  _fail "orchestrator vs INBOX drift"
fi

# 4) Lane + E2E recipe wiring
test -f "$ROOT/brain-os/enforcement/FOUNDER_LANE_SEPARATION_LOCKED_v1.md"
grep -q "STRATEGIC — not Worker scope" "$ROOT/brain-os/plan-registry/CANADA_AI_FOR_ALL_FUNDING_ALIGNMENT_v1.md"
test -f "$SCRIPTS/validate-sourcea-e2e-standard-v1.sh"
test -f "$SCRIPTS/validate-e2e-fast-ladder-v1.sh"
bash "$SCRIPTS/validate-sourcea-session-index-locked-v1.sh" >/dev/null
_ok "lane separation + E2E recipe + LOCKED session docs on disk"

# 5) Hub built_at sync contract (sa-0042 flake class)
bash "$SCRIPTS/validate-hub-built-at-sync-contract-v1.sh" >/dev/null
_ok "hub built_at sync contract (sa-0017/sa-0042)"

# 6) P0 hardening still wired
bash "$SCRIPTS/validate-e2e-hardening-p0-v1.sh" >/dev/null
_ok "E2E hardening P0 bundle"

# 7) Hub API + Safety button wired (empty-reply / missing action class)
if PYTHONPATH="$SCRIPTS" python3 "$SCRIPTS/_ecosystem_safety_hub_api_check_v1.py"; then
  _ok "hub /api/action + hub-sync + Safety button"
else
  _fail "hub API or home Safety button"
fi

# 8) Anti-staleness bundle — hub P0 · spawn gate · bowl · brain sync (AS-01..07)
if bash "$SCRIPTS/validate-anti-staleness-bundle-v1.sh" >/dev/null; then
  _ok "anti-staleness bundle (hub P0 · spawn · bowl · brain)"
else
  _fail "anti-staleness bundle — see validate-anti-staleness-bundle-v1.sh"
fi

# 8b) S10 eternal self-heal loop wiring (T9)
if bash "$SCRIPTS/validate-s10-eternal-loop-v1.sh" >/dev/null; then
  _ok "S10 eternal audit loop wired"
else
  _fail "validate-s10-eternal-loop-v1.sh"
fi

# 8c) Agent navigation — mandatory read paths (G0.3)
if bash "$SCRIPTS/validate-mandatory-read-paths-v1.sh" >/dev/null; then
  _ok "mandatory read paths (no os/chat-handoffs)"
else
  _fail "MANDATORY_READ_BY_ROLE broken paths"
fi

# 8b) Cursor rules scoping (G1.1)
if bash "$SCRIPTS/validate-cursor-rules-scoping-v1.sh" >/dev/null; then
  _ok "cursor rules scoped (≤4 global alwaysApply)"
else
  _fail "cursor rules scoping — see validate-cursor-rules-scoping-v1.sh"
fi

# 8c) Closeout receipt-only gate (INCIDENT-026 — fast grep)
if bash "$SCRIPTS/validate-closeout-receipt-only-v1.sh" >/dev/null; then
  _ok "closeout receipt-only (no validator recursion)"
else
  _fail "closeout subprocesses validators — see validate-closeout-receipt-only-v1.sh"
fi

# 9) Live ongoing next-10 + pack validator
if bash "$SCRIPTS/validate-live-ongoing-prompts-v1.sh" >/dev/null; then
  _ok "live ongoing prompts cursor-aligned"
else
  _fail "live ongoing prompts stale or misaligned — run live_ongoing_prompts_v1.py --rebuild"
fi
if PYTHONPATH="$SCRIPTS" python3 "$SCRIPTS/validate-next-prompt-pack-live-v1.py" --strict --json >/dev/null 2>&1; then
  _ok "live pack validator PASS"
else
  _fail "live pack validator FAIL — see live-pack-validator-receipt-v1.json"
fi

# 10) Dual-pick FAIL-closed — live_pick vs queue (G0.2 · DISK_TRUTH_E2E row 13)
if PYTHONPATH="$SCRIPTS" python3 "$SCRIPTS/_ecosystem_safety_dual_pick_check_v1.py"; then
  _ok "dual-pick aligned (goal-progress live_pick = run-inbox queue)"
else
  _fail "dual-pick GAP — live_pick != queue_sa (hub projection lies; see SOURCEA_DISK_TRUTH_E2E_MATRIX_LOCKED_v1.md §13)"
fi

if [[ $errors -gt 0 ]]; then
  echo "FAIL: validate-ecosystem-safety-v1 errors=$errors"
  exit 1
fi
echo "PASS: validate-ecosystem-safety-v1"
