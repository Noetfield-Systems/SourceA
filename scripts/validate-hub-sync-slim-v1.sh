#!/usr/bin/env bash
# Track 2 L3 — hub-sync must stay slim with generation_id.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

curl -sf "http://127.0.0.1:13020/health" >/dev/null || {
  echo "FAIL: hub not up"
  exit 1
}

python3 - <<'PY'
import json
import sys
import urllib.request

with urllib.request.urlopen("http://127.0.0.1:13020/api/hub-sync", timeout=10) as r:
    body = r.read()
    data = json.loads(body.decode("utf-8"))

size = len(body)
if size > 512000:
    print(f"FAIL: hub-sync too large ({size} bytes)", file=sys.stderr)
    sys.exit(1)
if "generation_id" not in data:
    print("FAIL: generation_id missing from hub-sync", file=sys.stderr)
    sys.exit(1)
if data.get("data"):
    print("FAIL: hub-sync still returns legacy data wrapper", file=sys.stderr)
    sys.exit(1)
print(f"OK: hub-sync slim ({size} bytes) generation_id={data.get('generation_id')}")
PY

echo "OK: validate-hub-sync-slim-v1"
