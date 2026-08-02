#!/usr/bin/env bash
# Full SourceA ecosystem connected gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
python3 scripts/investigator_judge_unified_receipt_v1.py --json >/dev/null
python3 scripts/validate_sourcea_ecosystem_connected_v1.py --json >/dev/null
echo "OK: validate-sourcea-ecosystem-connected-v1 · worker · nerve · graph · agentic · orient"
