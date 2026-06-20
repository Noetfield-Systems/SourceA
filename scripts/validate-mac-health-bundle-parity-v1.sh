#!/usr/bin/env bash
# validate-mac-health-bundle-parity-v1.sh — SSOT vs bundle parity (RF-MHG-001)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSOT="$ROOT/scripts/mac-health-standalone"
fail=0

hash_file() {
  python3 -c "
import hashlib,sys
from pathlib import Path
p=Path(sys.argv[1])
print(hashlib.sha256(p.read_bytes()).hexdigest()[:16])
" "$1"
}

check_bundle() {
  local label="$1" app_base="$2"
  local app_dir="$app_base/app"
  local scripts_dir="$app_base/scripts"
  if [[ ! -d "$app_dir" ]]; then
    echo "WARN: skip $label — no bundle at $app_dir"
    return 0
  fi
  for f in index.html app.js app.css; do
    if [[ ! -f "$app_dir/$f" ]]; then
      echo "FAIL: $label missing app/$f"
      fail=1
      continue
    fi
    sh=$(hash_file "$SSOT/$f")
    bh=$(hash_file "$app_dir/$f")
    if [[ "$sh" != "$bh" ]]; then
      echo "FAIL: $label app/$f hash mismatch (SSOT $sh vs bundle $bh) — run sync"
      fail=1
    else
      echo "PASS: $label app/$f parity"
    fi
  done
  if [[ ! -f "$scripts_dir/mac_health_settings_v1.py" ]]; then
    echo "FAIL: $label missing mac_health_settings_v1.py in scripts/"
    fail=1
  else
    echo "PASS: $label settings module present"
  fi
  if [[ ! -f "$scripts_dir/mac_health_version_v1.py" ]]; then
    echo "FAIL: $label missing mac_health_version_v1.py — run sync"
    fail=1
  else
    echo "PASS: $label version module present"
  fi
}

for base in \
  "$ROOT/brand/macos-apps/Mac Health Guard.app/Contents/Resources/mac-health-bundle" \
  "$HOME/Desktop/Mac Health Guard.app/Contents/Resources/mac-health-bundle" \
  "$HOME/Applications/Mac Health Guard.app/Contents/Resources/mac-health-bundle"; do
  check_bundle "$base" "$base"
done

if [[ "${1:-}" == "--build" ]]; then
  echo "=== cold-start build check ==="
  bash "$ROOT/scripts/build-mac-health-standalone-app-v1.sh" >/dev/null
  for _ in {1..40}; do
    curl -sf "http://127.0.0.1:${MAC_HEALTH_PORT:-13024}/health" >/dev/null 2>&1 && break
    sleep 0.25
  done
  curl -sf "http://127.0.0.1:${MAC_HEALTH_PORT:-13024}/health" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
assert str(d.get('version','')).startswith('3.3'), d
print('PASS: cold-start /health after build')
" || fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-health-bundle-parity-v1: PASS"
  exit 0
fi
echo "validate-mac-health-bundle-parity-v1: FAIL"
exit 1
