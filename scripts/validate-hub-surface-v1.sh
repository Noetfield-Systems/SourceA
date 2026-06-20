#!/usr/bin/env bash
# validate-hub-surface-v1.sh — U3 surface route live + slim contract
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-hub-surface-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/scripts/hub_surface_v1.py" ]] || fail "missing hub_surface_v1.py"
grep -q '"/api/surface/v1"' "$ROOT/scripts/sina-command-server.py" || fail "server route not wired"

if ! curl -sf "http://127.0.0.1:13020/health" >/dev/null 2>&1; then
  bash "$ROOT/scripts/serve-sina-command.sh" >/dev/null 2>&1 || true
  sleep 2
fi
curl -sf "http://127.0.0.1:13020/health" >/dev/null || fail "hub :13020 not up"

python3 - <<'PY'
import json
import sys
import urllib.request

url = "http://127.0.0.1:13020/api/surface/v1"
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        body = r.read()
        code = r.status
except Exception as exc:
    print(f"FAIL: GET {url} — {exc}", file=sys.stderr)
    sys.exit(1)

if code != 200:
    print(f"FAIL: GET {url} HTTP {code}", file=sys.stderr)
    sys.exit(1)

size = len(body)
if size > 65536:
    print(f"FAIL: surface payload too large ({size} bytes)", file=sys.stderr)
    sys.exit(1)

data = json.loads(body.decode("utf-8"))
for key in ("ok", "generation_id", "freeze_status", "queue_sa_id", "nav", "built_at", "founder_form_pending"):
    if key not in data:
        print(f"FAIL: missing field {key}", file=sys.stderr)
        sys.exit(1)
if not data.get("ok"):
    print("FAIL: ok=false", file=sys.stderr)
    sys.exit(1)
print(
    f"OK: surface/v1 ({size} bytes) gid={data.get('generation_id')} "
    f"freeze={data.get('freeze_status')} queue={data.get('queue_sa_id')}"
)
PY

echo "OK: validate-hub-surface-v1"
