#!/usr/bin/env bash
# Sync canonical FBE cloud entrypoint scripts/fbe → cloud/ when cross-lane guard allows.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/scripts/fbe/fbe_cloud_entrypoint_v1.sh"
DST="$ROOT/cloud/fbe-worker-entrypoint.sh"

if [[ ! -f "$SRC" ]]; then
  echo "FAIL: missing canonical $SRC"
  exit 1
fi

guard="$(python3 "$ROOT/scripts/pre_write_guard_v1.py" check --agent cursor --path "$DST" --json 2>/dev/null || true)"
allowed="$(echo "$guard" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ok', False))" 2>/dev/null || echo False)"
if [[ "$allowed" != "True" ]]; then
  echo "SKIP: cloud/fbe-worker-entrypoint.sh blocked by cross-lane guard"
  echo "  Canonical SSOT: scripts/fbe/fbe_cloud_entrypoint_v1.sh (Railway deploy uses this)"
  echo "  Founder: EDIT ALLOWED: cloud/fbe-worker-entrypoint.sh + ACTION: sync from scripts/fbe"
  diff -q "$SRC" "$DST" 2>/dev/null && echo "  (files already match)" || echo "  (cloud copy differs from canonical)"
  exit 0
fi

install -m 755 "$SRC" "$DST"
if diff -q "$SRC" "$DST" >/dev/null; then
  echo "PASS: synced cloud/fbe-worker-entrypoint.sh from scripts/fbe/fbe_cloud_entrypoint_v1.sh"
else
  echo "FAIL: sync mismatch after install"
  exit 1
fi
