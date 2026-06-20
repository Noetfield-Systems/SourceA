#!/usr/bin/env bash
# validate-complex-situation-fork-v1.sh — Fork Machine law + wiring on disk
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=governance-paths-v1.sh
. "$ROOT/scripts/governance-paths-v1.sh"
SCRIPTS="$ROOT/scripts"

fail() { echo "FAIL: validate-complex-situation-fork-v1 — $*" >&2; exit 1; }

LAW="$ROOT/SOURCEA_COMPLEX_SITUATION_FORK_MACHINE_LOCKED_v1.md"
PROMPT="$ROOT/prompts/COMPLEX_SITUATION_FORK_SESSION_PROMPT_LOCKED_v1.md"
PY="$SCRIPTS/complex_situation_fork_machine_v1.py"

[[ -f "$LAW" ]] || fail "missing law"
[[ -f "$PROMPT" ]] || fail "missing session prompt"
[[ -f "$PY" ]] || fail "missing python module"

grep -q "FORK-MACHINE SESSION" "$PROMPT" || fail "prompt missing FORK-MACHINE block"
grep -q "FORK_MACHINE" "$SINA_AUTHORITY_INDEX" || fail "authority row FORK_MACHINE"
grep -q "COMPLEX_SITUATION_FORK" "$ROOT/scripts/hub_essentials_index.py" || fail "READ_CHAIN missing"
grep -q "COMPLEX_SITUATION_FORK" "$ROOT/scripts/important_docs_index.py" || fail "doc library missing"
[[ -f "$ROOT/.cursor/rules/complex-situation-fork.mdc" ]] || fail "cursor rule missing"
grep -q "Fork Machine" "$ROOT/.cursor/rules/complex-situation-fork.mdc" || fail "cursor rule not wired"

python3 "$PY" assess --role brain --json >/dev/null
python3 "$PY" template >/dev/null

echo "OK: validate-complex-situation-fork-v1"
