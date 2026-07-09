#!/usr/bin/env bash
# resolve_sourcea_root_v1.sh — SSOT for Mac Health / launchers (Noetfield path wins over stale Desktop/SourceA).
set -euo pipefail

resolve_sourcea_root() {
  local candidate=""
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [[ -n "${SINA_SOURCEA:-}" && -f "${SINA_SOURCEA}/scripts/mac-health-guard-server.py" ]]; then
    printf '%s' "${SINA_SOURCEA}"
    return 0
  fi
  for candidate in \
    "$(cd "${script_dir}/.." && pwd)" \
    "${HOME}/Desktop/Noetfield-Systems/SourceA" \
    "${HOME}/Desktop/SourceA"; do
    if [[ -f "${candidate}/scripts/mac-health-guard-server.py" ]]; then
      printf '%s' "${candidate}"
      return 0
    fi
  done
  return 1
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  resolve_sourcea_root || {
    echo "FAIL: cannot resolve SourceA root (missing mac-health-guard-server.py)" >&2
    exit 1
  }
  echo
fi
