#!/usr/bin/env bash
# Shared macOS codesign for SourceA .app bundles — Developer ID + Hardened Runtime when available.
# Apple refs:
#   https://developer.apple.com/help/account/certificates/create-developer-id-certificates
#   https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution
set -euo pipefail

resolve_codesign_identity() {
  if [[ -n "${SINA_CODESIGN_IDENTITY:-}" ]]; then
    echo "$SINA_CODESIGN_IDENTITY"
    return 0
  fi
  security find-identity -v -p codesigning 2>/dev/null \
    | awk -F'"' '/Developer ID Application/ { print $2; exit }'
}

sign_sina_app_bundle() {
  local app="$1"
  local ent="${2:-}"
  local exec_name="${3:-}"

  if [[ ! -d "$app" ]]; then
    echo "FAIL: not a bundle: $app" >&2
    return 1
  fi

  xattr -cr "$app" 2>/dev/null || true

  local identity
  identity="$(resolve_codesign_identity)"
  local sign_mode="adhoc"
  local -a sign_base=(--force)
  if [[ -n "$identity" ]]; then
    sign_mode="developer_id"
    sign_base+=(--sign "$identity" --options runtime --timestamp)
  else
    sign_base+=(--sign - --timestamp=none)
  fi

  local -a ent_args=()
  if [[ -n "$ent" && -f "$ent" ]]; then
    ent_args=(--entitlements "$ent")
  fi

  # Inside-out: every Mach-O executable in the bundle (Apple notarization requirement).
  while IFS= read -r -d '' bin; do
    codesign "${sign_base[@]}" "${ent_args[@]}" "$bin" 2>/dev/null || true
  done < <(find "$app/Contents" -type f -perm +111 -print0 2>/dev/null)

  local inner=""
  if [[ -n "$exec_name" ]]; then
    inner="$app/Contents/MacOS/$exec_name"
  else
    inner="$(find "$app/Contents/MacOS" -maxdepth 1 -type f -perm +111 2>/dev/null | head -1)"
  fi
  if [[ -n "$inner" && -f "$inner" ]]; then
    codesign "${sign_base[@]}" "${ent_args[@]}" "$inner"
  fi
  codesign "${sign_base[@]}" "${ent_args[@]}" --deep "$app"

  local receipt
  receipt="$HOME/.sina/sina-codesign-receipt-v1.json"
  python3 - <<PY
import json
from datetime import datetime, timezone
from pathlib import Path
row = {
    "schema": "sina-codesign-receipt-v1",
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "app": "$app",
    "sign_mode": "$sign_mode",
    "identity": "${identity:-adhoc}",
    "hardened_runtime": "$sign_mode" == "developer_id",
}
Path("$receipt").write_text(json.dumps(row, indent=2) + "\\n")
print(json.dumps(row))
PY

  if [[ "$sign_mode" == "adhoc" ]]; then
    echo "WARN: ad-hoc signed — Gatekeeper blocks web downloads. Need Developer ID + notarization." >&2
    echo "  Apple: https://developer.apple.com/account/resources/certificates/list" >&2
    return 2
  fi
  return 0
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  [[ $# -ge 1 ]] || { echo "usage: $0 <App.app> [entitlements.plist] [ExecutableName]" >&2; exit 1; }
  sign_sina_app_bundle "$1" "${2:-}" "${3:-}"
fi
