#!/usr/bin/env bash
# validate-w1-film-receipt-v1.sh — W1 demo film receipt + proof page embed
set -euo pipefail
cd "$(dirname "$0")/.."

RECEIPT="${HOME}/.sina/enforcement/w1-film-receipt-v1.json"
PROOF="SourceA-landing/green-unified/proof.html"
ASSET="SourceA-landing/green-unified/assets/w1-demo.mp4"

fail() { echo "FAIL: validate-w1-film-receipt-v1 — $*" >&2; exit 1; }

[[ -f "$RECEIPT" ]] || fail "missing receipt $RECEIPT"
[[ -f "$PROOF" ]] || fail "missing $PROOF"
grep -q 'id="w1-demo-film"' "$PROOF" || fail "proof.html missing #w1-demo-film"

python3 - <<'PY' || fail "receipt contract"
import json
from pathlib import Path

rec = json.loads(Path.home().joinpath(".sina/enforcement/w1-film-receipt-v1.json").read_text())
assert rec.get("schema") == "w1-film-receipt-v1"
required = {"ALLOW", "BLOCK", "tamper-FAIL"}
got = set(rec.get("beats") or [])
assert required <= got, f"beats missing required {required - got}"
status = rec.get("status")
assert status in ("embed_live", "filmed", "interactive_fallback")
if status == "filmed":
    assert rec.get("embed_url") or rec.get("published"), "filmed status requires embed_url or published paths"
print("OK: W1 receipt · status", status, "· beats", rec.get("beats"))
PY

if [[ -f "$ASSET" ]]; then
  echo "OK: W1 asset present · $ASSET"
elif grep -q 'sa-demo-film-video' "$PROOF"; then
  echo "OK: W1 proof embed markup present (asset optional)"
else
  grep -q 'sa-demo-film-poster' "$PROOF" || fail "missing film poster fallback"
  echo "OK: W1 interactive fallback on proof.html"
fi

echo "OK: validate-w1-film-receipt-v1"
