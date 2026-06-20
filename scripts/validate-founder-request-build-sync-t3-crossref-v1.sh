#!/usr/bin/env bash
# validate-founder-request-build-sync-t3-crossref-v1.sh — sa-0582 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0582-founder-request-build-sync-t3-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0507-founder-request-build-sync_LOCKED_v1.md"
receipt = root / "receipts/sa-0507-receipt.json"

assert cross.is_file(), "missing sa-0582 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0507",
    "sa-0532",
    "sa-0557",
    "sa-0582",
    "sa-0507-founder-request-build-sync_LOCKED_v1.md",
    "validate-founder-request-build-sync-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0507 attachment missing"
assert receipt.is_file(), "canonical sa-0507 receipt missing"
for marker in ("sync_shipped_from_disk", "build-sina-command-panel.py"):
    assert marker not in text, f"T3 cross-ref must not duplicate prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("founder_request_build_sync_t3_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "t2_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.founder_request_build_sync_t3_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0507":
    raise SystemExit("FAIL: canonical_sa must be sa-0507")
if hook.get("t1_echo_sa") != "sa-0532":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0532")
if hook.get("t2_echo_sa") != "sa-0557":
    raise SystemExit("FAIL: t2_echo_sa must be sa-0557")
if "sa-0582-founder-request-build-sync-t3-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0582 attachment")

print("OK: validate-founder-request-build-sync-t3-crossref-v1 · canonical=sa-0507 · t2=sa-0557 · sa-0582")
PY

bash validate-founder-request-build-sync-v1.sh
