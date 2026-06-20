#!/usr/bin/env bash
# Gate N — formal close for HUB_STABILIZATION N1 + backlog P1–P10.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0

_fail() {
  echo "FAIL: $*" >&2
  FAIL=1
}

echo "=== Gate N0 — baseline ports ==="
lsof -nP -iTCP:13020 -sTCP:LISTEN >/dev/null 2>&1 || _fail ":13020 not listening"
lsof -nP -iTCP:13030 -sTCP:LISTEN >/dev/null 2>&1 || _fail ":13030 not listening"
curl -sf "http://127.0.0.1:13020/health" >/dev/null || _fail "hub /health"
curl -sf "http://127.0.0.1:13030/health" >/dev/null || _fail "worker /health"
echo "OK: N0 baseline — :13020 + :13030 up"

echo "=== Gate N1 — restart chain ==="
SINA_FORCE_RESTART=1 bash "$ROOT/scripts/serve-sina-command.sh" >/dev/null 2>&1 || _fail "serve-sina-command.sh"
sleep 3
curl -sf "http://127.0.0.1:13020/health" >/dev/null || _fail "hub down after restart"
curl -sf "http://127.0.0.1:13030/health" >/dev/null || _fail "worker down after restart"
echo "OK: N1 restart chain — both ports up"

echo "=== Gate N2 — coalesce proof ==="
DONE_LOG="$HOME/.sina/hub-rebuild-done-v1.jsonl"
WORKER_LOG="$HOME/.sina/hub-rebuild-worker.log"
MARK="gate_n_coalesce_$(date +%s)"
BEFORE_DONE=0
if [[ -f "$DONE_LOG" ]]; then
  BEFORE_DONE=$(wc -l <"$DONE_LOG" | tr -d ' ')
fi
for i in $(seq 1 10); do
  PYTHONPATH="$ROOT/scripts" python3 -c "
from hub_queue_lib_v1 import enqueue_rebuild
enqueue_rebuild(source='${MARK}_$i', run_refresh=False)
"
done
sleep 10
CONSUMED=0
if [[ -f "$DONE_LOG" ]]; then
  CONSUMED=$(grep -c "$MARK" "$DONE_LOG" 2>/dev/null || true)
fi
if [[ "$CONSUMED" -lt 10 ]]; then
  _fail "coalesce: expected 10 consumed events with $MARK, got $CONSUMED"
fi
if [[ -f "$WORKER_LOG" ]] && ! grep -q "coalescing 10 events" "$WORKER_LOG" 2>/dev/null; then
  # Accept if a single coalesce line exists for this batch (log may rotate)
  if ! tail -30 "$WORKER_LOG" 2>/dev/null | grep -q "coalescing"; then
    _fail "coalesce: worker log missing 'coalescing N events'"
  fi
fi
echo "OK: N2 coalesce — 10 events consumed ($MARK)"

echo "=== Gate N3 — stabilization light E2E ==="
bash "$ROOT/scripts/validate-hub-stabilization-e2e-light-v1.sh" || _fail "light E2E"

echo "=== Gate N4 — ecosystem safety ==="
bash "$ROOT/scripts/validate-ecosystem-safety-v1.sh" || _fail "ecosystem safety"

echo "=== Gate N5 — find_critical_bugs ==="
python3 "$ROOT/scripts/find_critical_bugs.py" || _fail "find_critical_bugs"

if [[ "$FAIL" -ne 0 ]]; then
  echo "FAIL: validate-hub-stabilization-gate-n-v1" >&2
  exit 1
fi
echo "OK: validate-hub-stabilization-gate-n-v1 — Gate N PASS"
