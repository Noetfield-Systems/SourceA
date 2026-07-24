#!/usr/bin/env bash
# Founder session gate entry — source from heavy validators (M111 wave 1).
_founder_session_gate_or_exit() {
  local script_name="${1:-$(basename "${BASH_SOURCE[1]:-$0}")}"
  local root="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
  if ! python3 "${root}/scripts/founder_session_gate_v1.py" "${script_name}" >/dev/null 2>&1; then
    python3 "${root}/scripts/founder_session_gate_v1.py" "${script_name}" >&2
    exit 2
  fi
}
