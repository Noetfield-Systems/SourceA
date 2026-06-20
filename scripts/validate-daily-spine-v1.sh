#!/usr/bin/env bash
# validate-daily-spine-v1.sh — Zone A daily green (no museum E2E)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-daily-spine-v1 — $*" >&2; exit 1; }

python3 scripts/agent_truth_bundle_v1.py --json >/dev/null || fail "truth bundle"
bash scripts/validate-super-fast-hub-v1.sh || fail "super fast hub"
bash scripts/validate-brain-not-command-data-ssot-v1.sh || fail "brain not command-data"
bash scripts/validate-museum-stale-copy-v1.sh || fail "museum founder hero"
bash scripts/validate-prompt-feed-no-autosend-copy-v1.sh || fail "prompt feed autosend"
python3 scripts/governance_meta_audit_v1.py --tier fast --json >/dev/null || fail "gov meta-audit"

echo "OK: validate-daily-spine-v1 · Zone A daily spine"
