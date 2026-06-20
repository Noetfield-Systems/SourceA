#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=governance-paths-v1.sh
. "$ROOT/scripts/governance-paths-v1.sh"
fail() { echo "FAIL: validate-five-step-progress-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md" ]] || fail "missing blueprint"
[[ -f "$ROOT/prompts/FIVE_STEP_SESSION_PROMPT_LOCKED_v1.md" ]] || fail "missing prompt"
[[ -f "$ROOT/scripts/five_step_progress_machine_v1.py" ]] || fail "missing script"
grep -q "FIVE_STEP_APEX" "$SINA_AUTHORITY_INDEX" || fail "authority row"
grep -q "FIVE_STEP" "$ROOT/scripts/hub_essentials_index.py" || fail "READ_CHAIN"
grep -q "SCAN" "$ROOT/SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md" || fail "blueprint incomplete"

python3 "$ROOT/scripts/five_step_progress_machine_v1.py" scan --json >/dev/null
python3 "$ROOT/scripts/five_step_progress_machine_v1.py" say-template >/dev/null

echo "OK: validate-five-step-progress-v1"
