#!/usr/bin/env bash
# validate-product-factory-roadmap-hub-signals-t1-crossref-v1.sh — sa-0542 ACT T1 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0542-product-factory-roadmap-hub-signals-t1-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0517-product-factory-roadmap-hub-signals_LOCKED_v1.md"
roadmap = root / "PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md"
receipt = root / "receipts/sa-0517-receipt.json"

assert cross.is_file(), "missing sa-0542 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0517",
    "sa-0542",
    "sa-0517-product-factory-roadmap-hub-signals_LOCKED_v1.md",
    "PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md",
    "validate-product-factory-roadmap-hub-signals-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0517 attachment missing"
assert roadmap.is_file(), "PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md missing"
assert receipt.is_file(), "canonical sa-0517 receipt missing"
for marker in ("build-sina-command-panel.py", "hub_self_refresh"):
    assert marker not in text, f"T1 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("product_factory_roadmap_hub_signals_t1_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.product_factory_roadmap_hub_signals_t1_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0517":
    raise SystemExit("FAIL: canonical_sa must be sa-0517")
if "sa-0542-product-factory-roadmap-hub-signals-t1-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0542 attachment")

print("OK: validate-product-factory-roadmap-hub-signals-t1-crossref-v1 · canonical=sa-0517 · sa-0542")
PY

bash validate-product-factory-roadmap-hub-signals-v1.sh
