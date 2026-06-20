#!/usr/bin/env bash
# validate-commercial-attests-priority-t2-crossref-v1.sh — sa-0571 ACT T2 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0571-commercial-attests-priority-t2-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0521-commercial-attests-priority-founder_LOCKED_v1.md"
priority = root / "brain-os/plan-registry/SOURCEA-PRIORITY.md"
receipt = root / "receipts/sa-0521-receipt.json"

assert cross.is_file(), "missing sa-0571 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0521",
    "sa-0546",
    "sa-0571",
    "sa-0521-commercial-attests-priority-founder_LOCKED_v1.md",
    "SOURCEA-PRIORITY.md",
    "validate-commercial-attests-priority-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0521 attachment missing"
assert priority.is_file(), "SOURCEA-PRIORITY.md missing"
assert receipt.is_file(), "canonical sa-0521 receipt missing"
for marker in ("build-sina-command-panel.py", "hub_self_refresh"):
    assert marker not in text, f"T2 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("commercial_attests_checklist_t2_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.commercial_attests_checklist_t2_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0521":
    raise SystemExit("FAIL: canonical_sa must be sa-0521")
if hook.get("t1_echo_sa") != "sa-0546":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0546")
if "sa-0571-commercial-attests-priority-t2-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0571 attachment")

print("OK: validate-commercial-attests-priority-t2-crossref-v1 · canonical=sa-0521 · t1=sa-0546 · sa-0571")
PY

bash validate-commercial-attests-priority-v1.sh
