#!/usr/bin/env bash
# validate-authority-root-coverage-v1.sh — full root *_LOCKED*.md T3 orphan gate (extends AS-10)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-authority-root-coverage-v1 — $*" >&2; exit 1; }

python3 scripts/authority_root_coverage_audit.py --check || {
  python3 scripts/authority_root_coverage_audit.py
  fail "T3 orphans remain — register in authority index, LAW_ROOT, incident corpus, or GOV_UNIFY allowlist"
}

echo "OK: validate-authority-root-coverage-v1"
