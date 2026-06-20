#!/usr/bin/env bash
# WitnessBC E2E — cwd-safe wrapper (cloud CI / ship window only — not Mac founder session)
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
exec bash "$ROOT/witnessbc-site/scripts/wbc-e2e.sh" "$@"
