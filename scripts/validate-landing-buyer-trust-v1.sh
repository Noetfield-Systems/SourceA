#!/usr/bin/env bash
# validate-landing-buyer-trust-v1.sh — Buyer 1 trust strip wiring + honest signals JSON
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

LANDING="$ROOT/SourceA-landing/green-unified"
DATA="$LANDING/data/trust-signals.json"
DEPLOY="$HOME/Desktop/agentrun-app/sourcea"

python3 "$ROOT/scripts/inject_landing_buyer_trust_v1.py" --dry-run >/dev/null 2>&1 || true
test -f "$DATA" || { echo "FAIL: missing $DATA — run inject_landing_buyer_trust_v1.py"; exit 1; }

python3 - <<PY
import json
import sys
from pathlib import Path

root = Path("$ROOT")
data_path = root / "SourceA-landing" / "green-unified" / "data" / "trust-signals.json"
row = json.loads(data_path.read_text(encoding="utf-8"))
assert row.get("schema") == "sourcea-trust-signals-v1", row.get("schema")
assert "receipts_signed_today" in row
assert row.get("receipt_metric_label"), "missing receipt_metric_label"
assert row.get("valid_yes") is not None, "valid_yes missing — wire factory_now_line"
ids = {b.get("id") for b in row.get("built_on") or []}
assert "stripe" not in ids, "Stripe must not appear in built_on"
assert "cursor" in ids and "cloudflare" in ids, "built_on missing cursor/cloudflare"
if row.get("receipts_signed_today", 0) > 100:
    raise SystemExit("FAIL: receipts_signed_today inflated (>100 material events) — filter broken")
print(f"OK: trust-signals · valid_yes={row.get('valid_yes')} · events_today={row.get('receipts_signed_today')}")
PY

for f in sourcea-trust-bar.js; do
  test -f "$LANDING/$f" || { echo "FAIL: missing $LANDING/$f"; exit 1; }
done

for page in index.html platform.html proof.html security.html status.html; do
  html="$LANDING/$page"
  test -f "$html" || { echo "FAIL: missing $html"; exit 1; }
  grep -q 'data-sa-trust-bar' "$html" || { echo "FAIL: no trust bar in $page"; exit 1; }
  grep -q 'sourcea-trust-bar.js' "$html" || { echo "FAIL: no trust-bar.js in $page"; exit 1; }
  grep -qi 'stripe' "$html" && { echo "FAIL: Stripe still in $page"; exit 1; }
  echo "PASS: trust strip wired · $page"
done

test -f "$LANDING/attach/proof-bundle-sample.html" || { echo "FAIL: missing proof sample"; exit 1; }
grep -q 'window.print' "$LANDING/attach/proof-bundle-sample.html" || { echo "FAIL: proof sample missing print"; exit 1; }

if [[ -d "$DEPLOY" ]]; then
  test -f "$DEPLOY/data/trust-signals.json" || { echo "FAIL: deploy missing trust-signals.json"; exit 1; }
  echo "PASS: deployed trust-signals.json"
fi

echo "validate-landing-buyer-trust-v1.sh: ALL PASS"
