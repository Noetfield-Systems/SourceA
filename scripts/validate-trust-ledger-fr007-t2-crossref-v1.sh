#!/usr/bin/env bash
# validate-trust-ledger-fr007-t2-crossref-v1.sh — sa-0553 ACT T2 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0553-trust-ledger-fr007-t2-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0503-trust-ledger-fr007_LOCKED_v1.md"
schema_law = root / "TRUST_LEDGER_SCHEMA_LOCKED_v1.md"
receipt = root / "receipts/sa-0503-receipt.json"

assert cross.is_file(), "missing sa-0553 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in ("sa-0503", "sa-0528", "sa-0553", "sa-0503-trust-ledger-fr007_LOCKED_v1.md", "TRUST_LEDGER_SCHEMA_LOCKED_v1.md"):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0503 attachment missing"
assert schema_law.is_file(), "TRUST_LEDGER_SCHEMA_LOCKED_v1.md missing"
assert receipt.is_file(), "canonical sa-0503 receipt missing"
for marker in ("sync_shipped_from_disk", "founder_request_tracker"):
    assert marker not in text, f"T2 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("trust_ledger_fr007_t2_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.trust_ledger_fr007_t2_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0503":
    raise SystemExit("FAIL: canonical_sa must be sa-0503")
if hook.get("t1_echo_sa") != "sa-0528":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0528")
if "sa-0553-trust-ledger-fr007-t2-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0553 attachment")

print("OK: validate-trust-ledger-fr007-t2-crossref-v1 · canonical=sa-0503 · t1=sa-0528 · sa-0553")
PY

bash validate-trust-ledger-fr007-v1.sh
bash validate-founder-request-fleet-sync-v1.sh
