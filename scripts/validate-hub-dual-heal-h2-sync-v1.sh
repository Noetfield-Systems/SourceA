#!/usr/bin/env bash
# validate-hub-dual-heal-h2-sync-v1.sh — sa-0811 H2 registry sync after H1 light refresh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-hub-dual-heal-h2-sync-v1 — $*" >&2; exit 1; }

RECEIPT="${HOME}/.sina/two-hub-heal-receipt-v1.json"
[[ -f "$RECEIPT" ]] || fail "missing two-hub-heal-receipt-v1.json — run hub_dual_heal_v1.py"

python3 - <<'PY' || fail "receipt validation"
import json
import os
import urllib.request
from pathlib import Path

receipt = json.loads(Path(os.path.expanduser("~/.sina/two-hub-heal-receipt-v1.json")).read_text())
if receipt.get("schema") != "two-hub-heal-v1":
    raise SystemExit(f"bad schema: {receipt.get('schema')!r}")
if not receipt.get("ok"):
    raise SystemExit("receipt ok=false")
steps = {s["step"]: s for s in receipt.get("steps") or []}
for need in ("h2_registry_sync", "h2_payload_refresh"):
    if not steps.get(need, {}).get("ok"):
        raise SystemExit(f"missing or failed step: {need}")
if not steps.get("h1_worker_hub_heal"):
    raise SystemExit("h1_worker_hub_heal step missing")

h2 = receipt.get("h2_health") or {}
if h2.get("status") not in ("fresh", "aging", "unknown"):
    raise SystemExit(f"H2 health bad: {h2.get('status')}")

with urllib.request.urlopen("http://127.0.0.1:13020/api/machine-hub/v1", timeout=8) as r:
    live = json.loads(r.read().decode())
live_h = live.get("health") or {}
if live_h.get("status") not in ("fresh", "aging", "unknown"):
    raise SystemExit(f"live H2 health bad: {live_h.get('status')}")

print(
    f"OK: validate-hub-dual-heal-h2-sync-v1 · pending={live.get('pending_total')} "
    f"H2={live_h.get('status')} · receipt_at={receipt.get('at')}"
)
PY

echo "OK: validate-hub-dual-heal-h2-sync-v1 · sa-0811"
