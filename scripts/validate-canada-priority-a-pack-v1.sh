#!/usr/bin/env bash
# validate-canada-priority-a-pack-v1.sh — Canada Priority A lock + routing + brand patches
set -euo pipefail
cd "$(dirname "$0")/.."

fail() { echo "FAIL: validate-canada-priority-a-pack-v1 — $*" >&2; exit 1; }

[[ -f data/commercial/canada-priority-a-emails-v1.json ]] || fail "missing canada-priority-a-emails-v1.json"
[[ -f data/commercial/canada-brand-routing-v1.json ]] || fail "missing canada-brand-routing-v1.json"
[[ -f data/commercial/canada-portfolio-lock-manifest-v1.json ]] || fail "missing lock manifest — run lock_canada_portfolio_pack_v1.py"

python3 - <<'PY' || fail "email pack schema"
import json
from pathlib import Path
p = Path("data/commercial/canada-priority-a-emails-v1.json")
d = json.loads(p.read_text())
assert d.get("email_count") == 12, d.get("email_count")
lanes = {a["lane"] for a in d["accounts"]}
assert "TrustField" in lanes and "Noetfield" in lanes
nf = [a for a in d["accounts"] if a["lane"] == "Noetfield"]
assert any(a["company"] == "Fundmore.ai" for a in nf)
assert all("stop" in (a.get("body_full") or a.get("body") or "").lower() for a in d["accounts"])
print("OK: 12 emails · lanes · CASL stop")
PY

PAGER="$HOME/Desktop/1 PAGER"
[[ -f "$PAGER/CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md" ]] || fail "missing LOCKED email pack in 1 PAGER"
[[ -f "$PAGER/PORTFOLIO_SOURCEA_WITNESSBC_777_INSIGHT_PLAN_LOCKED_v1.md" ]] || fail "missing portfolio insight LOCKED"

TF="$HOME/Desktop/TrustField Technologies/templates/compliance.html"
[[ -f "$TF" ]] || fail "TrustField compliance template missing"
grep -q "Canada tokenization" "$TF" || fail "TrustField Canada block not implemented"

NF_BP="$HOME/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/bank-pilot/index.html"
NF_CP="$HOME/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/copilot/index.html"
for f in "$NF_BP" "$NF_CP"; do
  [[ -f "$f" ]] || fail "missing $f"
  grep -q "nf-section-block--canada\|canada-mortgage" "$f" || fail "Noetfield Canada block missing in $f"
done

echo "PASS: validate-canada-priority-a-pack-v1"
