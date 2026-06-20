#!/usr/bin/env bash
# validate-founder-pivot-pattern-v1.sh — pivot SSOT · router · wire proof
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-founder-pivot-pattern-v1 — $*" >&2; exit 1; }

test -f data/founder-pivot-pattern-v1.json || fail "missing SSOT"
test -f scripts/founder_pivot_router_v1.py || fail "missing router"
grep -q 'founder_pivot_router' scripts/brain_intent_gate_v1.py || fail "brain_intent_gate not wired"
grep -q 'founder_pivot_router' scripts/founder_input_cascade_v1.py || fail "cascade not wired"
grep -q 'founder_pivot_router' scripts/founder_routing_panel_v1.py || fail "routing panel not wired"

python3 - <<'PY' || fail "pattern match proof"
import json, sys
from pathlib import Path

sys.path.insert(0, "scripts")
from founder_pivot_router_v1 import route_founder_pivot, RECEIPT, SSOT

spec = json.loads(Path("data/founder-pivot-pattern-v1.json").read_text())
if len(spec.get("patterns") or []) < 5:
    raise SystemExit("expected >=5 seeded patterns")

msg = "WORK: Wire cloud worker team and Phase 0 noetfield freemium factory — all loops on machines"
row = route_founder_pivot(msg, source="validator_proof", write=True)
if not row.get("matched"):
    raise SystemExit("expected pivot match on compound message")
if row.get("pivot_id") != "PIVOT-NF-FACTORY-FIRST":
    raise SystemExit(f"expected NF first priority, got {row.get('pivot_id')}")

if not RECEIPT.is_file():
    raise SystemExit("missing receipt")
rec = json.loads(RECEIPT.read_text())
if rec.get("schema") != "founder-pivot-routing-receipt-v1":
    raise SystemExit("bad receipt schema")
if not rec.get("inject_line"):
    raise SystemExit("missing inject_line")

print(f"OK: pivot proof · id={rec.get('pivot_id')} · patterns={len(spec.get('patterns') or [])}")
PY

python3 scripts/founder_routing_panel_v1.py --json >/dev/null || fail "routing panel run after pivot"

echo "OK: validate-founder-pivot-pattern-v1"
