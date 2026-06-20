#!/usr/bin/env bash
# validate-founder-request-build-sync-t1-crossref-v1.sh — sa-0532 ACT T1 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0532-founder-request-build-sync-t1-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0507-founder-request-build-sync_LOCKED_v1.md"
tracking_law = root / "brain-os/law/enforcement/FOUNDER_FIRST_ASSISTANT_TRACKING_LAW_LOCKED_v1.md"
receipt = root / "receipts/sa-0507-receipt.json"

assert cross.is_file(), "missing sa-0532 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in ("sa-0507", "sa-0532", "sa-0507-founder-request-build-sync_LOCKED_v1.md", "FOUNDER_FIRST_ASSISTANT_TRACKING_LAW_LOCKED_v1.md"):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0507 attachment missing"
assert tracking_law.is_file(), "FOUNDER_FIRST_ASSISTANT_TRACKING_LAW_LOCKED_v1.md missing"
assert receipt.is_file(), "canonical sa-0507 receipt missing"
for marker in ("sync_shipped_from_disk", "build-sina-command-panel.py"):
    assert marker not in text, f"T1 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("founder_request_build_sync_t1_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.founder_request_build_sync_t1_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0507":
    raise SystemExit("FAIL: canonical_sa must be sa-0507")
if "sa-0532-founder-request-build-sync-t1-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0532 attachment")

print("OK: validate-founder-request-build-sync-t1-crossref-v1 · canonical=sa-0507 · sa-0532")
PY

bash validate-founder-request-build-sync-v1.sh
