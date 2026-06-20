#!/usr/bin/env bash
# Wire canonical Desktop deploy paths for SourceA landing recipe.
# Creates symlinks to ~/Desktop/YA5/* when canonical paths are missing.
set -euo pipefail

CANON_SA4="${HOME}/Desktop/SA4"
CANON_AGENTRUN="${HOME}/Desktop/agentrun-app"
YA5_SA4="${HOME}/Desktop/YA5/SA4"
YA5_AGENTRUN="${HOME}/Desktop/YA5/agentrun-app"

link_or_ok() {
  local canon="$1"
  local fallback="$2"
  local label="$3"
  if [[ -d "$canon" ]]; then
    echo "OK: $label present — $canon"
    return 0
  fi
  if [[ -L "$canon" ]]; then
    echo "OK: $label symlink — $canon → $(readlink "$canon")"
    return 0
  fi
  if [[ -e "$canon" ]]; then
    echo "FAIL: $label blocked — $canon exists but is not a directory"
    return 1
  fi
  if [[ ! -d "$fallback" ]]; then
    echo "FAIL: $label missing — need $canon or $fallback"
    return 1
  fi
  ln -s "$fallback" "$canon"
  echo "OK: linked $canon → $fallback"
}

fail=0
link_or_ok "$CANON_SA4" "$YA5_SA4" "SA4 (AgentGo :8080)" || fail=1
link_or_ok "$CANON_AGENTRUN" "$YA5_AGENTRUN" "agentrun-app (Agent Run :5180)" || fail=1

if [[ "$fail" -ne 0 ]]; then
  echo ""
  echo "Bootstrap failed. Expected one of:"
  echo "  $CANON_SA4"
  echo "  $CANON_AGENTRUN"
  echo "or YA5 copies:"
  echo "  $YA5_SA4"
  echo "  $YA5_AGENTRUN"
  exit 1
fi

echo "bootstrap-sourcea-desktop-deploy-v1: PASS"
