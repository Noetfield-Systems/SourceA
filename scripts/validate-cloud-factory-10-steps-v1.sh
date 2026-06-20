#!/usr/bin/env bash
# validate-cloud-factory-10-steps-v1.sh — CHECK ALL cloud factory receipts
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
python3 scripts/cloud_factory_check_v1.py --json
exit $?
