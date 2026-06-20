#!/usr/bin/env bash
# validate-governance-completion-backlog-v1.sh — open founder forks must surface (AS-19)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-governance-completion-backlog-v1 — $*" >&2; exit 1; }

python3 scripts/governance_completion_backlog_audit.py --check || {
  python3 scripts/governance_completion_backlog_audit.py
  fail "critical founder/completion backlog open — report in SAY card before SHIP"
}

echo "OK: validate-governance-completion-backlog-v1 (no critical open forks)"
