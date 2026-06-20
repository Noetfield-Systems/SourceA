#!/usr/bin/env bash
# validate-museum-quarantine-v1.sh — E2E cancelled · H1 no command-data prefetch
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-museum-quarantine-v1 — $*" >&2; exit 1; }

out="$(bash scripts/validate-sourcea-e2e-full-v1.sh 2>&1)" || true
echo "$out" | grep -q "CANCELLED" || fail "full E2E must stay CANCELLED by default"

html="$ROOT/agent-control-panel/worker-hub/index.html"
grep -q "command-data.json" "$html" && fail "H1 must not prefetch command-data.json"
grep -qi "museum-card" "$html" && fail "H1 must not embed Founder Museum card (SSOT v1.2 daily path)"
grep -qi "Open Form" "$html" || fail "H1 must expose Open Form (FORM_OFFICIAL)"

test -f "$ROOT/SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md" || fail "missing three-zone law"
test -f "$ROOT/scripts/zone_c_quarantine_gate_v1.py" || fail "missing zone_c gate"

echo "OK: validate-museum-quarantine-v1"
